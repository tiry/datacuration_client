#!/usr/bin/env dotnet-script

using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Text.RegularExpressions;

// Configuration class to hold API settings and credentials
public class DataCurationConfig
{
    public string ClientId { get; set; } = Environment.GetEnvironmentVariable("DATA_CURATION_CLIENT_ID") ?? "";
    public string ClientSecret { get; set; } = Environment.GetEnvironmentVariable("DATA_CURATION_CLIENT_SECRET") ?? "";
    public string AuthEndpoint { get; set; } = Environment.GetEnvironmentVariable("DATA_CURATION_AUTH_ENDPOINT") ?? "https://auth.hyland.com/connect/token";
    public string ApiBaseUrl { get; set; } = Environment.GetEnvironmentVariable("DATA_CURATION_API_URL") ?? "https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation";
    
    public string PresignEndpoint => $"{ApiBaseUrl}/presign";
    public string StatusEndpoint => $"{ApiBaseUrl}/status";
    
    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(ClientId))
            throw new ArgumentException("DATA_CURATION_CLIENT_ID environment variable is required");
        if (string.IsNullOrWhiteSpace(ClientSecret))
            throw new ArgumentException("DATA_CURATION_CLIENT_SECRET environment variable is required");
    }
}

// Simple JSON parsing helpers for the API responses
public static class SimpleJsonParser
{
    public static string ExtractString(string json, string key)
    {
        var pattern = $"\"{key}\"\\s*:\\s*\"([^\"]+)\"";
        var match = Regex.Match(json, pattern);
        return match.Success ? match.Groups[1].Value : "";
    }
    
    public static int ExtractInt(string json, string key)
    {
        var pattern = $"\"{key}\"\\s*:\\s*(\\d+)";
        var match = Regex.Match(json, pattern);
        return match.Success ? int.Parse(match.Groups[1].Value) : 0;
    }
    
    public static string BuildBasicOptionsJson()
    {
        return @"{
            ""normalization"": {
                ""quotations"": true,
                ""dashes"": true
            },
            ""chunking"": false,
            ""embedding"": false,
            ""json_schema"": false
        }";
    }
}

// Main Data Curation API client
public class DataCurationClient
{
    private readonly HttpClient _httpClient;
    private readonly DataCurationConfig _config;
    private string _accessToken = "";

    public DataCurationClient()
    {
        _httpClient = new HttpClient();
        _config = new DataCurationConfig();
        _config.Validate();
    }

    // Authenticate and get access token
    public async Task<string> AuthenticateAsync()
    {
        Console.WriteLine($"Authenticating with endpoint: {_config.AuthEndpoint}");
        
        var requestData = new Dictionary<string, string>
        {
            {"grant_type", "client_credentials"},
            {"scope", "environment_authorization"},
            {"client_id", _config.ClientId},
            {"client_secret", _config.ClientSecret}
        };

        var formContent = new FormUrlEncodedContent(requestData);
        
        try
        {
            var response = await _httpClient.PostAsync(_config.AuthEndpoint, formContent);
            var responseContent = await response.Content.ReadAsStringAsync();
            
            Console.WriteLine($"Auth response status: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                throw new HttpRequestException($"Authentication failed: {response.StatusCode} - {responseContent}");
            }

            // Parse access token from JSON response
            _accessToken = SimpleJsonParser.ExtractString(responseContent, "access_token");
            if (string.IsNullOrEmpty(_accessToken))
            {
                throw new InvalidOperationException("Failed to parse access token from response");
            }

            Console.WriteLine("Authentication successful");
            return _accessToken;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Authentication error: {ex.Message}");
            throw;
        }
    }

    // Call presign endpoint to get upload and download URLs
    public async Task<(string jobId, string putUrl, string getUrl)> PresignAsync(string optionsJson = null)
    {
        if (string.IsNullOrEmpty(_accessToken))
        {
            await AuthenticateAsync();
        }

        Console.WriteLine($"Calling presign endpoint: {_config.PresignEndpoint}");
        
        var json = optionsJson ?? SimpleJsonParser.BuildBasicOptionsJson();
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_accessToken}");

