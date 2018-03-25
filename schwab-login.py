#!/usr/bin/python


import json
import os
import selenium
from   selenium import webdriver
from   selenium.webdriver.common.by import By
from   selenium.webdriver.support.ui import WebDriverWait
from   selenium.webdriver.support import expected_conditions as EC
import sys
import time


### Login Credentials
# You might want to load via ENV or secure keystore etc, can be dangerous to have 
# sitting on your drive
creds = json.load(open('schwab.creds'))
LOGIN = creds['login']
PASSWORD = creds['password']


### Browser Setup - Using Chrome in headless mode
# alternative: https://www.alexkras.com/running-chrome-and-other-browsers-in-almost-headless-mode/
CHROMEDRIVER = '/usr/bin/chromedriver'
options = webdriver.ChromeOptions()

# Specify your preferred version of Chrome
options.binary_location = '/usr/bin/chromium' 

# Default Headless Options - can comment out if you want to see it on screen
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=600,800")

# If you want to specify a particular home folder (otherwise will use temp)
# https://chromium.googlesource.com/chromium/src/+/master/docs/user_data_dir.md#Linux
options.add_argument('--user-data-dir={}/.config/chromium'.format(os.environ['HOME']))

# If you want to test the full process this is useful
# options.add_argument('--incognito')

service_args = []
service_log_path = './chromedriver.log'

# DEBUG - lots of info
# service_args = ['--verbose']

browser = webdriver.Chrome(CHROMEDRIVER,
                           chrome_options=options,
                           service_args=service_args,
                           service_log_path=service_log_path)


### Login
LOGIN_URL = 'https://www.schwab.com/public/schwab/nn/login/mobile-login.html&lang=en'
browser.get(LOGIN_URL)
browser.switch_to.frame('mobile-login')
username = browser.find_element_by_id('LoginId')
password = browser.find_element_by_id('Password')
username.send_keys(LOGIN)
password.send_keys(PASSWORD)
browser.find_element_by_id('RememberLoginId').click()
browser.find_element_by_id('Submit').click()

# Wait until login is done... (is AJAX login)
while  browser.current_url == LOGIN_URL:
  print('waiting...')
  time.sleep(0.1)


### 1st Time Browser Auth
if browser.current_url.startswith('https://lms.schwab.com/Sua/DeviceTag'):
  browser.find_element_by_id('SmsOptionText').click()
  browser.find_element_by_id('Submit').click()

  # Wait for SMS code
  PINCODE = input('Require SMS text code: ')

  # We should be on https://lms.schwab.com/Sua/DeviceTag/AccessCodeEntry
  pin = browser.find_element_by_id('PinNumber')
  pin.send_keys(PINCODE)
  browser.find_element_by_id('TrustDeviceCheckBox').click()
  browser.find_element_by_id('Submit').click()

  # Confirmation Page
  browser.find_element_by_id('Submit').click()


### Summary
'''
we might want to check cookies to see if we're succesfully logged in:
 (double-check url, will be redirected otherwise)
  AcctInfo
'''
print(browser.current_url)
# Wait for AJAX to load...
element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "lbl-account")))
browser.save_screenshot("summary.png")

### Quit
browser.quit()


'''
Useful screens:
https://client.schwab.com/MobileWeb/#accounts/summary
https://client.schwab.com/MobileWeb/#accounts/balances
https://client.schwab.com/MobileWeb/#accounts/positions
https://client.schwab.com/MobileWeb/#accounts/history
'''
