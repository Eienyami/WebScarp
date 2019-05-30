import pytesseract
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

# Site and captcha url
siteurl = ''
imgurl = ''
payload={}

# Functions for removing the noise from captcha image
def start_point(w,h,img):
    for i in range(5,w):
        for j in range(5,h):
            if (img.getpixel((i,j))[0] < 50 and
                img.getpixel((i,j))[1] < 50 and
                img.getpixel((i,j))[2] < 50 ):
                return (i,j)
            
            
def removeLinethrough(x,y, img):
    line_y = start_point(x,y,img)[1]
    for i in range(x):
        img.putpixel((i,line_y),img.getpixel((i,line_y+1)))
        img.save('cap_final.jpeg')


driver = webdriver.Firefox(executable_path=r'C:\geckodriver.exe')
driver.get(siteurl)
driver.execute_script("window.open('" + imgurl + "', 'new_window')")
driver.switch_to.window(driver.window_handles[1])
time.sleep(1)

driver.save_screenshot('cap.png')
img = Image.open('cap.png')

# Cropping out captcha from screenshot
width = img.size[0]
height = img.size[1]
new_width = 120
new_height = 40
left = (width - new_width)/2
top = (height - new_height)/2
right = (width + new_width)/2
bottom = (height + new_height)/2
img2 = img.crop(box=(left, top, right, bottom))
rgb = img2.convert('RGB')

removeLinethrough(120,40,rgb)

# Extracting text from image
img_text = pytesseract.image_to_string(Image.open('cap_final.jpeg'))

# payload['CodeNumberTextBox'] = img_text
driver.switch_to.window(driver.window_handles[0])

# Filling the fields of form
for key in payload.keys():
    driver.find_element_by_id(key).send_keys(payload[key])

driver.find_element_by_id('btnSearch').click()

# Scrapping the table from site
html = driver.page_source
soup = BeautifulSoup(html)

data = []
table = soup.find('table', attrs = {'class':'Rgrid'}).find('tbody')
for row in table.find_all('tr'):
    for cols in row.find_all('td'):
        data.append([ele for ele in cols])

print(data)
