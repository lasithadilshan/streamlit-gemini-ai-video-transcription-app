import streamlit as st
import tempfile
import os
import ffmpeg
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from google.generativeai import GenerativeModel

# Configure Gemini 2.0 Flash
model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("📌 MeetingMind AI - Generate Meeting Minutes")
st.write("Upload a meeting recording to extract summarized minutes per speaker.")

uploaded_file = st.file_uploader("Upload Meeting Recording", type=["mp4", "avi", "mov", "mkv", "wav", "mp3"])

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            video_path = temp_file.name
        
        st.success("File uploaded successfully!")

        # Extract Audio (if video file)
        audio_path = video_path.replace(".mp4", ".wav")
        ffmpeg.input(video_path).output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k').run(overwrite_output=True)
        st.info("Audio extracted successfully!")

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
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(minutes_file)
        
        st.success("Meeting minutes generated successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
