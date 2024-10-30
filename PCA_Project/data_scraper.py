import os
import requests
import time
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# MAX_PICTURES = 500
# PAGEINDEX = 2


# scrape images and before and after images from plastic surgery.org
url_plastic_surgery = "https://www.plasticsurgery.org/photo-gallery/procedure/rhinoplasty"
url_gallery_of_cosmetic = "https://galleryofcosmeticsurgery.com/gallery-category/dr-sadati/nose/female-rhinoplasty/"


# modify data loader to collect data based on before and after, sift based on
# "before and after"


def split_images(input_folder, output_folder):
   if not os.path.exists(output_folder):
       os.makedirs(output_folder)
  
   for filename in os.listdir(input_folder):
       if filename.endswith('.jpg') or filename.endswith('.png'):
           try:
               image_path = os.path.join(input_folder, filename)
               image = Image.open(image_path)


               width, height = image.size
               midpoint = width // 2
              
               before_image = image.crop((0, 0, midpoint, height))
               after_image = image.crop((midpoint, 0, width, height))


               before_filename = f"{os.path.splitext(filename)[0]}_before.jpg"
               after_filename = f"{os.path.splitext(filename)[0]}_after.jpg"


               before_image.save(os.path.join(output_folder, before_filename))
               after_image.save(os.path.join(output_folder, after_filename))


           except Exception as e:
               print(f"ran into issue {e} while parsing file {filename}")
              


def scrape_with_selenium(url, output_folder, page):
   if not os.path.exists(output_folder):
       os.makedirs(output_folder)


   # Set up Chrome driver with Selenium
   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
   driver.get(url)
   time.sleep(3)  # Wait for the page to load


   soup = BeautifulSoup(driver.page_source, 'html.parser')
   img_tags = soup.find_all('img')


   for index, img_tag in enumerate(img_tags):
       img_url = img_tag.get('src') or img_tag.get('data-src')
      
       if img_url and img_url.startswith('http'):
           try:
               img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}).content
               img_filename = os.path.join(output_folder, f'image_{page}_{index+1}.jpg')
               with open(img_filename, 'wb') as img_file:
                   img_file.write(img_data)
               print(f"Saved image: {img_filename}")
           except Exception as e:
               print(f"Failed to download {img_url}: {e}")


   driver.quit()


def scrape_general(url, output_folder, page):
   # scrape images from online
   if not os.path.exists(output_folder):
       os.makedirs(output_folder)


   response = requests.get(url)


   if response.status_code == 200:
       soup = BeautifulSoup(response.text, 'html.parser')
       img_tags = soup.find_all('img')
      
       for index, img_tag in enumerate(img_tags):
           img_url = img_tag.get('src') or img_tag.get('data-src')
          
           if img_url and img_url.startswith('http'):
               img_data = requests.get(img_url).content
               img_filename = os.path.join(output_folder,
                                           f'image_{page}_{index+1}.jpg')
               with open(img_filename, 'wb') as img_file:
                   img_file.write(img_data)
   else:
       print("Couldn't fetch images :(")




def scrape_before_after(url, before_folder, after_folder, page):
   # scraping before and after pics and bucketing them in different folders
   if not os.path.exists(before_folder):
       os.makedirs(before_folder)
  
   if not os.path.exists(after_folder):
       os.makedirs(after_folder)
  
   response = requests.get(url)
  
   if response.status_code == 200:
       soup = BeautifulSoup(response.text, 'html.parser')
       img_tags = soup.find_all('img')


       for indx, img_tag in enumerate(img_tags):
           img_url = img_tag.get('src') or img_tag.get('data-src')
           alt_text = img_tag.get('alt', '').lower()


           if img_url and img_url.startswith("http") and "before" in alt_text:
               img_data = requests.get(img_url).content
               with open(os.path.join(before_folder, f"before_{indx}_page_{page}.jpg"), 'wb') as f:
                   f.write(img_data)


           elif img_url and img_url.startswith("http") and 'after' in alt_text:
               img_data = requests.get(img_url).content
               with open(os.path.join(after_folder, f"after_{indx}_page_{page}.jpg"), 'wb') as f:
                   f.write(img_data)
  
   print(f"bucketed for page: {page}")






def scrape_all_before_after(max_pics, page_indx, before, after):
   # similar to scrape all general, but will create and bucket images based on before and after
   while page_indx < 15:
       curr_curl = f"https://www.plasticsurgery.org/photo-gallery/procedure/rhinoplasty/page/{page_indx}"
       scrape_before_after(curr_curl, before, after, page_indx)
       page_indx += 1
       max_pics -= 1
   cleanup(before)
   cleanup(after)
   print(f"scraped for first {page_indx} pages")




def scrape_all_general(max_pics, page_indx, folder):
   # scrape from the whole website, disregarding before and after alt-tags.
   while page_indx > 0:
       curr_url = url_rest = f"https://www.plasticsurgery.org/photo-gallery/procedure/rhinoplasty/page/{page_indx}"
       scrape_general(curr_url, folder, page_indx)
       page_indx += 1
       max_pics -=1
   cleanup(folder)
   print(f"scraped for first {page_indx} pages")


# generate one image and save it to image_edges
def outline(save_folder, base_folder, image, laplace=False):
   # outline of image
   image_name = image
   image = os.path.join(base_folder, image)
   image = Image.open(image)


   if laplace:
       image = image.filter(ImageFilter.Kernel((3, 3), (-1, -1, -1, -1, 8,
                                         -1, -1, -1, -1), 1, 0))
   else:
       image = image.filter(ImageFilter.FIND_EDGES)


       # convert image more to RBG if not
       if image.mode != 'RGB':
           image = image.convert('RGB')
  
   new_image = image_name + "edges"
   image.save(f"{save_folder}/{new_image}.jpg")




def generate_outlines(save_folder, images):
   # create outlines for all the images
   if not os.path.exists(save_folder):
       os.makedirs(save_folder)
  
   for image in os.listdir(images):
       try:
           outline(save_folder, images, image)
       except Exception as e:
           # for KW --> look into these issues, why not converting?
           print(f"Bad file: {image}")
           print(f"Corresponding error: " + str(e))
  
   print("Done Generating Outlines!")




def cleanup(folder):
   # for some reason the images before folder has some garbage files in there
   # so this clean up file will ger rid of non jpg files


   for file in os.listdir(folder):
       file_path = os.path.join(folder, file)
      
       if os.path.isfile(file_path) and not file.endswith('.jpg'):
           os.remove(file_path)
  
   print("deleted garbage files")