# streamlit-gemini-ai-video-transcription-app

This project is a Streamlit application that allows users to upload video files and generate accurate transcripts using Generative AI.

## Features

- Upload video files in various formats (mp4, avi, mov, mkv)
- Extract audio from the uploaded video
- Transcribe audio using Gemini 2.0 Flash
- Chunk the transcript for better processing
- Generate embeddings and store them using FAISS
- Display the generated transcript
- Download the transcript as a text file

## Requirements

- Python 3.7+
- Streamlit
- OpenAI
- Google Generative AI
- ffmpeg-python
- langchain
- faiss-cpu

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/streamlit-gemini-ai-video-transcription-app.git
    cd streamlit-gemini-ai-video-transcription-app
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure you have `ffmpeg` installed on your system. You can download it from [FFmpeg](https://ffmpeg.org/download.html).

## Usage

1. Set your Gemini API key in the `app.py` file:
    ```python
    configure(api_key="YOUR_GEMINI_API_KEY")
    ```

2. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

3. Open your web browser and go to `http://localhost:8501` to access the application.

4. Upload a video file and wait for the transcription process to complete. You can then view and download the generated transcript.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.