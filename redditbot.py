import logging
import os
import shutil
import subprocess
import time

import praw
from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.validation import Validator
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

from robot import config, images, sounds

IMAGE_FILE_NAME = 'image_file_list.txt'
AUDIO_FILE_NAME = 'audio_file_list.txt'

REDDIT = praw.Reddit(
    client_id="5F-D7_H2_UjZ7Q",
    client_secret="Dcw9gR5MTPzIps6nC9YqxzJA5x4",
    user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")


def print_color_text(text: str, color: str):
    print_formatted_text(HTML(f'<{color}>{text}</{color}>'))


def danger(text):
    print_color_text(text, 'red')


def info(text):
    print_color_text(text, 'cyan')


def warn(text):
    print_color_text(text, 'yellow')


def select_submission(submission_list):
    options = {str(key): sub for key, sub in enumerate(submission_list)}
    for key, value in options.items():
        print_formatted_text(HTML(f'<red>{key}</red> {value.title}'))

        validator = Validator.from_callable(
            lambda x: x in options.keys(),
            error_message="Invalid Option",
        )

    selected = prompt('>>> Submission: ', validator=validator)
    submission = options.get(selected)
    info(f'Submission {submission} selected')

    submission_dir = os.path.join(config.OUTPUT_DIR, submission.fullname)
    if not os.path.exists(submission_dir):
        info(f'Creating Submission folder @ {submission_dir}')
        os.mkdir(submission_dir)

    return submission


def _initialize_path():
    logging.debug("Initializing PATH")
    os.environ["PATH"] += os.path.join(os.path.abspath(__file__), "bin")


def order_comments_by_depth(comment_forest):
    """Return a depth-first list of all Comments.
    This list may contain :class:`.MoreComments` instances if
    :meth:`.replace_more` was not called first.
    """
    comments = []
    queue = list(comment_forest)
    while queue:
        comment = queue.pop(0)
        comments.append(comment)
        if not isinstance(comment, praw.models.MoreComments):
            queue[0:0] = comment.replies
    return tuple(comments)


def fetch_submission(submission: praw.models.Submission):

    submission_dir = os.path.join(config.OUTPUT_DIR, submission.fullname)
    if not os.path.exists(submission_dir):
        os.mkdir(submission_dir)

    # get all comments and order them
    warn(f"Getting {submission} comments (this may take a while)")
    submission.comments.replace_more(limit=None)

    comments = order_comments_by_depth(submission.comments.list())

    #warn(f'Got {len(comments)} comments')
    warn(f'Got {len(comments)} comments')

    info(f'Creating AV Files')

    driver = images.driver()

    image_file_path = os.path.join(submission_dir, IMAGE_FILE_NAME)
    image_file = open(image_file_path, "a+")

    audio_file_path = os.path.join(submission_dir, AUDIO_FILE_NAME)
    audio_file = open(audio_file_path, "a+")

    try:
        info(f'Fetching {submission} image and sound')
        driver.get(f'https://www.reddit.com{submission.permalink}')

        view_entire = driver.find_element_by_xpath(
            "//*[contains(text(), 'View entire')]")
        view_entire.click()
        time.sleep(1)

        info(f'Taking Submission Screenshot')
        submission_screenshot = os.path.join(
            submission_dir, submission.fullname + ".png")
        driver.save_screenshot(submission_screenshot)

        info(f'Making Submission TTS')
        sub_audio = sounds.submission2mp3(submission)
        audio_file.write(
            f"file '{submission_dir}/{submission.fullname}.mp3\nduration {sub_audio.info.length}\n")
        image_file.write(
            f"file '{submission_dir}/{submission.fullname}.png\nduration {sub_audio.info.length}\n")

        video_length = 0
        video_length += sub_audio.info.length

        for i, comment in enumerate(tqdm(comments)):
            try:
                if video_length < 11 * 60:
                    element = driver.find_element_by_id(comment.fullname)
                    driver.execute_script(
                        "arguments[0].style.backgroundColor = 'azure'",
                        element)
                    driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'})",
                        element)
                    time.sleep(0.8)

                    comment_file_name = f'{str(i).zfill(3)}-{comment.fullname}'

                    driver.save_screenshot(
                        os.path.join(
                            submission_dir, comment_file_name+'.png'))
                    driver.execute_script(
                        "arguments[0].style.backgroundColor = 'white'",
                        element)

                    audio = sounds.comment2mp3(comment, os.path.join(
                        submission_dir, comment_file_name+'.mp3'))

                    audio_file.write(
                        f"file '{submission_dir}/{comment_file_name}.mp3\nduration {audio.info.length}\n")

                    image_file.write(
                        f"file '{submission_dir}/{comment_file_name}.png\nduration {audio.info.length}\n")

                    video_length += audio.info.length

            except NoSuchElementException:
                logging.debug(
                    'Comment %s not found on page - Skipping' % comment.fullname)

    finally:
        info('Done Processing Comments')
        image_file.close()
        audio_file.close()
        driver.quit()

    info('Starting to make the video')
    video_name = submission.title.replace(" ", "_") + '.mp4'
    cmnd = [
        "ffmpeg",
        "-f", "concat", "-safe", "0", "-i", f"{image_file_path}",
        "-f", "concat", "-safe", "0", "-i", f'{audio_file_path}',
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "-shortest", video_name]

    warn(cmnd)
    subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info('Done!')


def clean_files():
    shutil.rmtree(config.OUTPUT_DIR)


def initialize():
    logging.basicConfig(level=logging.WARN)
    _initialize_path()
    info('Getting Hot Topics')
    submission = select_submission(REDDIT.front.hot(limit=25))
    fetch_submission(submission)
    clean_files()


if __name__ == "__main__":
    initialize()
