import logging
import os

from gtts import gTTS
from prompt_toolkit.shortcuts import ProgressBar


def text2tts(text, lang='en', slow=False):
    return gTTS(text=text, lang=lang, slow=slow)


def comment2mp3(comment, out):
    extension = ".mp3"
    filename = out + extension
    if not os.path.exists(filename):
        with open(filename, 'wb') as mp3:
                logging.info(f"[SOUND] {filename} to {out} ")
                tts = text2tts(comment.body)
                tts.write_to_fp(mp3)


def frame2mp3(frame, out_folder):
    extension = ".mp3"
    out_dir = os.path.join(out_folder, frame.topic_id)
    filename = os.path.join(out_dir, frame.topic_id + "_"+frame.id) + extension
    logging.info("saving sound %s" % filename)
    with open(filename, 'wb') as mp3:
        tts = text2tts(frame.text)
        tts.write_to_fp(mp3)


def submission2mp3(submission, out_folder):
    extension = ".mp3"
    out_dir = os.path.join(out_folder, submission.id)
    filename = os.path.join(out_dir, submission.id) + extension
    logging.info("saving sound %s" % filename)
    with open(filename, 'wb') as mp3:
        tts = text2tts(submission.title)
        tts.write_to_fp(mp3)
