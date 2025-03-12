import streamlit as st
import os
import ffmpeg
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from google.generativeai import GenerativeModel
import yt_dlp

# Configure Gemini 2.0 Flash
model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("📌 MeetingMind AI - Generate Meeting Minutes")
st.write("Enter a meeting video URL to extract summarized minutes per speaker.")

video_url = st.text_input("Enter Video URL")

if video_url:
    try:
        # Download Video Audio
        st.info("Downloading video audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': 'meeting_audio.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        audio_path = "meeting_audio.wav"
        st.success("Audio downloaded successfully!")

        # Transcribe using Gemini
        with open(audio_path, "rb") as audio_file:
            transcript_response = model.generate_content(audio_file.read())
            full_transcript = transcript_response.text
        
        # Split Transcript by Speaker (Basic)
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
        
        # Cleanup
        os.remove(audio_path)
        os.remove(minutes_file)
        
        st.success("Meeting minutes generated successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
