import requests
import os
def download_file(url, local_filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a local file to write the downloaded content
        with open(local_filename, 'wb') as file:
            # Write the content to the file in chunks
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'File downloaded successfully: {local_filename}')
    else:
        print(f'Failed to download file. Status code: {response.status_code}')

def delete_file(file_path):
    """Deletes the specified file if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f'File {file_path} deleted successfully.')
    else:
        print(f'The file {file_path} does not exist.')



# # Example usage
# url = 'https://adeapp.bordeaux-inp.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=6961&projectId=1&calType=ical&firstDate=2024-09-16&lastDate=2024-09-16&displayConfigId=71'  # Replace with your file URL
local_filename = 'downloaded_file.ics'  # Replace with your desired local filename
# download_file(url, local_filename)

delete_file(local_filename)