
from tkinter.ttk import Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.common.keys import Keys

# start web browser
options = Options()
#options.add_argument("--headless")
#options.add_argument("--dump-dom")
options.add_argument("--incognito")
browser = webdriver.Chrome(options=options)


# get source code
browser.get("https://www.apple.com/environment/")
# Implicit wait
test=WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul[class=reports-list]'))
    )
# Explicit wait
all_pdfs = browser.find_elements(By.XPATH,"//a[contains(@href, '.pdf')]")
pdfs=[]
pdfs.append(i.get_attribute("href") for i in all_pdfs)
for i in all_pdfs:
    if "/products/" in i.get_attribute("href"):
        print(i.get_attribute("href"))
browser.close()