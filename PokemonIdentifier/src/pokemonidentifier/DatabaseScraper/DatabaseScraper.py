from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import os

# Set up Firefox options
firefox_options = Options()
firefox_options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Update path here
firefox_options.add_argument("--headless")  # Optional: run in headless mode

# Set up GeckoDriver path
geckodriver_path = 'C:\\Users\\willi\\Downloads\\geckodriver-v0.35.0-win32\\geckodriver.exe'
service = Service(geckodriver_path)

# Initialize Firefox driver with specified binary and options
driver = webdriver.Firefox(service=service, options=firefox_options)

# Navigate to the URL
url = 'https://pokemon.gameinfo.io/'
driver.get(url)

# Extract page content with BeautifulSoup
from bs4 import BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find all Pokémon links and extract data
pokemon_links = soup.find_all('a', class_='pokemon')
count = 0
for pokemon_link in pokemon_links:
    count += 1
    name = pokemon_link['data-name']  # Extracting from data attribute
    print(f"Name: {name}")

print(f'Total Pokémon processed: {count}')

# Close the browser
driver.quit()
