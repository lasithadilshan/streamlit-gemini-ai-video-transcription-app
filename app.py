import streamlit as st
import yt_dlp
import torch
import whisperx
from google.generativeai import GenerativeModel
from pydub import AudioSegment
import tempfile
import requests

# Configure Gemini 2.0 Flash
model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("📌 MeetingMind AI - Generate Meeting Minutes")
st.write("Enter a meeting video URL to extract summarized minutes per speaker.")

video_url = st.text_input("Enter Video URL")

def download_audio(audio_url):
    response = requests.get(audio_url, stream=True)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(temp_audio.name, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return temp_audio.name

if video_url:
    try:
        # Extract Direct Audio URL
        st.info("Fetching audio stream URL...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get('url', None)
        
        if not audio_url:
            st.error("Failed to retrieve audio stream.")
        else:
            st.success("Audio stream retrieved successfully!")
            
            # Download and Convert Audio
            st.info("Processing audio for transcription...")
            audio_path = download_audio(audio_url)
            
            # Load WhisperX model
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = whisperx.load_model("large-v2", device)
            diarization_model = whisperx.DiarizationPipeline(device=device)
            
            # Transcribe with Speaker Diarization
            audio = whisperx.load_audio(audio_path)
            result = model.transcribe(audio)
            diarization_result = diarization_model(audio, result["segments"])
            
            # Extract Speaker Labels
            transcript = []
            for segment in diarization_result:
                speaker = segment["speaker"]
                text = segment["text"]
                transcript.append(f"{speaker}: {text}")
            full_transcript = "\n".join(transcript)
            
            # Summarize using Gemini
            response = model.generate_content("Summarize the following meeting transcript into key points per speaker:\n" + full_transcript)
            meeting_minutes = response.text
            
            # Display Meeting Minutes
            st.subheader("📝 Meeting Minutes (Summarized)")
            st.markdown(meeting_minutes)
            
            # Save Summary
            minutes_file = "meeting_minutes.txt"
            with open(minutes_file, "w") as f:
                f.write(meeting_minutes)
            
            st.download_button("Download Meeting Minutes", data=open(minutes_file, "rb"), file_name="meeting_minutes.txt", mime="text/plain")
            
            st.success("Meeting minutes generated successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
