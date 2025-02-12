import os
import tempfile
import subprocess
from datetime import timedelta

import streamlit as st
import srt
import whisper
from deep_translator import GoogleTranslator
import google.generativeai as genai
from gtts import gTTS

# Configure Gemini AI (replace with your actual API key)
GENAI_API_KEY = "AIzaSyDVutwg8ECUUv3VzOj3bakCn3wxxMao4w8"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    """Load the Whisper model (cached for performance)."""
    return whisper.load_model("small")


def transcribe_and_save_srt(video_path, srt_filename="subtitles.srt"):
    """
    Transcribes video audio using Whisper and saves it as an SRT file.
    Returns the list of Subtitle objects.
    """
    whisper_model = load_whisper_model()
    result = whisper_model.transcribe(video_path, task="transcribe")

    subtitles = []
    for i, segment in enumerate(result["segments"]):
        start_time = timedelta(seconds=segment["start"])
        end_time = timedelta(seconds=segment["end"])
        text = segment["text"].strip()
        subtitles.append(srt.Subtitle(index=i + 1, start=start_time, end=end_time, content=text))

    with open(srt_filename, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))
    return subtitles


def translate_subtitles(subtitles, target_lang="es"):
    """Translates subtitles into the specified language."""
    translator = GoogleTranslator(source="auto", target=target_lang)
    translated_subs = []
    for sub in subtitles:
        translated_text = translator.translate(sub.content)
        translated_subs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=translated_text))
    return translated_subs


def save_translated_srt(subtitles, output_filename="translated_subtitles.srt"):
    """Saves the translated subtitles as an SRT file."""
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))
    return output_filename


def add_subtitles_to_video(video_file, subtitle_file, output_file):
    """Uses FFmpeg to burn subtitles into the video with automatic overwrite."""
    # The "-y" flag forces overwriting of the output file without prompting.
    command = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-vf", f"subtitles={subtitle_file}",
        "-c:a", "copy",
        output_file
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        st.error(f"Error burning subtitles into video: {e}")


def generate_summary(subtitles):
    """Generates a summary of the video with topic segmentation using Gemini AI."""
    transcript = "\n".join(
        [f"{str(sub.start)} - {str(sub.end)}: {sub.content}" for sub in subtitles]
    )

    prompt = f"""
Given the following transcribed text from a video, generate a summary with a breakdown of topics discussed along with their timestamps.

**Transcript:**
{transcript}

**Output Format:**
00:00 -- 1:00
Introduction
[Brief summary of what was discussed]

01:00 -- 2:00
Topic Name
[Brief summary]

Keep it concise and to the point.
"""
    response = gemini_model.generate_content(prompt)
    summary = response.text.strip() if hasattr(response, "text") else "No summary generated."

    with open("video_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    return summary


def generate_dubbed_audio(translated_subtitles, target_language, output_audio="dubbed_audio.mp3"):
    """Generates a dubbed audio track using gTTS from the translated subtitles."""
    # Concatenate all translated texts with pauses
    full_text = ". ".join([sub.content for sub in translated_subtitles])
    tts = gTTS(text=full_text, lang=target_language)
    tts.save(output_audio)
    return output_audio


def add_dubbed_audio_to_video(video_file, dubbed_audio, output_file="video_dubbed.mp4"):
    """Replaces the original audio of the video with the dubbed audio using FFmpeg."""
    command = [
        "ffmpeg",
        "-y",
        "-i", video_file,
        "-i", dubbed_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_file
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        st.error(f"Error dubbing video: {e}")


def process_video(tmp_video_path, target_language):
    """Runs all heavy processing tasks and returns the results."""
    # 1. Transcribe video and save subtitles
    subtitles = transcribe_and_save_srt(tmp_video_path, "subtitles.srt")

    # 2. Translate subtitles and save translated SRT
    translated_subs = translate_subtitles(subtitles, target_lang=target_language)
    translated_srt_path = save_translated_srt(translated_subs, "translated_subtitles.srt")

    # 3. Generate summary
    summary = generate_summary(subtitles)

    # 4. Burn translated subtitles into video
    output_video = "video_with_translated_subtitles.mp4"
    add_subtitles_to_video(tmp_video_path, "translated_subtitles.srt", output_video)

    # 5. Generate dubbed audio and produce dubbed video
    dubbed_audio = generate_dubbed_audio(translated_subs, target_language, "dubbed_audio.mp3")
    dubbed_video = "video_dubbed.mp4"
    add_dubbed_audio_to_video(tmp_video_path, dubbed_audio, dubbed_video)

    return {
        "subtitles": subtitles,
        "translated_srt": translated_srt_path,
        "summary": summary,
        "output_video": output_video,
        "dubbed_video": dubbed_video,
    }


def main():
    st.title("Video Transcription, Translation, Summary & Dubbing Generator")
    st.markdown(
        """
        Upload a video file and specify a target language code for translation/dubbing (e.g., `es` for Spanish, `fr` for French).  
        The app will automatically:
        - Transcribe the video using Whisper  
        - Translate the subtitles  
        - Generate a topic-segmented summary using Gemini AI  
        - Burn the translated subtitles into the video  
        - Generate a dubbed audio track and produce a dubbed version of the video  
        
        Once processing is complete, click the buttons below to view or download your results.
        """
    )

    video_file = st.file_uploader("Upload your video file", type=["mp4", "mkv", "avi", "mov"])
    target_language = st.text_input("Enter target language code", value="es")

    if video_file is not None and target_language:
        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1]) as tmp_file:
            tmp_file.write(video_file.read())
            tmp_video_path = tmp_file.name

        # Run heavy processing once and store results in session state.
        if "results" not in st.session_state:
            with st.spinner("Processing video... Please wait."):
                st.session_state.results = process_video(tmp_video_path, target_language)
            os.remove(tmp_video_path)

        results = st.session_state.results

        st.header("Results")
        # Final outputs are revealed only when the corresponding button is clicked.

        if st.button("Show Translated Subtitles (SRT)"):
            with open(results["translated_srt"], "rb") as f:
                st.download_button("Download Translated SRT", data=f, file_name="translated_subtitles.srt")
            st.success("Translated subtitles are ready for download.")

        if st.button("Show Video Summary"):
            st.text_area("Summary", value=results["summary"], height=200)
            with open("video_summary.txt", "rb") as f:
                st.download_button("Download Summary", data=f, file_name="video_summary.txt")
            st.success("Video summary is ready for download.")

        if st.button("Show Subtitled Video"):
            if os.path.exists(results["output_video"]):
                st.video(results["output_video"])
                with open(results["output_video"], "rb") as vid_file:
                    st.download_button("Download Subtitled Video", data=vid_file, file_name=results["output_video"])
                st.success("Subtitled video is ready for download.")

        if st.button("Show Dubbed Video"):
            if os.path.exists(results["dubbed_video"]):
                st.video(results["dubbed_video"])
                with open(results["dubbed_video"], "rb") as vid_file:
                    st.download_button("Download Dubbed Video", data=vid_file, file_name=results["dubbed_video"])
                st.success("Dubbed video is ready for download.")
    else:
        st.info("Please upload a video file and specify a target language code.")


if __name__ == "__main__":
    main()
