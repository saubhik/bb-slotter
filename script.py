import logging
import os
import smtplib
import time
from datetime import datetime, timedelta
from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

locations = [
    {
        "city": os.environ["CITY1"],
        "area": os.environ["AREA1"],
        "email_ts": datetime.utcnow() - timedelta(hours=1),
    },
    {
        "city": os.environ["CITY2"],
        "area": os.environ["AREA2"],
        "email_ts": datetime.utcnow() - timedelta(hours=1),
    },
]


def _sanitise_string(text: str):
    return (
        text.encode(encoding="ascii", errors="ignore").decode(encoding="ascii").strip()
    )


def send_email(location: Dict, message: str) -> None:
    if (datetime.utcnow() - location["email_ts"]).total_seconds() < 60 * 5:
        logging.info("I do not want to send frequent emails...")
        return

    logging.info("Trying to send email...")

    sent_from = os.environ["FROM_ADDR"]
    to = [os.environ["TO_ADDR"], sent_from]
    subject = f"{location['city']} BB Slot Available!"
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
        server.login(user=sent_from, password=os.environ["EMAIL_PASSWORD"])
        server.sendmail(
            from_addr=sent_from,
            to_addrs=to,
            msg="Subject: {}\n\n{}".format(subject, body),
        )
        location["email_ts"] = datetime.utcnow()
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
    first_time = True

    while True:
        try:
            for location in locations:
                logging.info(f"Trying location {location['city']}")

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
                city_element.send_keys(location["city"])
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
                area_element.send_keys(location["area"])
                time.sleep(1)
                area_element.send_keys(Keys.RETURN)
                time.sleep(1)

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
                        location=location,
                        message=f"City: {location['city']}, "
                        f"Area: {location['area']}, "
                        f"Slot: {slot_element.text}",
                    )

        except Exception as exc:
            logging.warning(f"Raised exception: {type(exc).__name__}")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    run_service()
