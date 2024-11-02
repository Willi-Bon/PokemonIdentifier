import os
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import random

import panel as pn  # Importing the Panel library for creating interactive dashboards
import pandas as pd  # Importing pandas for data manipulation and analysis
from PIL import Image  # Importing the Python Imaging Library for image processing
import numpy as np  # Importing numpy for numerical operations
import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import param  # Importing param for creating interactive widgets
from tqdm import tqdm  # Importing tqdm for progress bar
from matplotlib.ticker import MaxNLocator  # Importing MaxNLocator for integer y-axis

def select_folder():
    """
    Opens a dialog to select a folder.

    Returns:
        str: The path to the selected folder.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    return folder_selected

def prompt_subset_choice():
    """
    Prompts the user to choose between using a random subset of 500 images or the entire dataset.

    Returns:
        bool: True if the user chooses to use a random subset, False otherwise.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    choice = messagebox.askyesno("Subset Choice", "Do you want to use a random subset of 500 images?\n(Selecting 'No' will load all images in the dataset)")
    return choice

class PokemonDashboard(param.Parameterized):
    """
    A dashboard for visualizing Pokémon images.

    Attributes:
        shiny_filter (param.ObjectSelector): Filter for shiny status.
        gender_filter (param.ObjectSelector): Filter for gender.
        name_filter (param.String): Filter for Pokémon name.
        location_filter (param.ObjectSelector): Filter for location.
    """
    shiny_filter = param.ObjectSelector(default='All', objects=['All', 'Shiny', 'Normal'])
    gender_filter = param.ObjectSelector(default='All', objects=['All', 'Male & Female', 'Male', 'Female'])
    name_filter = param.String(default='', doc="Filter by name")
    location_filter = param.ObjectSelector(default='All', objects=['All'])

    def __init__(self, **params):
        """
        Initializes the dashboard.

        Args:
            **params: Additional parameters for the dashboard.
        """
        super().__init__(**params)
        self.progress = pn.widgets.Progress(name='Initializing Dashboard', value=0, max=100, sizing_mode='stretch_width')
        self.image_data = self.load_images_with_metadata(IMAGE_FOLDER_PATH, USE_SUBSET)
        self.filtered_data = self.image_data.copy()
        self.data_table = pn.widgets.Tabulator(self.filtered_data, name='Image Data', sizing_mode='stretch_width', height=400)
        self.entry_counter = pn.pane.Markdown(f"<div style='font-size: 32px; font-weight: bold;'>Total Displayed Entries: {len(self.filtered_data)}</div>")
        self.preview_button = pn.widgets.Button(name='Preview Images', button_type='primary')
        self.image_gallery = pn.Row()  # Pane to display the images in a row
        self.shiny_plot_pane = pn.pane.Matplotlib()
        self.gender_plot_pane = pn.pane.Matplotlib()
        self.scatter_plot_pane = pn.pane.Matplotlib()
        self.param.location_filter.objects = ['All'] + sorted(self.image_data['location'].unique().tolist())
        self.create_static_graphs()
        self.update_dashboard()

        # Add a callback to update the image gallery when the button is pressed
        self.preview_button.on_click(self.update_image_gallery)

    def load_images_with_metadata(self, folder_path, use_subset):
        """
        Loads images and their metadata from the specified folder.

        Args:
            folder_path (str): The path to the folder containing the images.
            use_subset (bool): Whether to use a random subset of 500 images.

        Returns:
            pd.DataFrame: A DataFrame containing the image metadata.
        """
        image_data = []  # Initialize an empty list to store image data
        files = os.listdir(folder_path)
        if use_subset:
            files = random.sample(files, min(500, len(files)))  # Select a random subset of 500 images
        total_files = len(files)
        for idx, file_name in enumerate(tqdm(files, desc="Loading Images")):  # Iterate over all files in the folder
            if file_name.endswith('.png'):  # Check if the file is a PNG image
                image_path = os.path.join(folder_path, file_name)  # Get the full path of the image
                image_info = get_image_data(image_path)  # Get the image data
                metadata = parse_filename(file_name)  # Parse the filename for metadata
                metadata['index'] = idx  # Set the index
                image_info.update(metadata)  # Merge the image data with the metadata
                image_data.append(image_info)  # Append the combined data to the list
            self.progress.value = int((idx + 1) / total_files * 100)  # Update progress bar
        df = pd.DataFrame(image_data)  # Convert the list to a pandas DataFrame
        df = df[['filename', 'name', 'location', 'shiny', 'gender', 'average_color', 'width', 'height', 'mean_pixel_value']]  # Reorder columns
        return df

    def create_static_graphs(self):
        """
        Creates static graphs for the dashboard.
        """
        # Create a bar plot for the number of "Shiny" and "Normal" Pokémon images
        shiny_counts = self.image_data['shiny'].value_counts()
        fig, ax = plt.subplots()
        shiny_counts.plot(kind='bar', ax=ax, color=['gray', 'orange'])
        ax.set_title('Number of Shiny and Normal Pokémon Images')
        ax.set_xlabel('Shiny Status')
        ax.set_ylabel('Count')
        ax.set_xticklabels(shiny_counts.index, rotation=0)  # Set text horizontal
        ax.grid(True, axis='y')  # Add horizontal gridlines only
        self.shiny_plot_pane.object = fig  # Update the plot

        # Create a bar plot for the number of "Male & Female", "Male", and "Female" Pokémon images
        gender_counts = self.image_data['gender'].value_counts()
        fig2, ax2 = plt.subplots()
        gender_counts.plot(kind='bar', ax=ax2, color=['purple', 'blue', 'red'])
        ax2.set_title('Distinct Pokemon Forms Based on Gender')
        ax2.set_xlabel('Gender')
        ax2.set_ylabel('Count')
        ax2.set_xticklabels(gender_counts.index, rotation=0)  # Set text horizontal
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))  # Ensure y-axis shows only integers
        ax2.grid(True, axis='y')  # Add horizontal gridlines only
        self.gender_plot_pane.object = fig2  # Update the plot

        # Create a scatter plot for the average color intensity and area of each image
        fig3, ax3 = plt.subplots()
        for _, row in self.image_data.iterrows():
            mean_pixel_value = row['mean_pixel_value']
            area = row['width'] * row['height']
            ax3.scatter(mean_pixel_value, area, color=[c / 255.0 for c in row['average_color']], s=100)
        ax3.set_title('Scatter Plot of Average Color Intensity and Area of Pokémon Images')
        ax3.set_xlabel('Average Color Intensity')
        ax3.set_ylabel('Area (Width x Height)')
        ax3.grid(True, axis='both')  # Add gridlines
        self.scatter_plot_pane.object = fig3  # Update the plot

    @param.depends('shiny_filter', 'gender_filter', 'name_filter', 'location_filter', watch=True)
    def update_dashboard(self):
        """
        Updates the dashboard based on the selected filters.
        """
        self.filtered_data = self.image_data.copy()
        if self.shiny_filter != 'All':
            self.filtered_data = self.filtered_data[self.filtered_data['shiny'] == self.shiny_filter]
        if self.gender_filter != 'All':
            self.filtered_data = self.filtered_data[self.filtered_data['gender'] == self.gender_filter]
        if self.name_filter:
            self.filtered_data = self.filtered_data[self.filtered_data['name'].str.contains(self.name_filter, case=False)]
        if self.location_filter != 'All':
            self.filtered_data = self.filtered_data[self.filtered_data['location'] == self.location_filter]
        self.data_table.value = self.filtered_data
        self.entry_counter.object = f"<div style='font-size: 32px; font-weight: bold;'>Total Entries Displayed: {len(self.filtered_data)}</div>"

    def update_image_gallery(self, event):
        """
        Updates the image gallery based on the filtered data.

        Args:
            event: The event that triggered the update.
        """
        self.image_gallery.clear()  # Clear the current gallery
        images = []
        for _, row in self.filtered_data.iterrows():
            image_path = os.path.join(IMAGE_FOLDER_PATH, row['filename'])
            images.append(pn.Column(
                pn.pane.PNG(image_path, width=300, height=300),
                pn.pane.Markdown(f"<div style='text-align: center; margin-top: -10px;'>{row['filename']}</div>", width=300)
            ))
        self.image_gallery.extend(images)

    def view(self):
        """
        Creates the layout for the dashboard.

        Returns:
            pn.Column: The layout of the dashboard.
        """
        header = pn.pane.HTML(
            """
            <div style='background-color: maroon; color: white; padding: 10px; text-align: center; width: 100%;'>
                <h1>Pokémon Image Visualization Dashboard</h1>
                <p>This dashboard allows you to filter and visualize Pokémon images based on various criteria.</p>
            </div>
            """,
            sizing_mode='stretch_width'
        )
        
        instructions = pn.pane.Markdown(
            """
            ## Welcome!
            \nThis dashboard visualizes the dataset that will be used to train a machine learning model to predict what Pokemon is in an image from Pokemon Go.
            The dataset was created by scraping png images from https://pokemon.gameinfo.io/ and overlaying them onto different backgrounds.
            This manufactures the types of pictures that are taken in the AR feature of Pokemon Go, where players take pictures of there Pokemon in the real world.
            Each image in the dataset contains a Pokemon superimposed on a background, the name of the Pokemon, whether it is "Shiny" or "Normal" (Shiny Pokemon are rarer variants of Pokemon), and if the featured Pokemon is a Male or Female variant of the Pokemon species.
            \nFeatured in this dashboard are the following visualizations:
            -How many "Shiny" and "Normal" Pokemon images are in the dataset.
            -How many Pokemon have different Male or Female appearances
            -What average color intensity are in the images
            \nAdditionally, a table is provided to allow more fine-tuned examination of images in the dataset.
            Based on inputted filters, a table will display data based on images that meet given criteria.
            Then, all images that meet inputted criterion will have the option to be displayed. 
            """,
            width=800
        )
        
        shiny_description = pn.pane.Markdown(
            """
            **Number of Shiny and Normal Pokémon Images**: 
            This bar plot shows the count of shiny and normal Pokémon images. \n
            Pokemon appearance changes whether or not it is "Shiny" or "Normal".\n 
            It is expected that there are roughly the same number of "Shiny" and "Normal" Pokémon images.
            """,
            width=300
        )
        
        gender_description = pn.pane.Markdown(
            """
            **Distinct Pokémon Forms Based on Gender**: 
            This bar plot displays the number of distinct Pokémon Images categorized by gender.\n
            Some Pokemon look different if they are Female or Male. Pokemon images that do not differ based on Pokemon gender are labeled as "Male & Female".\n
            It is expected that there are significantly more Pokemon images that do not depend on the featured Pokemon's gender. Additionally, Pokemon images that feature a Male-exclusive and Female-exclusive counts are expected to be roughly equal.
            """,
            width=300
        )
        
        scatter_description = pn.pane.Markdown(
            """
            **Scatter Plot of Average Color Intensity and Area of Pokémon Images**: 
            This scatter plot represents the average color intensity and area of each Pokémon image. Each point is colored based on the average color of the corresponding image.\n
            The x-axis represents the average color intensity, and the y-axis represents the area (width times height) of the image.\n
            Average color intensity is calculated by taking the mean value of the pixels in the image.\n 
            It is expected that the points will be in three groups because the colors of the images are dominated by the colors of the backgrounds. This is due to the Pokemon only taking up the bottom third of the image, causing the mean color to be dominated by the backgrounds. 
            Additionally, since the three backgrounds are of different sizes, the area of the image will correspond to the different colors of the backgrounds.
            """,
            width=300
        )
        
        filter_description = pn.pane.Markdown(
            """
            **Filter Options**: 
            Use the filters to narrow down the Pokémon images based on shiny status, gender, name, and location (background).\n
            **Total Entries Displayed**: 
            Shows the number of images in dataset based on filter preferences.\n
            **Preview Images**:
            Displays all images that are currently meet filter prefences. 
            (**Not recommended when large number of entries are displayed**)\n
            **Displayed Information**:
            Table below will display the following information for each image:
            -Filename
            -Name of Pokemon
            Background of Image
            -If Shiny or Normal variant featured in image
            -If Gender specific variant featured in image
            -Average Color of Image (R, G, B, Opacity)
            -Width and Height of Image (in pixels)
            -Mean_Pixel_Value (Average Color Intensity of Image)            
            """,
            width=300
        )
        
        return pn.Column(
            header,
            instructions,
            self.progress,
            pn.Row(
                self.shiny_plot_pane,
                shiny_description
            ),
            pn.Row(
                self.gender_plot_pane,
                gender_description
            ),
            pn.Row(
                self.scatter_plot_pane,
                scatter_description
            ),
            pn.Row(
                pn.Column(
                    pn.Param(self.param, widgets={
                        'shiny_filter': pn.widgets.Select,
                        'gender_filter': pn.widgets.Select,
                        'name_filter': pn.widgets.TextInput,
                        'location_filter': pn.widgets.Select
                    }),
                    self.entry_counter,
                    self.preview_button,
                ),
                filter_description
            ),
            pn.Column(
                pn.Row(self.image_gallery, sizing_mode='stretch_width'),
                sizing_mode='stretch_width', scroll=True, height=400
            ),  # Enable horizontal scrolling
            self.data_table
        )

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
        mean_pixel_value = np.mean(img_array)  # Calculate the mean pixel value
        
        return {
            'filename': os.path.basename(image_path),
            'width': img.width,
            'height': img.height,
            'mode': img.mode,
            'mean_pixel_value': mean_pixel_value,
            'average_color': average_color
        }

def parse_filename(filename):
    """
    Parses the filename to extract metadata.

    Args:
        filename (str): The name of the image file.

    Returns:
        dict: A dictionary containing the following keys:
            - 'index' (int): The index of the image.
            - 'location' (str): The location of the image.
            - 'name' (str): The name of the Pokémon.
            - 'shiny' (str): The shiny status of the Pokémon.
            - 'gender' (str): The gender of the Pokémon.
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
        'index': None,
        'location': location,
        'name': name,
        'shiny': shiny,
        'gender': gender
    }

if __name__ == "__main__":
    # Select the folder containing the images
    IMAGE_FOLDER_PATH = select_folder()
    # Prompt the user to choose between using a random subset or the entire dataset
    USE_SUBSET = prompt_subset_choice()

    # Initialize Panel extension
    pn.extension()

    # Create and serve the dashboard
    dashboard = PokemonDashboard()
    pn.serve(dashboard.view)
