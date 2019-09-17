import collections
import concurrent.futures.process as process
import concurrent.futures.thread as threads
import logging
import os
import time
from functools import reduce
from pprint import pprint
from mutagen.mp3 import MP3
import praw
from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.validation import Validator
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

from robot import config as config
from robot import images, sounds, video

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
    for k, v in options.items():
        print_formatted_text(HTML(f'<red>{k}</red> {v.title}'))

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


def fetch_comment(comment: praw.models.Comment):
    logging.info(f"Fetching comment {comment} in process {os.getpid()}")
    submission_dir = os.path.join(
        config.OUTPUT_DIR, comment.submission.fullname)
    filename = os.path.join(
        submission_dir, comment.fullname)
    if not os.path.exists(filename + '.png'):
        images.screenshot_comment(comment)
    if not os.path.exists(filename + '.mp3'):
        sounds.comment2mp3(comment)
    return comment


def fetch_submission(submission: praw.models.Submission):

    
    submission_dir = os.path.join(config.OUTPUT_DIR, submission.fullname)
    if not os.path.exists(submission_dir):
        os.mkdir(submission_dir)

    # get all comments and order them
    warn(f"Getting {submission} comments (this may take a while)")
    submission.comments.replace_more(limit=None)

    comments = order_comments_by_depth(submission.comments.list())
    #comments = tuple(submission.comments.list())
    root_comments = tuple(filter(lambda c: c.is_root, comments))

    #warn(f'Got {len(comments)} comments')
    warn(f'Got {len(root_comments)} ROOT comments')

    info(f'Creating AV Files')

    driver = images.driver()
    image_file = open(os.path.join(submission_dir, IMAGE_FILE_NAME), "a+")
    audio_file = open(os.path.join(submission_dir, AUDIO_FILE_NAME), "a+")

    try:
        info(f'Fetching {submission} image and sound')
        driver.get(f'https://www.reddit.com{submission.permalink}')

        view_entire = driver.find_element_by_xpath(
            "//*[contains(text(), 'View entire')]")
        view_entire.click()
        time.sleep(0.4)

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

        for i, comment in enumerate(tqdm(comments)):
            try:
                el = driver.find_element_by_id(comment.fullname)
                driver.execute_script(
                    "arguments[0].style.backgroundColor = 'azure'", el)
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'})",
                    el)
                time.sleep(0.4)

                comment_file_name = f'{str(i).zfill(3)}-{comment.fullname}'

                driver.save_screenshot(
                    os.path.join(
                        submission_dir, comment_file_name+'.png'))
                driver.execute_script(
                    "arguments[0].style.backgroundColor = 'white'", el)

                audio = sounds.comment2mp3(comment, os.path.join(
                    submission_dir, comment_file_name+'.mp3'))
                audio_file.write(
                    f"file '{submission_dir}/{comment_file_name}.mp3\nduration {audio.info.length}\n")

                image_file.write(
                    f"file '{submission_dir}/{comment_file_name}.png\nduration {audio.info.length}\n")
                

            except NoSuchElementException as e:
                print(f'Element {comment.fullname} not found on page')
            finally:
                pass
                #print(f'[SS] {i}/{len(comments)}')

    finally:
        image_file.close()
        audio_file.close()
        driver.quit()

    """
    Comando para criar o video
    ffmpeg -f concat -safe 0 -i image_file_list.txt -f concat -safe 0 -i audio_file_list.txt -vsync vfr -pix_fmt yuv420p  output.mp4
    """
#    #with process.ProcessPoolExecutor() as executor:
#    warn(f'Screenshoting all comments - This may take a lot of time')
#    with threads.ThreadPoolExecutor(config.NUM_THREADS) as executor:
#        done = tuple(
#            tqdm(
#                executor.map(fetch_comment, root_comments),
#                total=len(root_comments)))


def comments_by_parent(comments):
    def reducer(acc, val):
        acc[val.parent_id].append(val)
        return acc

    comments_by_parent = reduce(
        reducer,
        comments,
        collections.defaultdict(list)
    )

    return comments_by_parent


def initialize():
    logging.basicConfig(level=logging.WARN)
    _initialize_path()
    info('Getting Hot Topics')
    submission = select_submission(REDDIT.front.hot(limit=25))
    fetch_submission(submission)

    info(f'Creating Submission Video - This may take a lot of time')
    video.create_submission_video(submission)
    info(f'Done')


if __name__ == "__main__":
    initialize()
    # video.test_video_creatin()
