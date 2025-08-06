import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

from django.contrib.auth.models import User
from main.models import CustomerProfile, Appointment
from .factories import UserFactory, CustomerProfileFactory, ProviderProfileFactory, AppointmentFactory

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
        EC.presence_of_element_located((By.NAME, "view_appointments"))
    )

@pytest.mark.django_db
def test_homepage_login_and_signup(driver, live_server):
    driver.get(live_server.url)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
    )
    login_button.click()
    assert "Login" in driver.title

    driver.get(live_server.url)
    signup_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Signup"))
    )
    signup_button.click()
    assert "Sign Up" in driver.title

@pytest.mark.django_db
def test_login_to_customer_dashboard(driver, live_server, create_user):
    user = create_user
    login_and_reach_dashboard(driver, live_server, user)
    assert "Dashboard" in driver.title or "dashboard" in driver.current_url.lower()

@pytest.mark.django_db
def test_all_buttons_in_customer_dashboard(driver, live_server, create_user):
    user = create_user
    login_and_reach_dashboard(driver, live_server, user)

    driver.find_element(By.NAME, "view_appointments").click()
    WebDriverWait(driver, 10).until(EC.title_contains("View My Appointments"))
    assert "View My Appointments" in driver.title

    driver.back()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "view_providers"))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Providers')]"))
    )

    driver.back()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "my_profile"))
    ).click()
    WebDriverWait(driver, 10).until(EC.title_contains("My Profile"))
    assert "My Profile" in driver.title

    driver.back()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "booking_history"))
    ).click()
    WebDriverWait(driver, 10).until(EC.title_contains("Booking History"))
    assert "Booking History" in driver.title

@pytest.mark.django_db
def test_view_appointments_cancellation(driver, live_server, create_user):
    user = create_user
    appointment = AppointmentFactory(customer=user, status="pending")
    login_and_reach_dashboard(driver, live_server, user)

    driver.find_element(By.NAME, "view_appointments").click()
    WebDriverWait(driver, 10).until(
        EC.title_contains("View My Appointments")
    )

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "cancel"))
    ).click()

    time.sleep(2)
    appointment.refresh_from_db()
    assert appointment.status == "cancelled"



@pytest.mark.django_db
def test_provider_profile_creation(driver , live_server , create_user):
    user = create_user
    login_and_reach_dashboard(driver , live_server , user )
    driver.find_element(By.NAME , "provider_side").click()

    WebDriverWait(driver , 10).until(
        EC.title_contains("Create Your Profile")
    )
    Select(driver.find_element(By.ID, "id_service_category")).select_by_visible_text("Doctor")
    driver.find_element(By.ID, "id_service_name").send_keys("Doctorship")
    Select(driver.find_element(By.ID, "id_pricing_model")).select_by_visible_text("Hourly")
    driver.find_element(By.ID, "id_duration_mins").send_keys("30")
    driver.find_element(By.ID, "id_start_time").send_keys("09:00")
    driver.find_element(By.ID, "id_end_time").send_keys("18:00")
    driver.find_element(By.ID, "id_rate").send_keys("2000")
    driver.find_element(By.ID, "id_buffer").send_keys("10")
    submit_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "create_provider"))
)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
    time.sleep(0.5) 
    submit_button.click()
    
    print("Current title:", driver.title)
    WebDriverWait(driver, 10).until(
    EC.title_contains("Connect Calendar")
)
    assert driver.title == "Connect Calendar"



