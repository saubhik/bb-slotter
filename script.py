import logging
import os
import smtplib
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List

import fire
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

last_email_ts = datetime.utcnow() - timedelta(hours=1)


def send_email(message: str):
    sent_from = os.environ["FROM_ADDR"]
    to = [os.environ["TO_ADDR1"], os.environ["TO_ADDR2"]]
    subject = "BB Slot Available!"
    body = message

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    Check out BB right now!
    Details are given as follows.
    %s
    
    From your beloved bb-slotter bot.
    """ % (
        sent_from,
        ", ".join(to),
        subject,
        body,
    )

    global last_email_ts
    if (last_email_ts - datetime.utcnow()).total_seconds() < 60 * 10:
        return

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(user=sent_from, password=os.environ["PASSWORD"])
        server.sendmail(
            from_addr=sent_from, to_addrs=to, msg=email_text,
        )
        last_email_ts = datetime.utcnow()
    except Exception as e:
        logging.warning(f"Error during emailing {e}")


def run_service(locations: Optional[List[Dict]] = None):
    if locations is None:
        locations = [
            {"city": os.environ["CITY1"], "area": os.environ["AREA1"]},
            {"city": os.environ["CITY2"], "area": os.environ["AREA2"]},
        ]

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")

    # download & move chromedriver to PATH
    driver = webdriver.Chrome(options=options)
    first_time = True

    while True:
        for location in locations:
            logging.info(f"Trying location {location['city']}")

            driver.get(url=os.environ["URL"])
            time.sleep(5)

            if first_time:
                location_element = driver.find_element_by_xpath(
                    "//div[@id='mainHeader']/div[3]/div[1]/div[2]"
                )
                logging.info(f"Currently at {location_element.text}...")
                location_element.click()
                time.sleep(1)
                first_time = False
            else:
                element = driver.find_element_by_xpath(
                    "//div[@id='mainHeader']//div[2]//div/div[2]"
                )
                element.click()
                time.sleep(1)

            element = driver.find_element_by_xpath(
                "//div[@id='modal']/div/div/div[2]/div[1]/span"
            )
            logging.info(f"Changing city from {element.text}...")
            element.click()
            time.sleep(1)
            city_element = driver.find_element_by_xpath(
                "//input[@placeholder='Select your city']"
            )
            city_element.send_keys(location["city"])
            time.sleep(1)
            city_element.send_keys(Keys.RETURN)
            time.sleep(1)
            area_element = driver.find_element_by_xpath(
                "//input[@placeholder='Enter your area / apartment / pincode']"
            )
            area_element.send_keys(location["area"])
            time.sleep(1)
            area_element.send_keys(Keys.RETURN)
            time.sleep(1)
            submit_btn = driver.find_element_by_xpath(
                "//form[@action='/choose-city/']/button"
            )
            submit_btn.click()
            time.sleep(5)
            slot_element = driver.find_element_by_xpath(
                "//div[@id='root']/div/div[2]/div[2]/div[3]/section/div[2]/div"
            )

            if "All Slots Full. Please Try Again Later" in slot_element.text:
                logging.info("Found all slots full. Refreshing...")
            else:
                logging.info("Found available slot!")
                logging.info(f"Slot details: {slot_element.text}")
                send_email(
                    message=f"City: {location['city']}, "
                    f"Area: {location['area']}, "
                    f"Slot: {slot_element.text}"
                )


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    fire.Fire(run_service())
