import os
import praw
from praw.models import MoreComments

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .sounds import list2mp3

from prompt_toolkit.shortcuts import ProgressBar

class RedditBot():

    def __init__(self, *args, **kwargs):
        self.driver = RedditBot.chrome_driver()

        self.output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        self.reddit = praw.Reddit(
            client_id="5F-D7_H2_UjZ7Q",
            client_secret="Dcw9gR5MTPzIps6nC9YqxzJA5x4",
            user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")

    @staticmethod
    def chrome_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")  # Full HD 1080p
        chrome_driver = os.path.join(
            os.getcwd(),
            "bin", "chromedriver")  # TODO config option
        driver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=chrome_driver)
        return driver

    def screenshot_topic(self, topic):
        topic_dir = os.path.join(self.output_dir, topic.id)
        if not os.path.exists(topic_dir):
            os.mkdir(topic_dir)
        out = os.path.join(topic_dir, topic.id+".png")
        if not os.path.exists(out):
            self.driver.get("https://www.reddit.com" + topic.permalink)
            self.driver.get_screenshot_as_file(out)

    def speak_topic(self, topic):
        topic_dir = os.path.join(self.output_dir, topic.id)
        if not os.path.exists(topic_dir):
            os.mkdir(topic_dir)
        out = os.path.join(topic_dir, topic.id+".mp3")
        tts_list = []
        tts_list.append(topic.title)
        topic.comments.replace_more()
        with ProgressBar() as pb:
            for i in pb(range(len(topic.comments))):
                for comment in topic.comments:
                    tts_list.append(comment.body)
        list2mp3(tts_list, out=out)

    def hot(self, limit=25):
        return self.reddit.front.hot(limit=limit)

    def DPS(self, comment_forest):
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
