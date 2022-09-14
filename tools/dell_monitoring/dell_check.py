from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# start web browser
options = Options()
options.add_argument("--headless")
#options.add_argument("--dump-dom")
desired_capabilities = options.to_capabilities()
browser = webdriver.Chrome(options=options)


# get source code
browser.get("https://www.dell.com/en-us/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm#tab0=1")
# Implicit wait
test=WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class=list-component]'))
    )
# Explicit wait
all_pdfs = browser.find_elements(By.XPATH,"//a[contains(@href, '.pdf')]")
pdfs=[]
pdfs.append([i.get_attribute("href") for i in all_pdfs])
for i in pdfs:
    print(i.get_attribute("href"))



# close web browser
browser.close()