import os
import pprint

from robot.scrapper import RedditBot

from prompt_toolkit import HTML, print_formatted_text, prompt
from prompt_toolkit.validation import Validator


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


def banner():
    print_formatted_text(HTML('<yellow>%s</yellow>') % 'HOT TOPICS\n')

if __name__ == "__main__":
    _initialize_path()
    banner()
    
    bot = RedditBot()
    topic = select_submission(bot.hot())
    print_formatted_text(HTML('<cyan>%s</cyan>') % topic.id)

    #bot.screenshot_topic(topic)
    #bot.speak_topic(topic)
    topic.comments.replace_more()
    bot.DPS(topic.comments)