# StreamInsight C# Clients

This folder contains two C# clients for the StreamInsight API:
1. **StreamInsightUI**: A Windows WPF Desktop Application (Recommended).
2. **StreamInsightClient**: A Console Application.

## Prerequisites

- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- Visual Studio 2022
- The StreamInsight API running at `http://localhost:9000`

## How to Run

### Using Visual Studio 2022 (Preferred)

1. Open `StreamInsight.sln` in Visual Studio 2022.
2. In the **Solution Explorer**, right-click on **StreamInsightUI** and select **Set as Startup Project**.
3. Press **F5** to build and run.
4. Use the "Browse" button to select a video and "Analyze Video" to process it.

### Using .NET CLI (Console Client)

1. Navigate to the console project directory:
   ```bash
   cd StreamInsightClient
   ```
2. Run the application:
   ```bash
   dotnet run -- <path_to_video_file>
   ```

## Functionality (WPF UI)

- **Real-time Health Check**: Automatically checks if the API is online and shows a Green/Red status.
- **File Browser**: native Windows file picker for video selection.
- **Progress Indicator**: Shows an indeterminate progress bar while the video is being processed.
- **Structured Results**: Displays the Summary, Chapters, Keywords, and Learning Objectives in a clean, scrollable text area.
