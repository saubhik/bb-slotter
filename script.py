import json
import logging
import os
import re
import smtplib
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
    if isinstance(subscriber["email"], list):
        to_addrs = subscriber["email"] + [from_addr]
    else:
        to_addrs = [subscriber["email"], from_addr]
    subject = f"{subscriber['area']} BB Slot Available!"
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
            to_addrs=to_addrs,
            msg="Subject: {}\n\n{}".format(subject, body),
        )
        subscriber["email_ts"] = datetime.utcnow()
        logging.info("Email sent...")
    except Exception as e:
        logging.warning(f"Error during emailing {e}")


def run_service():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) "
        "AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 "
        "Mobile Safari/535.19",
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    with open(file="subscribers.json", mode="r") as file:
        subscribers: List[Dict] = json.load(file)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver=driver, timeout=20)

    while True:
        try:
            for subscriber in subscribers:
                logging.info(
                    f"Trying city: {subscriber['city']}, area: {subscriber['area']}"
                )

                driver.get(url="https://www.bigbasket.com/")

                # click on change location button
                wait.until(
                    expected_conditions.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//default-location-component//"
                            "button[contains(@class, 'change-loc-btn')]",
                        )
                    )
                ).click()

                # set the city
                city_input = wait.until(
                    expected_conditions.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//form[@id='location']//input[@placeholder="
                            "'Type your city']",
                        )
                    )
                )
                city_input.click()
                city_input.send_keys(subscriber["city"])
                city_input.send_keys(Keys.RETURN)

                # set the area
                area_input = wait.until(
                    expected_conditions.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//form[@id='location']//"
                            "input[@placeholder="
                            "'Enter your area / apartment / pincode']",
                        )
                    )
                )
                area_input.click()
                area_input.send_keys(re.match(r"[a-zA-Z]+", subscriber["area"])[0])

                area_choices = wait.until(
                    expected_conditions.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            "//form[@id='location']//"
                            "ul[contains(@class, 'dropdown-menu')]/li",
                        )
                    )
                )

                area_found = False
                for choice in area_choices:
                    if choice.text == subscriber["area"]:
                        area_found = True
                        logging.info(f"Found area {choice.text}")
                        choice.click()
                        break

                if not area_found:
                    logging.error(msg=f"Area {subscriber['area']} not found")
                    continue

                # submit location change
                wait.until(
                    expected_conditions.element_to_be_clickable(
                        (By.XPATH, "//form[@id='location']//button[@type='submit']")
                    )
                ).click()

                # check slot element
                slot_element = wait.until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'homepage-card')]")
                    )
                )

                if "All Slots Full. Please Try Again Later" in slot_element.text:
                    logging.info("Found all slots full...")
                else:
                    logging.info("Found available slot!")
                    send_email(
                        subscriber=subscriber,
                        message=f"City: {subscriber['city']}, "
                        f"Area: {subscriber['area']}, "
                        f"Slot: {slot_element.text}",
                    )

                driver.delete_all_cookies()

        except Exception as exc:
            logging.exception(exc)
            driver.close()
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver=driver, timeout=20)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    run_service()
