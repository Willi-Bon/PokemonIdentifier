import panel as pn  # Importing the Panel library for creating interactive dashboards
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os for interacting with the operating system
from PIL import Image  # Importing the Python Imaging Library for image processing
import numpy as np  # Importing numpy for numerical operations

pn.extension()  # Initializing Panel extension

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

def load_images(folder_path):
    image_data = []  # Initialize an empty list to store image data
    for file_name in os.listdir(folder_path):  # Iterate over all files in the folder
        if file_name.endswith('.png'):  # Check if the file is a PNG image
            image_path = os.path.join(folder_path, file_name)  # Get the full path of the image
            image_data.append(get_image_data(image_path))  # Append the image data to the list
    return pd.DataFrame(image_data)  # Convert the list to a pandas DataFrame

def update_dashboard(event):
    folder_path = folder_selector.value  # Get the folder path from the text input
    if os.path.isdir(folder_path):  # Check if the folder path is valid
        image_data = load_images(folder_path)  # Load the images from the folder
        data_table.value = image_data  # Update the data table with the image data

def parse_filename(filename):
    """
    Parses the filename to extract location, name, shiny status, and gender.

    Args:
        filename (str): The name of the image file.

    Returns:
        dict: A dictionary containing the following keys:
            - 'index' (int): An arbitrary index for the image.
            - 'location' (str): The location extracted from the filename.
            - 'name' (str): The name extracted from the filename.
            - 'shiny' (str): The shiny status ('Shiny' or 'Normal').
            - 'gender' (str): The gender extracted from the filename.
    """
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

def update_dashboard(event):
    folder_path = folder_selector.value  # Get the folder path from the text input
    if os.path.isdir(folder_path):  # Check if the folder path is valid
        image_data = load_images_with_metadata(folder_path)  # Load the images with metadata from the folder
        data_table.value = image_data  # Update the data table with the image data


folder_selector = pn.widgets.TextInput(name='Folder Path', placeholder='Enter folder path containing PNG images')  # Create a text input widget for the folder path
load_button = pn.widgets.Button(name='Load Images', button_type='primary')  # Create a button widget to load images
load_button.on_click(update_dashboard)  # Set the button click event to call the update_dashboard function

data_table = pn.widgets.DataFrame(name='Image Data')  # Create a data table widget to display the image data

dashboard = pn.Column(folder_selector, load_button, data_table)  # Create a dashboard layout with the widgets
dashboard.servable()  # Make the dashboard servable

pn.serve(dashboard)
