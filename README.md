Welcome to the PokemonIdentifier! This is a project for MEM 679, with the intention to create a machine learning model that can predict what Pokemon is featured in images taken using the Pokemon Go AR feature.
Below features updates based on the most recent homework submission and a general outline of what is contained in this repository.



/n**Homework 3**
Homework 3 visualizes the dataset that will be used. This uses a dashboard that has a graph depicting the number of Shiny or Normal Pokemon Images, the number of Pokemon images that depend on the Pokemon's gender, and a graph depicting the relationship between image size and average color intensity.
Additionally, the dashboard has an interactive table which allows filtering of dataset images based on different parameters. Based on inputted parameters, different previews of the images can be outputted.
To use this:
1. Install all packages in the 'requirements.txt' file in the docs folder.
2. Download the dataset from the following public outlook folder:
3. Run 'PokemonImageVisualization.py' in the src folder.
4. Upon running, select downloaded dataset folder.
5. Select whether dashboard should depict a subset of the dataset (500 images, takes about one minute) or the entire dataset (>5000 images takes about ten minutes).


 
 
 **Contents of the Repo**
 Currently two subsets of this project are in the repo. 
 The first is the Webscraper that was used to generate the dataset. This webscraper pulls pngs of each Pokemon (all forms including Shiny and Normal variants and Gender-based variants) from https://pokemon.gameinfo.io/
 These are then put into another script that overlays the pngs onto different backgrounds. This emulates the effect of Pokemon Go's AR feature which allows images of Pokemon to be taken in real world locations. Another script was then used to sanity check by outputting a csv that contains the names of all the Pokemon in the dataset.

 The second part of this project is the data visualization. This script creates a dashboard that depicts graphical information of the dataset. It also allows previewing of dataset images that meet user-inputted criterion.
 The data visualization allows visualization to be based on either a random subset of 500 images (for quick analysis) or based on the entire dataset (for accurate analysis)
