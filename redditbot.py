import collections
import concurrent.futures.thread as mp
import logging
import os
import threading
from functools import reduce
from pprint import pprint

import praw
from praw.models import MoreComments
from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.validation import Validator

from robot import images, sounds

OUTPUT_DIR = os.path.join(os.getcwd(), "output")

REDDIT = praw.Reddit(
    client_id="5F-D7_H2_UjZ7Q",
    client_secret="Dcw9gR5MTPzIps6nC9YqxzJA5x4",
    user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")


def print_color_text(text, color):
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
        print_formatted_text(HTML(f'<red>{k}</red> {v.title} \n'))

    validator = Validator.from_callable(
        lambda x: x in options.keys(),
        error_message="Invalid Option",
    )

    selected = prompt('>>> Submission: ', validator=validator)
    submission = options.get(selected)
    info(f'Submission {submission} selected')

    submission_dir = os.path.join(OUTPUT_DIR, submission.id)
    if not os.path.exists(submission_dir):
        os.mkdir(submission_dir)

    return submission


def _initialize_path():
    logging.debug("Initializing PATH")
    os.environ["PATH"] += os.path.join(os.path.abspath(__file__), "bin")


def DPS(comment_forest):
    """Return a depth-first list of all Comments.
    This list may contain :class:`.MoreComments` instances if
    :meth:`.replace_more` was not called first.
    """
    comments = []
    queue = list(comment_forest)
    while queue:
        comment = queue.pop(0)
        comments.append(comment)
        if not isinstance(comment, MoreComments):
            queue[0:0] = comment.replies
    return comments


def fetch_comment(comment):
    logging.info(f"Fetching comment {comment} in process {os.getpid()}")
    submission_dir = os.path.join(OUTPUT_DIR, comment.submission.id)
    filename = os.path.join(submission_dir, f'{comment.submission.id}_{comment.id}')
    images.screenshot_object(comment, filename + ".png")
    sounds.comment2mp3(comment, filename)
    return comment

def initialize():
    logging.basicConfig(level=logging.INFO)
    _initialize_path()
    info('Getting Hot Topics')
    
    submission = select_submission(REDDIT.front.hot(limit=25))

    info(f'Fetching {submission} image and sound')
    images.screenshot_topic(submission)
    sounds.submission2mp3(submission, OUTPUT_DIR)

    # get all comments and order them
    warn(f"Getting {submission} comments (this may take a while)")
    submission.comment_sort = "new"
    submission.comments.replace_more()
    comments = tuple(submission.comments.list())
    warn(f'Got {len(comments)} comments')
    
    def reducer(acc, val):
        acc[val.parent_id].append(val)
        return acc

    comments_by_parent = reduce(
        reducer,
        comments,
        collections.defaultdict(list)
    )

    pprint(comments_by_parent)

    
    with mp.ThreadPoolExecutor() as executor:
        done = executor.map(fetch_comment, comments)

    pprint(tuple(done))
    
    

if __name__ == "__main__":
    initialize()
