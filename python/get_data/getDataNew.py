import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL of the webpage directory
directory_url = 'https://brunnur.vedur.is/pub/arason/brynjar/'

# Create a directory to store the downloaded files
output_directory = '../data/NewDownload'
os.makedirs(output_directory, exist_ok=True)

# Send a GET request to the directory URL
response = requests.get(directory_url)

if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links in the directory
    links = soup.find_all('a')

    for link in links:
        if not (str(link.string).startswith('f_') and str(link.string).endswith('.txt')):
            continue
        # Get the absolute URL of the linked file
        file_url = urljoin(directory_url, link['href'])

        # Extract the file name from the URL
        file_name = os.path.basename(file_url)

        # Download the file
        file_path = os.path.join(output_directory, file_name)
        with open(file_path, 'wb') as file:
            file_response = requests.get(file_url)
            file.write(file_response.content)
        
        print(f'Downloaded: {file_name}')
else:
    print(f'Failed to access {directory_url}')

print('Download complete.')
