
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
browser.get("https://h20195.www2.hp.com/v2/library.aspx?doctype=95&footer=95&filter_doctype=no&filter_country=no&cc=us&lc=en&filter_oid=no&filter_prodtype=rw&prodtype=ij&showproductcompatibility=yes&showregion=yes&showreglangcol=yes&showdescription=yes3doctype-95&sortorder-popular&teasers-off&isRetired-false&isRHParentNode-false&titleCheck-false#doctype-95&sortorder-revision_date&teasers-off&isRetired-false&isRHParentNode-false&titleCheck-false")
# Implicit wait
WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))) 
browser.find_element(By.ID,"onetrust-accept-btn-handler").click()
click_more=True
while click_more:
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//a[text()='Load More']"))) 
        time.sleep(3)
        if not "display: none" in browser.find_element(By.XPATH,"//a[text()='Load More']").get_attribute("style"):
            browser.find_element(By.XPATH,"//a[text()='Load More']").click()
        else:
            click_more = False
    except TimeoutException:
        click_more = False

all_pdfs = browser.find_elements(By.XPATH,"//a[contains(@href, 'GetDocument')]")
pdfs=[]
pdfs.append([i.get_attribute("href") for i in all_pdfs])
for i in all_pdfs:
    print(i.get_attribute("href"))
# close web browser
browser.close()