import os
import csv
import tkinter as tk
from tkinter import filedialog

def extract_name(filename):
    # Split the filename by spaces and take the first part as the name
    name = filename.split(' ')[0]
    return name

def get_unique_names_from_png_files(folder_path):
    # Initialize an empty set to store unique names
    unique_names = set()
    
    # Iterate over all files in the specified folder
    for filename in os.listdir(folder_path):
        # Check if the file has a .png extension
        if filename.endswith('.png'):
            # Extract the name from the filename
            name = extract_name(filename)
            # Add the name to the set of unique names
            unique_names.add(name)
    
    # Return the set of unique names
    return unique_names

def save_names_to_csv(names, output_csv_path):
    # Open the output CSV file in write mode with utf-8 encoding
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the names to the CSV file
        for name in names:
            writer.writerow([name])
            print(name)

if __name__ == "__main__":
    # Define the folder path containing the .png files
    # Create a Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()

    # Open a file dialog to select a folder
    folder_path = filedialog.askdirectory(title="Select Folder Containing PNG Files")
    # Define the output CSV file path
    # Open a file dialog to select a folder to save the CSV file
    output_folder_path = filedialog.askdirectory(title="Select Folder to Save CSV File")
    # Define the output CSV file path
    output_csv_path = os.path.join(output_folder_path, 'MasterNames.csv')
    
    # Get the unique names from the .png files in the specified folder
    unique_names = get_unique_names_from_png_files(folder_path)
    # Save the unique names to the specified CSV file
    save_names_to_csv(unique_names, output_csv_path)

    print('Operations Complete')