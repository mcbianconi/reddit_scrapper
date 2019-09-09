import os
import pprint

import praw
from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.validation import Validator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class RedditBot():

    def __init__(self, *args, **kwargs):
        self.driver = RedditBot.chrome_driver()
        self.output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        self.reddit = praw.Reddit(client_id = "5F-D7_H2_UjZ7Q",
                    client_secret = "Dcw9gR5MTPzIps6nC9YqxzJA5x4",
                    user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")

    @staticmethod
    def chrome_driver():   
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080") # Full HD 1080p
        chrome_driver = os.path.join(os.getcwd(), "bin", "chromedriver")
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
        return driver

    def screenshot_topic(self, topic):
        topic_dir =  os.path.join(self.output_dir, topic.id)
        if not os.path.exists(topic_dir):
            os.mkdir(topic_dir)
        filename = os.path.join(topic_dir, topic.id+".png")
        if not os.path.exists(filename):
            self.driver.get("https://www.reddit.com" + topic.permalink)
            self.driver.get_screenshot_as_file(filename)

    def hot(self, limit=25):
        return self.reddit.front.hot(limit = limit)


def select_submission(submission_list):
    options = {str(key):sub for key, sub in enumerate(submission_list)}
    for k, v in options.items():
        print_formatted_text(HTML('<red>%s</red> %s \n' % (k, v.title)))

    validator = Validator.from_callable(
        lambda x: x in options.keys(),
        error_message="Invalid Option",
        move_cursor_to_end=False
    )
    selected = prompt('Select Post: ', validator = validator)

    return options.get(selected)

def _initialize_path():
    os.environ["PATH"] += os.path.join(os.path.abspath(__file__), "bin")


if __name__ == "__main__":
    _initialize_path()
    bot = RedditBot()
    print_formatted_text(HTML('<yellow>%s</yellow>') % 'HOT TOPICS\n')
    topic = select_submission(bot.hot())

    bot.screenshot_topic(topic)