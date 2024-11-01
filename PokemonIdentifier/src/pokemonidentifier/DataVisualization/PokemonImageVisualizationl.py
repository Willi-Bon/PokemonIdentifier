import tkinter as tk
from tkinter import filedialog

import panel as pn  # Importing the Panel library for creating interactive dashboards
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os for interacting with the operating system
from PIL import Image  # Importing the Python Imaging Library for image processing
import numpy as np  # Importing numpy for numerical operations
import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import param  # Importing param for creating interactive widgets
from tqdm import tqdm  # Importing tqdm for progress bar

# IMAGE_FOLDER_PATH = r'C:\Users\willi\Documents\Drexel\Fall Quart 5\MEM 679 - Machine Learning\pokemon_images_subset (Testing Only)\combined_images'
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    return folder_selected
IMAGE_FOLDER_PATH = select_folder()

pn.extension()  # Initializing Panel extension

class PokemonDashboard(param.Parameterized):
    shiny_filter = param.ObjectSelector(default='All', objects=['All', 'Shiny', 'Normal'])
    gender_filter = param.ObjectSelector(default='All', objects=['All', 'Male & Female', 'Male', 'Female'])
    name_filter = param.String(default='', doc="Filter by name")
    location_filter = param.ObjectSelector(default='All', objects=['All'])

    def __init__(self, **params):
        super().__init__(**params)
        self.progress = pn.widgets.Progress(name='Initializing Dashboard', value=0, max=100, sizing_mode='stretch_width')
        self.image_data = self.load_images_with_metadata(IMAGE_FOLDER_PATH)
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

    def load_images_with_metadata(self, folder_path):
        image_data = []  # Initialize an empty list to store image data
        files = os.listdir(folder_path)
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
        ax3.set_ylabel('Area (Pixels Squared)')
        ax3.grid(True, axis='both')  # Add gridlines
        self.scatter_plot_pane.object = fig3  # Update the plot

    @param.depends('shiny_filter', 'gender_filter', 'name_filter', 'location_filter', watch=True)
    def update_dashboard(self):
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
        header = pn.pane.HTML(
            """
            <div style='background-color: maroon; color: white; padding: 10px; text-align: center; width: 100%;'>
                <h1>Pokémon Image Visualization Dashboard</h1>
                <p>This dashboard facilitates the visualization of the Pokemon Go Pokemon Identifier dataset. It shows statistics of the different classifiers of each image in the dataset.
                This dashboard also allows the visualization of images that meet user-inputted criterion.</p>
            </div>
            """,
            sizing_mode='stretch_width'
        )
        
        shiny_description = pn.pane.Markdown(
            """
            **Number of Shiny and Normal Pokémon Images**: 
            This bar plot shows the count of shiny and normal Pokémon images. \n
            Pokemon appearance changes whether or not it is "Shiny" or "Normal".\n 
            It is expected that there are an equal number of "Shiny" and "Normal" Pokémon images.
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
            **Average Color Intensity and Area of Pokémon Images**: 
            This scatter plot represents the average color intensity and area of each dataset image. Each point is colored based on the average color of the corresponding image.
            The x-axis represents the average color intensity (average of the average RGB values of the dataset image), and the y-axis represents the area (width * height) of the image.\n
            It is expected that there will be 3 clusters because there are 3 backgrounds in the dataset. Since the backgrounds make-up most of the image the average color intensity will be dominated by the backgrounds.
            """,
            width=300
        )
        
        filter_description = pn.pane.Markdown(
            """
            **Filter Options**: 
            Use the filters to narrow down the Pokémon images based on shiny status, gender, name, and location.
            (Note that location is essentially the background of the image. It represents where the Pokemon Go AR image would be taken in the real world)\n
            **Total Entries Displayed**: 
            Shows the number of images in dataset based on filter preferences.\n
            **Preview Images**:
            Displays all images that are currently meet filter prefences. 
            (Not recommended when large number of entries are displayed)
            
            """,
            width=300
        )
        
        return pn.Column(
            header,
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
        
        return {
            'filename': os.path.basename(image_path),
            'width': img.width,
            'height': img.height,
            'mode': img.mode,
            'mean_pixel_value': np.mean(img_array),
            'average_color': average_color
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
        'index': None,
        'location': location,
        'name': name,
        'shiny': shiny,
        'gender': gender
    }

dashboard = PokemonDashboard()
pn.serve(dashboard.view)
