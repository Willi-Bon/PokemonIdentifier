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
soup = BeautifulSoup(driver.page_source, "html.parser") #Extracts homepage

# Find all Pokémon links and extract data
pokemon_links = soup.find_all('a', class_='pokemon')
count = 0   #Begins a count that will be used to check which value pokemon code is on (useful to restart code if it crashes)
os.makedirs('pokemon_images', exist_ok=True)
for pokemon_link in pokemon_links:
    if count > 400: #If code crashes, start at last saved image.
                    #If first pass, set to -1
        #Get url to specific pokemon
        pokemon_url = pokemon_link['href']
        full_url = f"https://pokemon.gameinfo.io{pokemon_url}"
        

        # Navigate to the Pokémon's page
        driver.get(full_url)
        driver.implicitly_wait(60) #Driver waits a minute for page to load
        # Give the page time to load always
        time.sleep(2)

        # Extract data from the Pokémon's page
        pokemon_soup = BeautifulSoup(driver.page_source, "html.parser")
        # Example of extracting specific information, adjust selectors as necessary
        article = pokemon_soup.find('article', class_='images-block') #Relevant images are in this article
        if article: 
            images = article.find_all('img') #Pulls all images from article
            image_urls = [img['src'] for img in images] #Stors image url & Image name
            image_names = [img['alt'] for img in images]
            for i, img_url in enumerate(image_urls): #Saves each image in article (Male/Female & Normal/Shiny)
                response = requests.get(f'https:{img_url}')
                if response.status_code == 200:
                    # Save the image to the local directory
                    with open(f'pokemon_images/{image_names[i]}.png', 'wb') as f:
                        f.write(response.content)
                    print(f"Saved image for {image_names[i]}")
                    print(f'count: {count}') #Prints count to keep track in case of time-out error
                else:
                    print(f"Failed to download image for {image_names[i]}")

        else:
            print("Article with class 'images-block' not found.")
        driver.back()  # Go back to the main Pokémon page
        time.sleep(2)

    count += 1 #Increments count by 1

print(f'Total Pokémon processed: {count}') #Prints total number of Pokémon processed

# Close the browser
driver.quit()
