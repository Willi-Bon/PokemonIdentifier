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
firefox_options.add_argument("--headless")  # Optional: run in headless mode

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
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find all Pokémon links and extract data
pokemon_links = soup.find_all('a', class_='pokemon')
count = 0
os.makedirs('pokemon_images', exist_ok=True)
for pokemon_link in pokemon_links:
    #Get url to specific pokemon
    pokemon_url = pokemon_link['href']
    full_url = f"https://pokemon.gameinfo.io{pokemon_url}"
    

    # Navigate to the Pokémon's page
    driver.get(full_url)
    # Give the page time to load (adjust the time as necessary)
    time.sleep(2)

    # Extract data from the Pokémon's page
    pokemon_soup = BeautifulSoup(driver.page_source, "html.parser")
    # Example of extracting specific information, adjust selectors as necessary
    article = pokemon_soup.find('article', class_='images-block')
    if article: 
        images = article.find_all('img')
        image_urls = [img['src'] for img in images]
        image_names = [img['alt'] for img in images]
        for i, img_url in enumerate(image_urls):
            #print(img_url)
            #print(image_names[i])

            response = requests.get(f'https:{img_url}')
            if response.status_code == 200:
                # Save the image to the local directory
                with open(f'pokemon_images/{image_names[i]}.png', 'wb') as f:
                    f.write(response.content)
                print(f"Saved image for {image_names[i]}")
            else:
                print(f"Failed to download image for {image_names[i]}")

    else:
        print("Article with class 'images-block' not found.")
    driver.back()  # Go back to the main Pokémon page
    time.sleep(2)

    count += 1

print(f'Total Pokémon processed: {count}')

# Close the browser
driver.quit()
