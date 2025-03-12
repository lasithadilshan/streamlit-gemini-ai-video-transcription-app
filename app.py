import streamlit as st
import yt_dlp
from google.generativeai import GenerativeModel

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            ._viewerBadge_nim44_23 {display: none;}  /* Hides "Hosted with Streamlit" */
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Configure Gemini 2.0 Flash
model = GenerativeModel("gemini-2.0-flash")

# Streamlit UI
st.title("📌 MeetingMind AI - Generate Meeting Minutes")
st.write("Enter a meeting video URL to extract summarized minutes per speaker.")

video_url = st.text_input("Enter Video URL")

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
            
            # Transcribe using Gemini
            transcript_response = model.generate_content(f"Transcribe the following audio: {audio_url}")
            full_transcript = transcript_response.text
            
            # Identify real names from context
            st.info("Identifying speakers...")
            name_prompt = f"""Analyze this meeting transcript and replace generic speaker labels (Speaker 1, Speaker 2, etc.) 
            with actual names mentioned in the conversation. Maintain the original format with 'Name: text'. 
            If names aren't mentioned, keep the original labels.\n\n{full_transcript}"""
            updated_response = model.generate_content(name_prompt)
            updated_transcript = updated_response.text
            
            # Split Transcript by Speaker
            transcript_lines = updated_transcript.split("\n")
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
