"""
Environment for Behave Testing
"""
import os
from behave import *
from selenium import webdriver
from service.service import get_apikey_for_behave

WAIT_SECONDS = 120
BASE_URL = os.getenv('BASE_URL', 'http://nyu-product-service-f19-dev.mybluemix.net/')

def before_all(context):
    """ Executed once before all tests """
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized") # open Browser in maximized mode
    options.add_argument("disable-infobars") # disabling infobars
    options.add_argument("--disable-extensions") # disabling extensions
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--headless")
    context.driver = webdriver.Chrome(chrome_options=options)
    # context.driver.manage().timeouts().pageLoadTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    # context.driver.manage().timeouts().setScriptTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    context.driver.implicitly_wait(WAIT_SECONDS) # seconds
    # context.driver.set_window_size(1120, 550)
    context.base_url = BASE_URL
    context.API_KEY = get_apikey_for_behave()

