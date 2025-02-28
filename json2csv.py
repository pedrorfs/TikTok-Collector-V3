import csv
import json

def convert_video_into_csv(videos, filename):
    # Open the CSV file in write mode
    with open(f"{filename}.csv", 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Define the header for the CSV file
        header = list(videos[0].keys())

        # Write the header row
        csv_writer.writerow(header)
        
        for video in videos:
            # Prepare the row using the attributes
            row = video.values()
            
            # Write the row to the CSV file
            csv_writer.writerow(row)

with open("responses.json", "r",  encoding='utf-8') as file:
    data = json.load(file)  # Load JSON as a Python dictionary
    videos = []
    for video in data.values():
        videos.append(video)
    convert_video_into_csv(videos, "enaldinho")