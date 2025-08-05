import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.contrib.auth import get_user_model
from .factories import UserFactory, ProviderProfileFactory, CustomerProfileFactory, AppointmentFactory , NotificationPreferencesFactory  # adjust these imports

@pytest.fixture(scope="session")
def chrome_options():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return options

@pytest.fixture(scope="session")
def driver(chrome_options):
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()