        try
        {
            var response = await _httpClient.PostAsync(_config.PresignEndpoint, content);
            var responseContent = await response.Content.ReadAsStringAsync();
            
            Console.WriteLine($"Presign response status: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                throw new HttpRequestException($"Presign failed: {response.StatusCode} - {responseContent}");
            }

            // Parse the response JSON
            var jobId = SimpleJsonParser.ExtractString(responseContent, "job_id");
            var putUrl = SimpleJsonParser.ExtractString(responseContent, "put_url");
            var getUrl = SimpleJsonParser.ExtractString(responseContent, "get_url");

            if (string.IsNullOrEmpty(jobId) || string.IsNullOrEmpty(putUrl) || string.IsNullOrEmpty(getUrl))
            {
                throw new InvalidOperationException("Failed to parse presign response");
            }

            Console.WriteLine($"Presign successful, job_id: {jobId}");
            return (jobId, putUrl, getUrl);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Presign error: {ex.Message}");
            throw;
        }
    }

    // Upload file to the presigned URL
    public async Task UploadFileAsync(string filePath, string putUrl)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"File not found: {filePath}");
        }

        Console.WriteLine($"Uploading file: {filePath}");
        var fileInfo = new FileInfo(filePath);
        Console.WriteLine($"File size: {fileInfo.Length} bytes");

        try
        {
            var fileBytes = await File.ReadAllBytesAsync(filePath);
            var content = new ByteArrayContent(fileBytes);
            content.Headers.Add("Content-Type", "application/octet-stream");

            var response = await _httpClient.PutAsync(putUrl, content);
            
            Console.WriteLine($"Upload response status: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"File upload failed: {response.StatusCode} - {responseContent}");
            }

            Console.WriteLine("File upload successful");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Upload error: {ex.Message}");
            throw;
        }
    }

    // Check job status
    public async Task<string> CheckStatusAsync(string jobId)
    {
        if (string.IsNullOrEmpty(_accessToken))
        {
            await AuthenticateAsync();
        }

        var statusUrl = $"{_config.StatusEndpoint}/{jobId}";
        Console.WriteLine($"Checking job status: {statusUrl}");

        _httpClient.DefaultRequestHeaders.Clear();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_accessToken}");

        try
        {
            var response = await _httpClient.GetAsync(statusUrl);
            var responseContent = await response.Content.ReadAsStringAsync();
            
            Console.WriteLine($"Status check response: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                throw new HttpRequestException($"Status check failed: {response.StatusCode} - {responseContent}");
            }

            // Parse status from JSON response
            var status = SimpleJsonParser.ExtractString(responseContent, "status");
            if (string.IsNullOrEmpty(status))
            {
                throw new InvalidOperationException("Failed to parse status response");
            }

            Console.WriteLine($"Job status: {status}");
            return status;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Status check error: {ex.Message}");
            throw;
        }
    }

    // Get results from the presigned URL
    public async Task<string> GetResultsAsync(string getUrl)
    {
        Console.WriteLine($"Getting results from: {getUrl}");

        try
        {
            var response = await _httpClient.GetAsync(getUrl);
            
            Console.WriteLine($"Get results response status: {response.StatusCode}");
            
            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException($"Get results failed: {response.StatusCode} - {errorContent}");
            }

            var result = await response.Content.ReadAsStringAsync();
            Console.WriteLine($"Results retrieved, length: {result.Length} characters");
            return result;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Get results error: {ex.Message}");
            throw;
        }
    }

    // Process file end-to-end
    public async Task<string> ProcessFileAsync(string filePath, string optionsJson = null, int maxRetries = 10, int retryDelaySeconds = 2)
    {
        Console.WriteLine($"Processing file: {filePath}");
        
        // Get presigned URLs
        var (jobId, putUrl, getUrl) = await PresignAsync(optionsJson);
        
        // Upload file
        await UploadFileAsync(filePath, putUrl);
        
        // Wait for processing to complete
        for (int retry = 0; retry < maxRetries; retry++)
        {
            try
            {
                Console.WriteLine($"Checking job status (attempt {retry + 1}/{maxRetries})");
                var status = await CheckStatusAsync(jobId);
                
                if (status == "Done")
                {
                    Console.WriteLine("Job complete, retrieving results");
                    return await GetResultsAsync(getUrl);
                }
                
                Console.WriteLine($"Job still processing, waiting {retryDelaySeconds} seconds...");
                await Task.Delay(retryDelaySeconds * 1000);
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("404"))
            {
                // Resource not ready yet, wait and retry
                Console.WriteLine($"Resource not ready (404), waiting {retryDelaySeconds} seconds...");
                await Task.Delay(retryDelaySeconds * 1000);
            }
        }
        
        throw new TimeoutException($"Processing timed out after {maxRetries} retries");
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

// Main script execution
async Task Main(string[] args)
{
    if (args.Length == 0)
    {
        Console.WriteLine("Usage: dotnet script datacuration.csx <file_path> [output_file]");
        Console.WriteLine();
        Console.WriteLine("Environment variables required:");
        Console.WriteLine("  DATA_CURATION_CLIENT_ID - Your client ID");
        Console.WriteLine("  DATA_CURATION_CLIENT_SECRET - Your client secret");
        Console.WriteLine();
        Console.WriteLine("Optional environment variables:");
        Console.WriteLine("  DATA_CURATION_AUTH_ENDPOINT - Auth endpoint (default: https://auth.hyland.com/connect/token)");
        Console.WriteLine("  DATA_CURATION_API_URL - API base URL (default: https://knowledge-enrichment.ai.experience.hyland.com/latest/api/data-curation)");
        return;
    }

    var filePath = args[0];
    var outputFile = args.Length > 1 ? args[1] : null;

    try
    {
        using var client = new DataCurationClient();
        
        var result = await client.ProcessFileAsync(filePath);
        
        if (!string.IsNullOrEmpty(outputFile))
        {
            await File.WriteAllTextAsync(outputFile, result);
            Console.WriteLine($"Results saved to: {outputFile}");
        }
        else
        {
            Console.WriteLine("=== CURATED TEXT ===");
            Console.WriteLine(result);
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
        Environment.Exit(1);
    }
}

// Execute the main function
await Main(Args.ToArray());