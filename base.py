import os
import sys
import requests
import json
import zipfile
import random
import logging
import time
import undetected_chromedriver as uc
from PIL import Image, ImageDraw
import pyautogui

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

from twocaptcha import TwoCaptcha

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)

from xpath import *

api_key = "f5e8ab0a052afe467a849001befbb0fc"
WAIT_FOR_CAPTCHA = 3

BROWER_TAB_AND_SEARCH_HEIGHT = 78
API_URL = "https://worker.bunnydream.site"

solver = TwoCaptcha(api_key)

response = requests.get("https://ipinfo.io")
IP_ADDRESS = response.json().get("ip", "")

if not IP_ADDRESS:
    sys.exit("Cannot get IP Address")

logging.info(f"Running on IP: {IP_ADDRESS}")


def post_viewed():
    headers = {"Content-Type": "application/json"}
    payload = {"ip": IP_ADDRESS}

    requests.post(f"{API_URL}/workercash/count/", headers=headers, json=payload)


def solve_click_captcha(image_path: str = "captcha.png"):
    try:
        result = solver.coordinates(image_path)
        logging.info(result)
        coordinates = result["code"].split(":")[1].split(";")
        coordinates_dict = {}
        for coordinate in coordinates:
            x, y = coordinate.split(",")
            x = x.split("=")[1]
            y = y.split("=")[1]
            coordinates_dict[x] = y

        logging.info(coordinates_dict)
        return coordinates_dict
    except Exception as e:
        logging.info(e)
        return {}


def get_chromedriver(use_proxy=False, user_agent=None, is_need_location=False):
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.headless = False

    driver = uc.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
        # headless=False,
    )

    return driver


