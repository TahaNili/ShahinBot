import os
import tempfile
import whisper
from gtts import gTTS
import subprocess

def speech_to_text(audio_path, model_size="base"):
    """
    Convert speech (voice message) to text using Whisper.
    :param audio_path: Path to the audio file (ogg, mp3, wav, etc.)
    :param model_size: Whisper model size (tiny, base, small, medium, large)
    :return: Transcribed text
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="fa")
    return result["text"]

def text_to_speech(text, lang="fa"):
    """
    Convert text to speech using gTTS and return the path to the mp3 file.
    :param text: Text to convert
    :param lang: Language code (fa for Persian, en for English)
    :return: Path to the generated mp3 file
    """
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def ogg_to_wav(ogg_path):
    """
    Convert OGG audio file (Telegram voice) to WAV for Whisper.
    :param ogg_path: Path to OGG file
    :return: Path to WAV file
    """
    wav_path = ogg_path + ".wav"
    ffmpeg_path = r"D:\ffmpeg\ffmpeg-2025-06-11-git-f019dd69f0-essentials_build\bin\ffmpeg.exe"
    # Check if ffmpeg.exe exists
    if not os.path.isfile(ffmpeg_path):
        raise RuntimeError(f"ffmpeg.exe not found at: {ffmpeg_path}")
    # Check if ogg file exists
    if not os.path.isfile(ogg_path):
        raise RuntimeError(f"OGG file not found: {ogg_path}")
    command = [
        ffmpeg_path, "-y", "-i", ogg_path, wav_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except Exception as e:
        raise RuntimeError(f"ffmpeg error: {e}")
    if not os.path.isfile(wav_path):
        raise RuntimeError(f"WAV file was not created: {wav_path}")
    return wav_path
