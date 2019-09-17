import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
import pprint
import praw.models
from robot.config import OUTPUT_DIR, IMG_WIDTH, IMG_HEIGHT
import PIL
from PIL import Image


def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"--window-size={IMG_WIDTH}x{IMG_HEIGHT}")  # Full HD 1080p
    prefs = {'disk-cache-size': 4096}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_driver = os.path.join(
        os.getcwd(),
        "bin", "chromedriver")  # TODO config option
    driver = webdriver.Chrome(
        options=chrome_options,
        executable_path=chrome_driver)
    return driver


def screenshot_comment(comment: praw.models.Comment):
    url = "https://www.reddit.com" + comment.permalink
    out_dir = os.path.join(OUTPUT_DIR, comment.submission.fullname)
    out = os.path.join(out_dir, comment.fullname + '.png')
    logging.info(f"[SS COMMENT] url: {url} to {out}")

    try:
        selenium = driver()
        selenium.get(url)
        load_comments_button = selenium.find_element_by_xpath(
            "//*[contains(text(), 'View entire')]")
        if load_comments_button:
            load_comments_button.click()
        try:
            cmt = WebDriverWait(selenium, 10).until(
                lambda x: x.find_element_by_id(comment.fullname))
            cmt.screenshot(out)
            #update_dimensions(out)

        except TimeoutException:
            print("Page load timed out...")
    except Exception as e:
        logging.error(f'[SCREENSHOT COMMENT ERROR] {e}')
    finally:
        selenium.quit()

def update_dimensions(image_path):
    pannel = Image.new(mode = "RGB", size = (IMG_WIDTH, IMG_HEIGHT), color=(255,255,255))
    comment = Image.open(image_path)
    pannel.paste(comment,(0,0), comment)
    pannel.save(image_path)



def screenshot_object(obj: webdriver.Chrome, out: str):
    if not os.path.exists(out):
        try:
            selenium = driver()
            url = "https://www.reddit.com" + obj.permalink
            logging.info(f"[SCREENSHOT] url: {url} to {out}")
            selenium.get(url)
            view_entire = selenium.find_element_by_xpath(
                "//*[contains(text(), 'View entire')]")
            view_entire.click()
            success = selenium.save_screenshot(out)
        finally:
            selenium.quit()


def save_screenshot(
        driver: webdriver.Chrome, path: str = '/tmp/screenshot.png'):
    # Ref: https://stackoverflow.com/a/52572919/
    original_size = driver.get_window_size()
    required_width = driver.execute_script(
        'return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script(
        'return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element_by_tag_name(
        'body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])


def tests():
    out = '/tmp/teste_screen_comment.png'
    permalink = '/r/funny/comments/d2bwot/'
    selenium = driver()
    url = "https://www.reddit.com" + permalink
    logging.info(f"[SCREENSHOT] url: {url} to {out}")
    selenium.get(url)

    load_comments_button = selenium.find_elements_by_xpath(
        "//*[contains(text(), 'View entire')]")
    if load_comments_button:
        load_comments_button[0].click()
    # time.sleep(3)
    # save_screenshot(selenium)
    obj_id = 'd2bwot'

    # acha a div do topico inteiro
    main_div = selenium.execute_script(
        f"return document.getElementById('t3_{obj_id}').parentNode")
    main_div.screenshot('/tmp/main_div.png')

    selenium.quit()
