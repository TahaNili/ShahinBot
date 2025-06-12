import os
import tempfile
import whisper
from gtts import gTTS
from pydub import AudioSegment

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
    sound = AudioSegment.from_file(ogg_path)
    wav_path = ogg_path + ".wav"
    sound.export(wav_path, format="wav")
    return wav_path
