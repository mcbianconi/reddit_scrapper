import praw
import pprint
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator

reddit = praw.Reddit(client_id = "5F-D7_H2_UjZ7Q",
                    client_secret = "Dcw9gR5MTPzIps6nC9YqxzJA5x4",
                    user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")


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


if __name__ == "__main__":
    print_formatted_text(HTML('<yellow>%s</yellow>') % 'HOT TOPICS\n')
    top = reddit.front.top(limit=25)
    topic = select_submission(top)
    topic.comments.replace_more(limit=2)
    all_comments = topic.comments.list()
    pprint.pprint(vars(all_comments[0]))