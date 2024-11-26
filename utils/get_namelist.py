import os

folder_path = 'bilibili_data'
with open('namelist.txt', 'w') as f:
    for fp in os.listdir(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            # Extract the name from the filename
            name = filename.split('_')[0]
            f.write(name + '\n')