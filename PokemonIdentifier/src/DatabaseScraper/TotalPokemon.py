import os
import csv
import tkinter as tk
from tkinter import filedialog

def extract_name(filename):
    """
    Extracts the name from a filename.

    Args:
        filename (str): The filename to extract the name from.

    Returns:
        str: The extracted name.
    """
    # Split the filename by spaces and take the first part as the name
    name = filename.split(' ')[0]
    return name

def get_unique_names_from_png_files(folder_path):
    """
    Gets unique names from PNG files in a specified folder.

    Args:
        folder_path (str): The path to the folder containing PNG files.

    Returns:
        set: A set of unique names extracted from the PNG filenames.
    """
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
    """
    Saves a set of names to a CSV file.

    Args:
        names (set): A set of names to save.
        output_csv_path (str): The path to the output CSV file.
    """
    # Open the CSV file for writing
    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write each name to a new row in the CSV file
        for name in names:
            writer.writerow([name])

if __name__ == "__main__":
    # Code that should not run during Sphinx documentation build
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing PNG Files")
    output_csv_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save CSV File As")
    
    # Get unique names from PNG files
    unique_names = get_unique_names_from_png_files(folder_path)
    
    # Save the unique names to a CSV file
    save_names_to_csv(unique_names, output_csv_path)