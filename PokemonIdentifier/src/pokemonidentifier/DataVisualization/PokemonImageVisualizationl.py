import panel as pn  # Importing the Panel library for creating interactive dashboards
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os for interacting with the operating system
from PIL import Image  # Importing the Python Imaging Library for image processing
import numpy as np  # Importing numpy for numerical operations
import matplotlib.pyplot as plt  # Importing matplotlib for plotting

pn.extension()  # Initializing Panel extension

IMAGE_FOLDER_PATH = r'C:\Users\willi\Documents\Drexel\Fall Quart 5\MEM 679 - Machine Learning\pokemon_images_subset (Testing Only)\combined_images'

def get_image_data(image_path):
    """
    Extracts and returns metadata and statistical information from an image file.

    Args:
        image_path (str): The file path to the image.

    Returns:
        dict: A dictionary containing the following keys:
            - 'filename' (str): The name of the image file.
            - 'width' (int): The width of the image in pixels.
            - 'height' (int): The height of the image in pixels.
            - 'mode' (str): The mode of the image (e.g., 'RGB', 'L').
            - 'mean_pixel_value' (float): The mean value of the pixels in the image.
            - 'average_color' (tuple): The average color of the image as an (R, G, B) tuple.
    """
    with Image.open(image_path) as img:  # Open the image file
        img_array = np.array(img)  # Convert the image to a numpy array
        average_color = tuple(np.mean(img_array, axis=(0, 1)).astype(int))  # Calculate the average color
        return {
            'filename': os.path.basename(image_path),  # Get the filename
            'width': img.width,  # Get the width of the image
            'height': img.height,  # Get the height of the image
            'mode': img.mode,  # Get the mode of the image
            'mean_pixel_value': np.mean(img_array),  # Calculate the mean pixel value
            'average_color': average_color  # Get the average color
        }

def parse_filename(filename):
    parts = filename.replace('.png', '').split(' ')
    location_name = parts[0]
    shiny = 'Shiny' if 'Shiny' in parts else 'Normal'
    gender = 'Unknown'
    if 'Male & Female' in filename:
        gender = 'Male & Female'
    elif 'Male' in filename:
        gender = 'Male'
    elif 'Female' in filename:
        gender = 'Female'
    
    location, name = location_name.split('_', 1)
    
    return {
        'index': None,  # Placeholder for index, to be set later
        'location': location,
        'name': name,
        'shiny': shiny,
        'gender': gender
    }

def load_images_with_metadata(folder_path):
    image_data = []  # Initialize an empty list to store image data
    for idx, file_name in enumerate(os.listdir(folder_path)):  # Iterate over all files in the folder
        if file_name.endswith('.png'):  # Check if the file is a PNG image
            image_path = os.path.join(folder_path, file_name)  # Get the full path of the image
            image_info = get_image_data(image_path)  # Get the image data
            metadata = parse_filename(file_name)  # Parse the filename for metadata
            metadata['index'] = idx  # Set the index
            image_info.update(metadata)  # Merge the image data with the metadata
            image_data.append(image_info)  # Append the combined data to the list
    return pd.DataFrame(image_data)  # Convert the list to a pandas DataFrame

def update_dashboard():
    image_data = load_images_with_metadata(IMAGE_FOLDER_PATH)  # Load the images with metadata from the constant folder path
    data_table.value = image_data  # Update the data table with the image data
    
    # Create a bar plot for the number of "Shiny" and "Normal" Pokémon images
    shiny_counts = image_data['shiny'].value_counts()
    fig, ax = plt.subplots()
    shiny_counts.plot(kind='bar', ax=ax, color=['blue', 'orange'])
    ax.set_title('Number of Shiny and Normal Pokémon Images')
    ax.set_xlabel('Shiny Status')
    ax.set_ylabel('Count')
    ax.set_xticklabels(shiny_counts.index, rotation=0)  # Set text horizontal
    ax.grid(True, axis='y')  # Add horizontal gridlines only
    
    shiny_plot_pane.object = fig  # Update the plot

    # Create a bar plot for the number of "Male & Female", "Male", and "Female" Pokémon images
    gender_counts = image_data['gender'].value_counts()
    fig2, ax2 = plt.subplots()
    gender_counts.plot(kind='bar', ax=ax2, color=['green', 'red', 'purple'])
    ax2.set_title('Number of Male & Female, Male, and Female Pokémon Images')
    ax2.set_xlabel('Gender')
    ax2.set_ylabel('Count')
    ax2.set_xticklabels(gender_counts.index, rotation=0)  # Set text horizontal
    ax2.grid(True, axis='y')  # Add horizontal gridlines only
    
    gender_plot_pane.object = fig2  # Update the plot

    # Create a scatter plot for the average color of each image
    fig3, ax3 = plt.subplots()
    for idx, row in image_data.iterrows():
        normalized_color = [c / 255.0 for c in row['average_color']]  # Normalize the color values to 0-1 range
        ax3.scatter(idx, 1, color=[normalized_color], s=100)  # Plot each image with its average color
    ax3.set_title('Average Color of Each Pokémon Image')
    ax3.set_xlabel('Image Index')
    ax3.set_yticks([])  # Remove y-axis ticks
    ax3.grid(True, axis='x')  # Add vertical gridlines only
    
    color_plot_pane.object = fig3  # Update the plot

data_table = pn.widgets.DataFrame(name='Image Data')  # Create a data table widget to display the image data
shiny_plot_pane = pn.pane.Matplotlib()  # Create a pane for the shiny plot
gender_plot_pane = pn.pane.Matplotlib()  # Create a pane for the gender plot
color_plot_pane = pn.pane.Matplotlib()  # Create a pane for the color plot

dashboard = pn.Column(data_table, shiny_plot_pane, gender_plot_pane, color_plot_pane)  # Create a dashboard layout with the widgets
dashboard.servable()  # Make the dashboard servable

update_dashboard()  # Automatically load images when the script runs

pn.serve(dashboard)
