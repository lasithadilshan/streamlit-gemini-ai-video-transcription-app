import streamlit as st
import yt_dlp
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from google.generativeai import GenerativeModel
import subprocess
import io

# Configure Gemini 2.0 Flash
model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("📌 MeetingMind AI - Generate Meeting Minutes")
st.write("Enter a meeting video URL to extract summarized minutes per speaker.")

video_url = st.text_input("Enter Video URL")

if video_url:
    try:
        # Extract Audio without Downloading
        st.info("Extracting audio stream...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': '-',  # Pipe output instead of saving
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            process = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', 'pipe:1'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            audio_stream, _ = process.communicate(ydl.extract_info(video_url, download=False)['url'].encode())
        
        st.success("Audio extracted successfully!")
        
        # Transcribe using Gemini
        transcript_response = model.generate_content(audio_stream)
        full_transcript = transcript_response.text
        
        # Split Transcript by Speaker
        transcript_lines = full_transcript.split("\n")
        speaker_transcripts = {}
        
        for line in transcript_lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                speaker = speaker.strip()
                text = text.strip()
                if speaker not in speaker_transcripts:
                    speaker_transcripts[speaker] = []
                speaker_transcripts[speaker].append(text)
        
        # Summarize Meeting Minutes per Speaker
        meeting_minutes = {}
        for speaker, texts in speaker_transcripts.items():
            response = model.generate_content("Summarize these points in bullet format:\n" + "\n".join(texts))
            meeting_minutes[speaker] = response.text
        
        # Display Meeting Minutes
        st.subheader("📝 Meeting Minutes (Summarized)")
        for speaker, summary in meeting_minutes.items():
            st.markdown(f"**{speaker}**")
            st.markdown(summary)
        
        # Save Summary
        minutes_file = "meeting_minutes.txt"
        with open(minutes_file, "w") as f:
            for speaker, summary in meeting_minutes.items():
                f.write(f"{speaker}:\n{summary}\n\n")
        
        st.download_button("Download Meeting Minutes", data=open(minutes_file, "rb"), file_name="meeting_minutes.txt", mime="text/plain")
        
        st.success("Meeting minutes generated successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
