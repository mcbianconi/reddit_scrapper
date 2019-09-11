import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")  # Full HD 1080p
    chrome_driver = os.path.join(
        os.getcwd(),
        "bin", "chromedriver")  # TODO config option
    driver = webdriver.Chrome(
        chrome_options=chrome_options, executable_path=chrome_driver)
    return driver

OUTPUT_DIR = os.path.join(os.getcwd(), "output")

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


def screenshot_topic(topic):
    logging.info("screenshoting %s" % topic)
    topic_dir = os.path.join(OUTPUT_DIR, topic.id)
    if not os.path.exists(topic_dir):
        os.mkdir(topic_dir)
    out = os.path.join(topic_dir, topic.id+".png")
    if not os.path.exists(out):
        screenshot_object(topic, out)


def screenshot_frame(frame):
    logging.info("screenshoting %s" % frame)
    out = os.path.join(OUTPUT_DIR, frame.topic_id)
    if not os.path.exists(out):
        os.mkdir(out)
    image = os.path.join(out, frame.topic_id + "_" + frame.id + ".png")
    if not os.path.exists(image):
        screenshot_object(frame.comments[0], image)


def screenshot_commnet(comment, out):
    if not os.path.exists(out):
        selenium = _chrome_driver()
        url = "https://www.reddit.com" + comment.permalink
        logging.info(f"[SCREENSHOT] url: {url} to {out}")
        selenium.get(url)
        load_comments_button = selenium.find_elements_by_xpath("//*[contains(text(), 'View entire')]")
        if load_comments_button:
            load_comments_button.click()

        success = False
        while not success:
            success = selenium.save_screenshot(out)
        selenium.close()

def screenshot_object(obj, out):
    if not os.path.exists(out):
        selenium = _chrome_driver()
        url = "https://www.reddit.com" + obj.permalink
        logging.info(f"[SCREENSHOT] url: {url} to {out}")
        selenium.get(url)
        success = False
        while not success:
            success = selenium.save_screenshot(out)
        selenium.close()

def save_screenshot(driver: webdriver.Chrome, path: str = '/tmp/screenshot.png'):
    # Ref: https://stackoverflow.com/a/52572919/
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])

if __name__ == "__main__":
    out = '/tmp/teste_screen_comment.png'
    permalink = '/r/funny/comments/d2bwot/printers/ezuv07q/'
    selenium = _chrome_driver()
    url = "https://www.reddit.com" + permalink
    logging.info(f"[SCREENSHOT] url: {url} to {out}")
    selenium.get(url)
    
    save_screenshot(selenium)

    selenium.close()