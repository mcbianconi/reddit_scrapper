import os
from pprint import pprint
import praw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium.common.exceptions import NoSuchElementException

REDDIT = praw.Reddit(
    client_id="5F-D7_H2_UjZ7Q",
    client_secret="Dcw9gR5MTPzIps6nC9YqxzJA5x4",
    user_agent="terminal:redditspeaker:1 (by /u/mcbianconi)")


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"--window-size=1920x1080")  # Full HD 1080p
prefs = {'disk-cache-size': 4096}
chrome_options.add_experimental_option('prefs', prefs)
chrome_driver = os.path.join(os.getcwd(), "bin", "chromedriver")
driver = webdriver.Chrome(options=chrome_options,
                          executable_path=chrome_driver)

hot = REDDIT.front.hot(limit=1)

submission = hot.next()

url = f'https://www.reddit.com{submission.permalink}'
print(url)
driver.get(url)

view_entire = driver.find_element_by_xpath(
    "//*[contains(text(), 'View entire')]")
view_entire.click()

driver.save_screenshot('/tmp/screenshot.png')

main_div = driver.execute_script(
    f"return document.getElementById('{submission.fullname}').parentNode")
time.sleep(0.4)
main_div.screenshot(f'/tmp/{submission.fullname}.png')

submission.comments.replace_more()
comments = submission.comments.list()

for i, comment in enumerate(comments):
    try:
        el = driver.find_element_by_id(comment.fullname)
        driver.execute_script("arguments[0].style.backgroundColor = 'red'", el)
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'auto',block: 'center',inline: 'center'})",
            el)
        time.sleep(0.4)
        driver.save_screenshot(
            f'/tmp/{str(i).zfill(3)}-{comment.fullname}.png')
        driver.execute_script(
            "arguments[0].style.backgroundColor = 'white'", el)
            sou
    except NoSuchElementException as e:
        print(f'Element {comment.fullname} not found on page')
    finally:
        print(f'[SS] {i}/{len(comments)}')


print('Done')

driver.quit()
