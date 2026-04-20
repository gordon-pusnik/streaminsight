using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using Microsoft.Win32;
using System.Text;

namespace StreamInsightUI
{
    public partial class MainWindow : Window
    {
        private static readonly HttpClient client = new HttpClient { BaseAddress = new Uri("http://192.168.250.111:8002") };
        private string? selectedFilePath;

        public MainWindow()
        {
            InitializeComponent();
            _ = CheckHealthAsync();
        }

        private async void CheckHealth_Click(object sender, RoutedEventArgs e)
        {
            await CheckHealthAsync();
        }

        private async Task CheckHealthAsync()
        {
            try
            {
                HealthStatusText.Text = "Checking...";
                HealthStatusText.Foreground = Brushes.Gray;

                var response = await client.GetAsync("/health");
                if (response.IsSuccessStatusCode)
                {
                    var status = await response.Content.ReadFromJsonAsync<HealthStatus>();
                    HealthStatusText.Text = status?.Status ?? "Connected";
                    HealthStatusText.Foreground = Brushes.Green;
                }
                else
                {
                    HealthStatusText.Text = "API Error";
                    HealthStatusText.Foreground = Brushes.Red;
                }
            }
            catch (Exception)
            {
                HealthStatusText.Text = "Unreachable";
                HealthStatusText.Foreground = Brushes.Red;
            }
        }

        private void Browse_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "Video files (*.mp4;*.mov;*.avi)|*.mp4;*.mov;*.avi|All files (*.*)|*.*"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                selectedFilePath = openFileDialog.FileName;
                FilePathTextBox.Text = selectedFilePath;
                AnalyzeButton.IsEnabled = true;
                StatusTextBlock.Text = "File selected.";
            }
        }

        private async void Analyze_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedFilePath) || !File.Exists(selectedFilePath))
            {
                MessageBox.Show("Please select a valid video file first.", "Warning", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                // UI State
                AnalyzeButton.IsEnabled = false;
                AnalysisProgressBar.Visibility = Visibility.Visible;
                StatusTextBlock.Text = "Processing video...";
                ResultsTextBox.Text = string.Empty;
                FooterStatus.Text = "Uploading and analyzing...";

                using var content = new MultipartFormDataContent();
                using var fileStream = File.OpenRead(selectedFilePath);
                using var streamContent = new StreamContent(fileStream);
                
                streamContent.Headers.ContentType = new MediaTypeHeaderValue("video/mp4");
                content.Add(streamContent, "file", Path.GetFileName(selectedFilePath));

                // Determine which engine to use
                string engine = OpenAIRadioButton.IsChecked == true ? "openai" : "vertex";
                var response = await client.PostAsync($"/analyze?engine={engine}", content);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorMsg = await response.Content.ReadAsStringAsync();
                    MessageBox.Show($"Analysis failed: {errorMsg}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    StatusTextBlock.Text = "Analysis failed.";
                    return;
                }

                var result = await response.Content.ReadFromJsonAsync<AnalysisResponse>();
                
                if (result != null)
                {
                    DisplayResults(result);
                    StatusTextBlock.Text = "Analysis complete.";
                    FooterStatus.Text = "Ready";
                }
                else
                {
                    MessageBox.Show("Received empty response from server.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    StatusTextBlock.Text = "Error: Invalid response.";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                StatusTextBlock.Text = "Error occurred.";
            }
            finally
            {
                AnalyzeButton.IsEnabled = true;
                AnalysisProgressBar.Visibility = Visibility.Collapsed;
            }
        }

        private void DisplayResults(AnalysisResponse result)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("SUMMARY");
            sb.AppendLine("=======");
            sb.AppendLine(result.Summary);
            sb.AppendLine();

            sb.AppendLine("CHAPTERS");
            sb.AppendLine("========");
            foreach (var chapter in result.Chapters)
            {
                sb.AppendLine($"[{chapter.Start}] {chapter.Title}");
            }
            sb.AppendLine();

            sb.AppendLine("KEYWORDS");
            sb.AppendLine("========");
            sb.AppendLine(string.Join(", ", result.Keywords));
            sb.AppendLine();

            sb.AppendLine("LEARNING OBJECTIVES");
            sb.AppendLine("===================");
            foreach (var objective in result.LearningObjectives)
            {
                sb.AppendLine($"- {objective}");
            }

            ResultsTextBox.Text = sb.ToString();
        }
    }

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
