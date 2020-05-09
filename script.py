import json
import logging
import os
import re
import smtplib
from datetime import datetime
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


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
        logging.exception(e)


class Service:
    def __init__(self):
        self._driver: Optional[WebDriver] = None
        self._previous_location: str

    def _init_driver(self):
        logging.info(msg="Starting a new session")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        if self._driver is not None:
            self._driver.close()
        self._driver = webdriver.Chrome(options=options)
        self._driver.get(url="https://www.bigbasket.com/")
        self._previous_location = "560004, Bangalore"

    def _get_element(self, xpath: str, timeout: int = 10) -> WebElement:
        element: WebElement = WebDriverWait(driver=self._driver, timeout=timeout).until(
            expected_conditions.element_to_be_clickable((By.XPATH, xpath))
        )
        return element

    def _list_elements(self, xpath: str, timeout: int = 10) -> List[WebElement]:
        elements: List[WebElement] = WebDriverWait(
            driver=self._driver, timeout=timeout
        ).until(expected_conditions.presence_of_all_elements_located((By.XPATH, xpath)))
        return elements

    def run(self):
        self._init_driver()

        with open(file="subscribers.json", mode="r") as file:
            subscribers: List[Dict] = json.load(file)

        while True:
            try:
                for subscriber in subscribers:
                    logging.info(
                        f"Trying city: {subscriber['city']}, area: {subscriber['area']}"
                    )

                    element = self._get_element(
                        xpath="//*[contains(text(), "
                        f"'{self._previous_location.split(',')[0]}')]"
                    )
                    element.click()

                    # change city
                    city_element = self._get_element(
                        xpath="//*[@placeholder='Select your city']"
                    )
                    city_element.click()
                    city_element = self._get_element(
                        xpath="//input[@placeholder='Select your city']"
                    )
                    city_element.send_keys(subscriber["city"])
                    city_element.send_keys(Keys.RETURN)
                    logging.info(msg=f"Changed city to {subscriber['city']}")

                    # change area
                    area_element = self._get_element(
                        xpath="//input[@placeholder="
                        "'Enter your area / apartment / pincode']",
                    )
                    area_element.send_keys(
                        re.match(r"[a-zA-Z]+", subscriber["area"])[0]
                    )
                    area_choices = self._list_elements(
                        xpath="//div[contains(@class, 'area-select')]//ul/li"
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
                    submit_btn = self._get_element(xpath="//button[@type='submit']")
                    submit_btn.click()

                    # check slot element
                    try:
                        slot_element = self._get_element(
                            xpath="//*[contains(text(), 'All Slots Full')]"
                        )
                        logging.info(msg=slot_element.text)
                    except TimeoutException:
                        slot_element = self._get_element(
                            xpath="//*[contains(text(), 'Standard Delivery')]",
                        )
                        logging.info("Found available slot!")
                        logging.info(msg=slot_element.text)
                        send_email(
                            subscriber=subscriber,
                            message=f"City: {subscriber['city']}, "
                            f"Area: {subscriber['area']}, "
                            f"Slot: {slot_element.text}",
                        )

                    self._previous_location = subscriber["shortLocation"]

            except Exception as exc:
                logging.exception(exc)
                self._init_driver()


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    Service().run()
