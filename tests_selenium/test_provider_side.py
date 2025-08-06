import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from django.contrib.auth.models import User
from main.models import CustomerProfile, ProviderProfile
from .factories import UserFactory, CustomerProfileFactory, ProviderProfileFactory
import time 


@pytest.fixture(scope="session")
def chrome_options():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    return options


@pytest.fixture(scope="session")
def driver(chrome_options):
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture
def create_user(db):
    user = UserFactory()
    password = "password123"
    CustomerProfileFactory(user=user)
    ProviderProfileFactory(user=user, google_calendar_connected=True)
    return user


def login_and_reach_dashboard(driver, live_server, user):
    driver.get(live_server.url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(user.username)

    driver.find_element(By.NAME, "password").send_keys("password123", Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "view_pending_appointments"))
    )


@pytest.mark.parametrize("button_name, expected_title", [
    ("view_pending_appointments", "Pending Appointments"),
    ("view_my_appointments", "My Appointments"),
    ("my_profile", "My Profile"),
    ("view_analytics", "Analytics"),
    ("my_availability", "My Availability"),
    ("customer_side", "Customer Dashboard"),
])
def test_dashboard_redirects(driver, live_server, create_user, button_name, expected_title):
    user = create_user
    login_and_reach_dashboard(driver, live_server, user)

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, button_name))
    )

    # Scroll into view to prevent click interception
    driver.execute_script("arguments[0].scrollIntoView(true);", button)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, button_name))).click()

    WebDriverWait(driver, 10).until(
        EC.title_contains(expected_title)
    )

    assert expected_title in driver.title







def test_disconnect_google_calendar(driver, live_server, create_user):
    user = create_user
    login_and_reach_dashboard(driver, live_server, user)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "my_profile"))
    ).click()

    WebDriverWait(driver, 10).until(EC.title_contains("My Profile"))

    # Wait for the disconnect button to appear
    disconnect_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "disconnect"))
    )

    # Scroll into view properly (adjust scroll offset)
    driver.execute_script("""
        const element = arguments[0];
        const yOffset = -150;
        const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({top: y, behavior: 'smooth'});
    """, disconnect_button)


    time.sleep(1)

  
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "disconnect"))
    ).click()


    WebDriverWait(driver, 10).until(EC.title_is("Home Page"))

    # Re-fetch user from database to confirm disconnection
    check_user = User.objects.get(id=user.id)
    assert not check_user.providerprofile.google_calendar_connected




