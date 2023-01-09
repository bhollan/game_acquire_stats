"""
# Filename: run_selenium.py
"""

## Run selenium and chrome driver to scrape data from cloudbytes.dev
import time
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")

# Set path to chromedriver as per your configuration
homedir = os.path.expanduser("~")
webdriver_service = Service(f"{homedir}/chromedriver/stable/chromedriver")

# Choose Chrome Browser
browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# signin = driver.find_element_by_link_text("sign in")
#             ec = expected_conditions.visibility_of(signin)
#             webdriverwait(driver, 30).until(ec)
#             signin.click()



# Get page
browser.get("https://acquire.tlstyer.com/stats/?username=bhollan")
# table = browser.find_element(By.ID, "user-summary")
vis = EC.text_to_be_present_in_element((By.ID, "user-summary"), "±")

WebDriverWait(browser, 10).until(vis)


# print(wait_until_visibilty_is_confirmed(browser, table, 0.1))

game_summary = browser.find_element(By.ID, "user-summary").get_attribute("content")
print(f"{game_summary}")


#Wait for 10 seconds
time.sleep(4)
browser.quit()