class WorkerCash:
    def __init__(
        self,
        driver: webdriver.Chrome,
        inital_url: str = "https://worker.cash/",
        username: str = "ps8919874@gmail.com",
        password: str = "!ElyQREbnoh@",
        recovery_email: str = "dorethabrinkley@outlook.com",
    ):
        self.driver = driver
        self.driver.get(inital_url)
        self.driver.maximize_window()
        self.timeout = 10
        self.username = username
        self.password = password
        self.recovery_email = recovery_email

    def wait_and_find_element(self, by: By, value: str):
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(
                (
                    by,
                    value,
                )
            )
        )

        return self.driver.find_element(
            by,
            value=value,
        )

    def wait_interactable_and_find_element(self, by: By, value: str):
        WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(
                (
                    by,
                    value,
                )
            )
        )

        return self.driver.find_element(
            by,
            value=value,
        )

    def quit_worker(self):
        self.driver.quit()

    def login(self):
        logging.info(f"Logging in to account: {self.username}")

        login_btn = self.wait_interactable_and_find_element(
            By.XPATH, value=XPATH_GOOGLE_LOGIN
        )
        login_btn.click()
        logging.info(f"Clicked login button!")

        identifierId = self.wait_interactable_and_find_element(
            by=By.ID, value="identifierId"
        )
        logging.info(f"Found identifierId. Sending username...")
        identifierId.send_keys(self.username)

        next_button = self.wait_interactable_and_find_element(
            by=By.XPATH, value=XPATH_USERNAME_NEXT_BUTTON
        )
        next_button.click()
        logging.info(f"Clicked next button!")

        password_input = self.wait_interactable_and_find_element(
            by=By.XPATH, value=XPATH_PASSWORD_INPUT
        )
        logging.info(f"Found password_input. Sending password_input...")
        password_input.send_keys(self.password)

        next_button = self.wait_interactable_and_find_element(
            by=By.XPATH, value=XPATH_PASSWORD_NEXT_BUTTON
        )
        next_button.click()
        logging.info(f"Clicked next button!")

        try:
            confirm_email_button = self.wait_interactable_and_find_element(
                by=By.XPATH, value=XPATH_CONFIRM_RECOVERY_EMAIL
            )
            confirm_email_button.click()

            confirm_email_input = self.wait_interactable_and_find_element(
                by=By.XPATH, value=XPATH_CONFIRM_RECOVERY_EMAIL_INPUT
            )
            confirm_email_input.send_keys(self.recovery_email)

            confirm_email_next = self.wait_interactable_and_find_element(
                by=By.XPATH, value=XPATH_CONFIRM_RECOVERY_EMAIL_NEXT
            )
            confirm_email_next.click()
        except:
            pass

        logging.info("Login successfully. Start earning... !!!")

    def watch_one_time(self) -> bool:
        logging.info("Closing leftover tabs...")
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(
                self.driver.window_handles[len(self.driver.window_handles) - 1]
            )
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        logging.info("Watching...")
        self.driver.get("https://worker.cash/tasks/video/")

        watch_video_btn = self.wait_interactable_and_find_element(
            by=By.XPATH, value=XPATH_WATCH_VIDEO
        )

        allLimit = self.wait_and_find_element(by=By.ID, value="allLimit")

        print(f"allLimit.text: {allLimit.text}")
        allLimit = int(allLimit.text)
        if allLimit <= 0:
            logging.info(f"No video left for {self.username}")
            # TODO: Noti
            return False

        watch_video_btn.click()

        self.driver.switch_to.window(self.driver.window_handles[1])
        task_video_iframe = self.wait_and_find_element(by=By.ID, value="task_video")
        self.driver.switch_to.frame(task_video_iframe)
        play_video_btn = self.wait_interactable_and_find_element(
            by=By.XPATH, value=XPATH_YOUTUBE_PLAY_VIDEO
        )
        play_video_btn.click()
        self.driver.switch_to.default_content()

        is_solved_captcha = False

        for i in range(30):
            full_text = self.driver.page_source
            if "Your view has been counted".lower() in full_text.lower():
                logging.info("Your view has been counted")
                post_viewed()
                return True

            if is_solved_captcha:
                continue

            try:
                wrapper_captcha = self.driver.find_element(
                    by=By.ID, value="wrapper_captcha"
                )
                captcha = wrapper_captcha.find_element(by=By.ID, value="captcha")
                style = captcha.get_attribute("style")
                if style:
                    logging.info(f"Found captcha on {i+1} second(s)")
                    sleep(1)

                    is_captured_captcha = False
                    waitted_time = 0
                    while not is_captured_captcha and waitted_time < WAIT_FOR_CAPTCHA:
                        try:
                            full_text = self.driver.page_source
                            if (
                                "Your view has been counted".lower()
                                in full_text.lower()
                            ):
                                logging.info("Your view has been counted")
                                post_viewed()
                                return True
                            wrapper_captcha = self.driver.find_element(
                                by=By.ID, value="wrapper_captcha"
                            )
                            wrapper_captcha.screenshot("captcha.png")
                            is_captured_captcha = True
                        except:
                            waitted_time += 0.1
                            sleep(0.1)

                    if not is_captured_captcha:
                        logging.error("Capture captcha failed...")
                        return True

                    wrapper_captcha = self.driver.find_element(
                        by=By.ID, value="wrapper_captcha"
                    )
                    location = wrapper_captcha.location
                    size = wrapper_captcha.size
                    x = location["x"]
                    y = location["y"]
                    width = size["width"]
                    height = size["height"]
                    logging.info(
                        f"Wrapper captcha is located at ({x}, {y}) with width {width} and height {height}"
                    )

                    # Execute JavaScript code to get the position of the window
                    window_position = self.driver.execute_script(
                        "return window.screenX + ',' + window.screenY;"
                    )

                    # Parse the position values
                    window_x, window_y = map(int, window_position.split(","))
                    window_y += BROWER_TAB_AND_SEARCH_HEIGHT
                    logging.info(f"window_position: {window_x}:{window_y}")

                    # Calculate the position of the wrapper_captcha element relative to the window
                    captcha_x = wrapper_captcha.location["x"] + window_x
                    captcha_y = wrapper_captcha.location["y"] + window_y

                    # # Move the mouse cursor to the center of the captcha
                    # pyautogui.moveTo(captcha_x, captcha_y)
                    # sleep(1)
                    # pyautogui.moveTo(captcha_x + width, captcha_y + height)

                    coordinates_dict = solve_click_captcha()
                    # coordinates_dict = {'153': '52', '105': '153', '191': '147'}

                    for x, y in coordinates_dict.items():
                        x, y = int(x), int(y)
                        logging.info(f"Clicking on {x}, {y}")

                        try:
                            pyautogui.moveTo(captcha_x + x, captcha_y + y)
                            sleep(0.2)
                            pyautogui.click()
                            sleep(0.2)
                            is_solved_captcha = True
                        except:
                            return True

                    is_solved_captcha = True

            except Exception as e:
                pass

            logging.info(f"Watching {i+1} second(s)")
            sleep(1)

        return True

    def watch(self):
        while True:
            continue_watch = self.watch_one_time()
            if not continue_watch:
                break


def read_accounts():
    with open("accounts.txt", "r") as f:
        accounts = f.readlines()

    accounts = [account for account in accounts if account]

    return accounts


def main():
    # driver.implicitly_wait(30)

    accounts = read_accounts()

    while True:
        for account in accounts:
            username, password, recovery = account.strip("\n").strip().split("|")[:3]
            driver = get_chromedriver()
            workercash = WorkerCash(
                driver=driver,
                username=username,
                password=password,
                recovery_email=recovery,
            )

            try:
                workercash.login()
                workercash.watch()
                workercash.quit_worker()
            except Exception as e:
                print(e)
                workercash.quit_worker()
                sleep(10)

            logging.info(f"Sleeping 30 minutes...")
            sleep(30 * 60)

    sleep(1000)


if __name__ == "__main__":
    main()
