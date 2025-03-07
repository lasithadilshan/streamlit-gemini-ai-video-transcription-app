import streamlit as st
import tempfile
import os
import ffmpeg
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from google.generativeai import GenerativeModel

# Configure Gemini 2.0 Flash

model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("🎥 Video Transcription with Generative AI")
st.write("Upload a video file to generate an accurate transcript.")

uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            video_path = temp_file.name
        
        st.success("Video uploaded successfully!")
        
        # Extract Audio
        audio_path = video_path.replace(".mp4", ".wav")
        ffmpeg.input(video_path).output(audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k').run(overwrite_output=True)
        st.info("Audio extracted successfully!")
        
        # Transcribe using Gemini
        with open(audio_path, "rb") as audio_file:
            transcript_response = model.generate_content(audio_file.read())
            transcript = transcript_response.text
        
        # Chunking Process
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(transcript)
        
        # Embedding and FAISS
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_texts(chunks, embeddings)
        
        # Display Transcript
        st.subheader("Generated Transcript")
        st.text_area("Transcript", transcript, height=300)
        
        # Download Option
        transcript_file = "transcript.txt"
        with open(transcript_file, "w") as f:
            f.write(transcript)
        st.download_button("Download Transcript", data=open(transcript_file, "rb"), file_name="transcript.txt", mime="text/plain")
        
        # Cleanup
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(transcript_file)
        
        st.success("Process completed successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")