import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import time
import re

def sanitize_url(url):
    # Replace any characters that are not allowed in file names with an underscore
    safe_chars = re.compile(r'[^a-zA-Z0-9_.-]')
    return safe_chars.sub('_', url)


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


# ########### Modify variables here ###########
url = "https://wallup.net/results/?ss=" # URL of the page to scrape
output_folder_name = "wallupdownloads"
# ###########  End of modification  ###########

# Create dir with given name
create_dir(output_folder_name)

# Initialize headless browser, load webpage, get initial page height
driver = webdriver.Chrome()
driver.get(url)
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    time.sleep(7) # Change seconds depending on how fast your internet can load the images
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # wait for new images to load
    driver.implicitly_wait(100)

    # get the new page height
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break

    last_height = new_height

time.sleep(7)

# Get entire "scrolled" page source
page_source = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find all the <a> tags and extract the href attribute
div_tags = soup.find_all('div', class_='wrap2')
for div in div_tags:
    a_tags = div.find_all('a', href=True)
    for a in a_tags:
        print(a['href'])
        url = a['href']
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            image_url = soup.find('meta', property='og:image:secure_url')['content']
            response = requests.get(image_url)
            filename = sanitize_url(url)
            file_path = os.path.join(output_folder_name, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print('Image downloaded successfully!')
        else:
            print('Failed to download image. Status code:', response.status_code)

# Close the browser
driver.quit()
