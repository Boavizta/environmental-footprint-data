
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert


# start web browser
options = Options()
#options.add_argument("--headless")
#options.add_argument("--dump-dom")
options.add_argument("--incognito")
browser = webdriver.Chrome(options=options)


# get source code
browser.get("https://www.microsoft.com/en-us/download/details.aspx?id=55974")
# Implicit wait


browser.find_element(By.XPATH,"//a[contains(@href, 'confirmation.aspx')]").click()

WebDriverWait(browser, 10).until(
       EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td[class=co1]'))
)
browser.find_element(By.XPATH,"//input[contains(@aria-label, '.pdf')]").click()

browser.find_element(By.XPATH,"//a[@class='mscom-link button next']").click()


WebDriverWait(browser, 10).until(
       EC.presence_of_element_located((By.XPATH, "//a[text()='click here to download manually']"))
)

browser.find_element(By.XPATH,"//a[text()='click here to download manually']").click()
all_pdfs = browser.find_elements(By.XPATH,"//a[contains(@href, '.pdf')]")
pdfs=[]
pdfs.append([i.get_attribute("href") for i in all_pdfs])
for i in all_pdfs:
    print(i.get_attribute("href"))
# close web browser
browser.close()