import json
import logging
import os
import re
import smtplib
import time
from datetime import datetime
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def _sanitise_string(text: str):
    return (
        text.encode(encoding="ascii", errors="ignore").decode(encoding="ascii").strip()
    )


def send_email(subscriber: Dict, message: str) -> None:
    if "email_ts" in subscriber:
        if (datetime.utcnow() - subscriber["email_ts"]).total_seconds() < 60 * 2:
            logging.info("I do not want to send frequent emails...")
            return

    logging.info("Trying to send email...")

    from_addr = os.environ["FROM_ADDR"]
    to = [from_addr, subscriber["email"]]
    subject = f"{subscriber['city']}-{subscriber['area']} BB Slot Available!"
    body = """\
    Check out BB right now!
    Details are given as follows.
    
    %s
    
    From your beloved bb-slotter bot.
    """ % (
        message,
    )

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(user=from_addr, password=os.environ["EMAIL_PASSWORD"])
        server.sendmail(
            from_addr=from_addr,
            to_addrs=to,
            msg="Subject: {}\n\n{}".format(subject, body),
        )
        subscriber["email_ts"] = datetime.utcnow()
        logging.info("Email sent...")
    except Exception as e:
        logging.warning(f"Error during emailing {e}")


def run_service():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(time_to_wait=10)
    wait = WebDriverWait(driver=driver, timeout=20)

    with open(file="subscribers.json", mode="r") as file:
        subscribers: List[Dict] = json.load(file)

    first_time = True

    while True:
        try:
            for subscriber in subscribers:
                logging.info(
                    f"Trying city: {subscriber['city']}, area: {subscriber['area']}"
                )

                driver.get(url=os.environ["URL"])
                time.sleep(5)

                if first_time:
                    location_element = wait.until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, "//div[@id='mainHeader']/div[3]/div[1]/div[2]")
                        )
                    )
                    logging.info(f"Currently at {location_element.text}...")
                    location_element.click()
                    time.sleep(1)
                    first_time = False
                else:
                    element = wait.until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, "//div[@id='mainHeader']//div[2]//div/div[2]")
                        )
                    )
                    element.click()
                    time.sleep(1)

                element = wait.until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@id='modal']/div/div/div[2]/div[1]/span")
                    )
                )
                logging.info(f"Changing city from {_sanitise_string(element.text)}...")
                element.click()
                time.sleep(1)

                # change city
                city_element = wait.until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//input[@placeholder='Select your city']")
                    )
                )
                city_element.send_keys(subscriber["city"])
                time.sleep(1)
                city_element.send_keys(Keys.RETURN)
                time.sleep(1)

                # change area
                area_element = wait.until(
                    expected_conditions.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input"
                            "[@placeholder='Enter your area / apartment / pincode']",
                        )
                    )
                )

                area_element.send_keys(re.match(r"[a-zA-Z]+", subscriber["area"])[0])
                area_choices = wait.until(
                    expected_conditions.presence_of_all_elements_located(
                        (By.XPATH, "//div[@id='modal']//ul/div")
                    )
                )

                for choice in area_choices:
                    if choice.text == subscriber["area"]:
                        logging.info(f"Found area {choice.text}")
                        choice.click()
                        time.sleep(1)
                        break

                # submit location change
                submit_btn = wait.until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//form[@action='/choose-city/']/button")
                    )
                )
                submit_btn.click()
                time.sleep(1)

                # check slot element
                slot_element = wait.until(
                    expected_conditions.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@id='root']/"
                            "div/div[2]/div[2]/div[3]/section/div[2]/div",
                        )
                    )
                )

                if "All Slots Full. Please Try Again Later" in slot_element.text:
                    logging.info("Found all slots full. Refreshing...")
                else:
                    logging.info("Found available slot!")
                    send_email(
                        subscriber=subscriber,
                        message=f"City: {subscriber['city']}, "
                        f"Area: {subscriber['area']}, "
                        f"Slot: {slot_element.text}",
                    )

        except Exception as exc:
            logging.warning(f"Raised exception: {type(exc).__name__}")
            logging.info("Starting a new session...")
            driver.close()
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(time_to_wait=10)
            wait = WebDriverWait(driver=driver, timeout=20)
            first_time = True


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    run_service()
