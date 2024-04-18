#!/usr/bin/env python
# coding: utf-8

# In[5]:


import requests, os
from bs4 import BeautifulSoup
from utils.util import getTopLevelPath
from tqdm import tqdm


# In[8]:


def downloadMeasurements():
    # URL of the website containing the text files
    url = 'http://brunnur.vedur.is/pub/arason/brynjar/'
    outputpath = getTopLevelPath() + 'data/Measured/NewDownload-16-4-24/'
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links (a tags) on the webpage
    links = soup.find_all('a')

    # Iterate over the links
    for link in tqdm(links, total = len(links)):
        href = link.get('href')
        # Check if the link ends with '.txt'
        if href.endswith('.txt'):
            # Download the text file
            file_url = url + '/' + href
            if '_10min_' in href or '_sj_' in href:
                file_name = outputpath + '10min/' + href
            elif '_klst_' in href or '_vg_' in href:
                file_name = outputpath + 'klst/' + href
            else:
                file_name = outputpath + href
            with open(file_name, 'wb') as file:
                file.write(requests.get(file_url).content)

