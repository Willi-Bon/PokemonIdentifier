from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
from bs4 import BeautifulSoup
import requests
import os

# Set up Firefox options
firefox_options = Options()
####THIS IS DEPENDENT ON PERSONAL COMPUTER PREFERENCES####
firefox_options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Update path here
#firefox_options.add_argument("--headless")  # Optional: run in headless mode

# Set up GeckoDriver path
####THIS IS DEPENDENT ON PERSONAL COMPUTER PREFERENCES####
geckodriver_path = 'C:\\Users\\willi\\Downloads\\geckodriver-v0.35.0-win32\\geckodriver.exe'
service = Service(geckodriver_path)

# Initialize Firefox driver with specified binary and options
driver = webdriver.Firefox(service=service, options=firefox_options)

# Navigate to the URL
url = 'https://pokemon.gameinfo.io/'
driver.get(url)

# Extract page content with BeautifulSoup
page_content = driver.page_source
soup = BeautifulSoup(page_content, 'html.parser')

def scrape_pokemon_data():
    """
    Scrapes Pokémon data from the specified URL.

    This function uses Selenium to navigate to the Pokémon GameInfo website,
    extracts the page content using BeautifulSoup, and processes the data.

    Returns:
        list: A list of dictionaries containing Pokémon data.
    """
    # List to store Pokémon data
    pokemon_data = []

    # Find all Pokémon entries on the page
    pokemon_entries = soup.find_all('div', class_='pokemon-entry')

    for entry in pokemon_entries:
        # Extract Pokémon name
        name = entry.find('h3').text.strip()

        # Extract Pokémon type(s)
        types = [type_tag.text.strip() for type_tag in entry.find_all('span', class_='type')]

        # Extract Pokémon image URL
        image_url = entry.find('img')['src']

        # Append data to the list
        pokemon_data.append({
            'name': name,
            'types': types,
            'image_url': image_url
        })

    return pokemon_data

def save_pokemon_data(data, filename='pokemon_data.json'):
    """
    Saves Pokémon data to a JSON file.

    Args:
        data (list): A list of dictionaries containing Pokémon data.
        filename (str): The name of the file to save the data to.
    """
    import json

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    # Scrape Pokémon data
    data = scrape_pokemon_data()

    # Save the data to a JSON file
    save_pokemon_data(data)

    # Close the browser
    driver.quit()
