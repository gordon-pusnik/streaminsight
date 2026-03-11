using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace StreamInsightClient
{
    internal class Program
    {
        private static readonly HttpClient client = new HttpClient { BaseAddress = new Uri("http://localhost:9000") };

        static async Task Main(string[] args)
        {
            Console.WriteLine("=== StreamInsight C# Client ===");

            // 1. Check Health
            await CheckHealthAsync();

            // 2. Upload and Analyze Video
            if (args.Length > 0)
            {
                string filePath = args[0];
                if (File.Exists(filePath))
                {
                    await AnalyzeVideoAsync(filePath);
                }
                else
                {
                    Console.WriteLine($"Error: File not found at {filePath}");
                }
            }
            else
            {
                Console.WriteLine("\nUsage: StreamInsightClient <video_file_path>");
                Console.WriteLine("Example: StreamInsightClient sample_video.mp4");
            }

            Console.WriteLine("\nPress any key to exit...");
            // Console.ReadKey(); // Usually useful in VS, but might hang in some CLI environments.
        }

        static async Task CheckHealthAsync()
        {
            try
            {
                Console.WriteLine("\nChecking API health...");
                var response = await client.GetAsync("/health");
                response.EnsureSuccessStatusCode();
                var status = await response.Content.ReadFromJsonAsync<HealthStatus>();
                Console.WriteLine($"Health Status: {status?.Status ?? "Unknown"}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Health Check failed: {ex.Message}");
            }
        }

        static async Task AnalyzeVideoAsync(string filePath)
        {
            try
            {
                Console.WriteLine($"\nUploading and analyzing video: {Path.GetFileName(filePath)}");
                Console.WriteLine("This may take a moment depending on the video size and processing time...");

                using var content = new MultipartFormDataContent();
                using var fileStream = File.OpenRead(filePath);
                using var streamContent = new StreamContent(fileStream);
                
                // Set the correct media type for the file part.
                streamContent.Headers.ContentType = new MediaTypeHeaderValue("video/mp4");
                
                content.Add(streamContent, "file", Path.GetFileName(filePath));

                // Optional: add engine query param if needed (e.g. /analyze?engine=openai)
                var response = await client.PostAsync("/analyze", content);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorMsg = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Analysis failed (Status {response.StatusCode}): {errorMsg}");
                    return;
                }

                var result = await response.Content.ReadFromJsonAsync<AnalysisResponse>();
                
                if (result != null)
                {
                    DisplayResults(result);
                }
                else
                {
                    Console.WriteLine("Error: Received empty or invalid response from server.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred during analysis: {ex.Message}");
            }
        }

        static void DisplayResults(AnalysisResponse result)
        {
            Console.WriteLine("\n--- Analysis Results ---");
            Console.WriteLine($"\nSummary:\n{result.Summary}");

            Console.WriteLine("\nChapters:");
            foreach (var chapter in result.Chapters)
            {
                Console.WriteLine($"- [{chapter.Start}] {chapter.Title}");
            }

            Console.WriteLine("\nKeywords:");
            Console.WriteLine(string.Join(", ", result.Keywords));

            Console.WriteLine("\nLearning Objectives:");
            foreach (var objective in result.LearningObjectives)
            {
                Console.WriteLine($"- {objective}");
            }
        }
    }

    // Models matching the Python API
    public class HealthStatus
    {
        [JsonPropertyName("status")]
        public string? Status { get; set; }
    }

    public class Chapter
    {
        [JsonPropertyName("start")]
        public string? Start { get; set; }
        [JsonPropertyName("title")]
        public string? Title { get; set; }
    }

    public class AnalysisResponse
    {
        [JsonPropertyName("summary")]
        public string Summary { get; set; } = string.Empty;
        [JsonPropertyName("chapters")]
        public List<Chapter> Chapters { get; set; } = new List<Chapter>();
        [JsonPropertyName("keywords")]
        public List<string> Keywords { get; set; } = new List<string>();
        [JsonPropertyName("learning_objectives")]
        public List<string> LearningObjectives { get; set; } = new List<string>();
    }
}
