import panel as pn  # Importing the Panel library for creating interactive dashboards
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os for interacting with the operating system
from PIL import Image  # Importing the Python Imaging Library for image processing
import numpy as np  # Importing numpy for numerical operations
import matplotlib.pyplot as plt  # Importing matplotlib for plotting
import param  # Importing param for creating interactive widgets

pn.extension()  # Initializing Panel extension

IMAGE_FOLDER_PATH = r'C:\Users\willi\Documents\Drexel\Fall Quart 5\MEM 679 - Machine Learning\pokemon_images_subset (Testing Only)\combined_images'

class PokemonDashboard(param.Parameterized):
    shiny_filter = param.ObjectSelector(default='All', objects=['All', 'Shiny', 'Normal'])
    gender_filter = param.ObjectSelector(default='All', objects=['All', 'Male & Female', 'Male', 'Female'])
    name_filter = param.String(default='', doc="Filter by name")
    location_filter = param.ObjectSelector(default='All', objects=['All'])

    def __init__(self, **params):
        super().__init__(**params)
        self.image_data = load_images_with_metadata(IMAGE_FOLDER_PATH)
        self.filtered_data = self.image_data.copy()
        self.data_table = pn.widgets.Tabulator(self.filtered_data.drop(columns=['width', 'height', 'mode', 'index']), name='Image Data', sizing_mode='stretch_width', height=400)
        self.entry_counter = pn.pane.Markdown(f"<div style='font-size: 32px; font-weight: bold;'>Total Entries: {len(self.filtered_data)}</div>")
        self.shiny_plot_pane = pn.pane.Matplotlib()
        self.gender_plot_pane = pn.pane.Matplotlib()
        self.color_plot_pane = pn.pane.Matplotlib()
        self.param.location_filter.objects = ['All'] + sorted(self.image_data['location'].unique().tolist())
        self.update_dashboard()

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
        self.data_table.value = self.filtered_data.drop(columns=['width', 'height', 'mode', 'index'])
        self.entry_counter.object = f"<div style='font-size: 32px; font-weight: bold;'>Total Entries: {len(self.filtered_data)}</div>"

        # Create a bar plot for the number of "Shiny" and "Normal" Pokémon images
        shiny_counts = self.filtered_data['shiny'].value_counts()
        fig, ax = plt.subplots()
        shiny_counts.plot(kind='bar', ax=ax, color=['gray', 'orange'])
        ax.set_title('Number of Shiny and Normal Pokémon Images')
        ax.set_xlabel('Shiny Status')
        ax.set_ylabel('Count')
        ax.set_xticklabels(shiny_counts.index, rotation=0)  # Set text horizontal
        ax.grid(True, axis='y')  # Add horizontal gridlines only
        self.shiny_plot_pane.object = fig  # Update the plot

        # Create a bar plot for the number of "Male & Female", "Male", and "Female" Pokémon images
        gender_counts = self.filtered_data['gender'].value_counts()
        fig2, ax2 = plt.subplots()
        gender_counts.plot(kind='bar', ax=ax2, color=['purple', 'blue', 'red'])
        ax2.set_title('Distinct Pokemon Forms Based on Gender')
        ax2.set_xlabel('Gender')
        ax2.set_ylabel('Count')
        ax2.set_xticklabels(gender_counts.index, rotation=0)  # Set text horizontal
        ax2.grid(True, axis='y')  # Add horizontal gridlines only
        self.gender_plot_pane.object = fig2  # Update the plot

        # Create a histogram for the average color intensity of each image
        mean_colors = [np.mean(row['average_color']) for _, row in self.filtered_data.iterrows()]
        fig3, ax3 = plt.subplots()
        n, bins, patches = ax3.hist(mean_colors, bins=30, edgecolor='black')
        for patch, row in zip(patches, self.filtered_data.iterrows()):
            normalized_color = [c / 255.0 for c in row[1]['average_color']]
            patch.set_facecolor(normalized_color)
        ax3.set_title('Histogram of Average Color Intensity of Pokémon Images')
        ax3.set_xlabel('Mean Color Intensity')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, axis='y')  # Add horizontal gridlines only
        self.color_plot_pane.object = fig3  # Update the plot

    def view(self):
        return pn.Column(
            pn.Row(
                pn.Column(
                    pn.Param(self.param, widgets={
                        'shiny_filter': pn.widgets.Select,
                        'gender_filter': pn.widgets.Select,
                        'name_filter': pn.widgets.TextInput,
                        'location_filter': pn.widgets.Select
                    }),
                    self.entry_counter,
                ),
            ),
            self.data_table,
            self.shiny_plot_pane,
            self.gender_plot_pane,
            self.color_plot_pane
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
            - 'average_color_portion' (tuple): The average color of the specified portion of the image as an (R, G, B) tuple.
    """
    with Image.open(image_path) as img:  # Open the image file
        img_array = np.array(img)  # Convert the image to a numpy array
        average_color = tuple(np.mean(img_array, axis=(0, 1)).astype(int))  # Calculate the average color
        
        # Calculate the average color for the specified portion (row 5, column 3 in a 5x5 grid)
        height, width, _ = img_array.shape
        portion = img_array[4*height//5:5*height//5, 2*width//5:3*width//5]
        average_color_portion = tuple(np.mean(portion, axis=(0, 1)).astype(int))
        
        return {
            'filename': os.path.basename(image_path),  # Get the filename
            'width': img.width,  # Get the width of the image
            'height': img.height,  # Get the height of the image
            'mode': img.mode,  # Get the mode of the image
            'mean_pixel_value': np.mean(img_array),  # Calculate the mean pixel value
            'average_color': average_color,  # Get the average color
            'average_color_portion': average_color_portion  # Get the average color of the specified portion
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

dashboard = PokemonDashboard()
pn.serve(dashboard.view)
