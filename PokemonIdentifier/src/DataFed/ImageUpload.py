import os
import json
import tkinter as tk
from tkinter import filedialog
from datafed.CommandLib import API
import time

df_api = API()
df_api.setContext("p/mem679-fall2024") #Instantiate
collection_id = "c/525610814" #Sets Collection ID

def create_record(data_path, filename):
    """
    Creates a new data record in Datafed with the given image file.
    Args:
        data_path (str): The file path to the image data to be uploaded.
        filename (str): The name of the image file.
    Returns:
        None
    This function performs the following steps:
    1. Constructs a title and description for the data record based on the filename.
    2. Creates a new data record in Datafed with the specified metadata.
    3. Extracts the ID of the newly created data record.
    4. Uploads the image data to the newly created data record.
    5. Prints the ID of the new data record and the response from the data upload.
    """
    # Construct the title and description for the data record
    title = filename
    description = f"JPG image of {filename} for Pokemon Identifier Dataset"
    
    # Create the record in Datafed with the specified metadata
    rec_resp = df_api.dataCreate(
        title, 
        metadata=json.dumps({
            "Title": title, 
            "Description": description, 
            "Authorship": "William Bonnecaze",
            "Affiliation": "Drexel University", 
            "Datatype": "Image", 
            "Dataformat": ".png",
            "Keywords": "Pokemon, Augmented Reality, Identification, Machine Learning"
        }), 
        parent_id=collection_id
    )
    
    # Extract the ID of the new data record
    this_rec_id = rec_resp[0].data[0].id
    print(this_rec_id)
    
    # Upload the image data to the newly created data record
    put_resp = df_api.dataPut(data_id=this_rec_id, path=data_path, wait=True)
    print(put_resp)
    
    return


def upload_images_in_folder():
    """
    Opens a dialog to select a folder and uploads all JPG images in the selected folder.
    This function uses tkinter to open a folder selection dialog. Once a folder is selected,
    it iterates through all JPG files in the folder, prints the name of each file being uploaded,
    and calls the create_record function to handle the upload process.
    If no folder is selected, the function prints a message and returns.
    Returns:
        None
    """
    # Use tkinter to open a dialog for selecting a folder
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder with JPG Images")

    # Check if a folder was selected
    if not folder_path:
        print("No folder selected.")
        return

    # Iterate through all JPG files in the selected folder
    for filename in os.listdir(folder_path):
        # Check if the file has a .jpg extension (case insensitive)
        if filename.lower().endswith('.jpg'):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)
            # Remove the file extension from the filename
            filename_without_extension = filename[:-4]
            print(f"Uploading: {filename}")
            # Call the create_record function to upload the image
            create_record(file_path, filename_without_extension)

    print("All images uploaded.")

# Call the function to start the upload process
upload_images_in_folder()
print("Done")