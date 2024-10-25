import requests
from bs4 import BeautifulSoup

url = 'https://pokemon.gameinfo.io/' #URL of PokemonGO list of Pokemon
response = requests.get(url)

if response.status_code == 200:
    page_content = response.content
    
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the <a> tag with the Pokémon data
    pokemon_links = soup.find_all('a', class_='pokemon')

    # Extract the desired data
    count = 0
    for pokemon_link in pokemon_links:
        count += 1
        name = pokemon_link['data-name']  # Extracting from data attribute
        
        #english_name = pokemon_link['data-name-en']  # Extracting English name
        #image_src = pokemon_link.find('img')['src']  # Extracting image source
        #pokemon_id = pokemon_link.find('div', class_='id').text  # Extracting ID

        #pokemon_type = pokemon_link.find('div', class_='type').text  # Extracting Pokémon type
        # Print the extracted data
        print(f"Name: {name}")
        #print(f"English Name: {english_name}")
        #print(f"Image Source: {image_src}")
        #print(f"ID: {pokemon_id}")
        #print(f"Type: {pokemon_type}")
        #print("-" * 20)  # Separator for readability
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    print(response.content)

print(f'Total Pkmn {count}')