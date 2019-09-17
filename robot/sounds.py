import logging
import os

from gtts import gTTS
from prompt_toolkit.shortcuts import ProgressBar
import praw.models
from robot import config
from mutagen.mp3 import MP3


def text2tts(text, lang='en', slow=False):
    return gTTS(text=text, lang=lang, slow=slow)


def comment2mp3(comment: praw.models.Comment, out: str):
    if not os.path.exists(out):
        with open(out, 'wb') as mp3:
            logging.info(f"[SOUND] TTS {out}")
            tts = text2tts(comment.body)
            tts.write_to_fp(mp3)
    return MP3(out)


def submission2mp3(submission):
    out = os.path.join(config.OUTPUT_DIR,
                       submission.fullname, submission.fullname)
    filename = out + ".mp3"
    if not os.path.exists(filename):
        with open(filename, 'wb') as mp3:
            logging.info(f"[SOUND] TTS {filename}")
            tts = text2tts(submission.title)
            tts.write_to_fp(mp3)
    return MP3(filename)
