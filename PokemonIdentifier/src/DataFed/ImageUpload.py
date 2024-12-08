import os
import json
import tkinter as tk
from tkinter import filedialog
from datafed.CommandLib import API
import time

df_api = API()
df_api.setContext("p/mem679-fall2024") #Instantiate
collection_id = "c/525610814" #Sets Collection ID

def create_record(data_path):
    title = "Garfield"
    description = "I Love Lasagna"
        # Create the record in Datafed
    rec_resp = df_api.dataCreate(
        title, 
        metadata=json.dumps({"Title": title, "Description": description, "Authorship":"William Bonnecaze","Affiliation":"Drexel University", "Datatype":"Image", "Dataformat":".png","Keywords":"Pokemon, Augmented Reality, Identification, Machine Learning"}), 
        parent_id=collection_id
    )
    # Extract the ID of the new data record
    this_rec_id = rec_resp[0].data[0].id
    print(this_rec_id)

    put_resp = df_api.dataPut(data_id = this_rec_id, path = data_path, wait=True)
    print(put_resp)

    #task_id = put_resp[0].task.id
    return 


def upload_images_in_folder():
    # Use tkinter to open a dialog for selecting a folder
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder with JPG Images")

    if not folder_path:
        print("No folder selected.")
        return

    # Iterate through all JPG files in the selected folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            file_path = os.path.join(folder_path, filename)
            print(f"Uploading: {file_path}")
            create_record(file_path)

    print("All images uploaded.")

# Call the function to start the upload process
upload_images_in_folder()
print("Done")