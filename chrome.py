from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
options.add_argument("--start-maximized")  # Start browser maximized

# Automatically download and manage ChromeDriver
service = Service(ChromeDriverManager().install())

# Create a new Chrome browser instance
driver = webdriver.Chrome(service=service, options=options)

# Open a website
driver.get("https://www.google.com")

# Wait for the page to load completely
try:
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Page loaded successfully!")
except Exception as e:
    print(f"Timeout occurred: {e}")

# Print the page title
print(driver.title)

# Close the browser
driver.quit()
