"""Spider to explore Dell Carbon footprints.

See the landing page here https://corporate.delltechnologies.com/en-us/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm

This spider:
 - scrape the landing page, then
 - extract all links to tabs like "Desktops", "Notebooks", etc.
 - scrape the corresponding links which list devices for each category
 - extract all links to Carbon Footprint PDFs
 - scrape the corresponding links (except if they were already in existing sources).
 - use the dell parser to extract info.

Note that extracting the whole info is quite long, so be patient.
"""

import csv
import io
import logging
import time
from os import link
from typing import Any, Iterator

from tools.spiders.lib import spider
from tools.parsers import microsoft
from tools.parsers.lib import data

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

_INDEX_PAGE_URL = 'https://www.microsoft.com/en-us/download/details.aspx?id=55974'

class DellSpider(spider.BoaViztaSpider):

    name = 'Microsoft'
    
    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'),
        'CONCURRENT_REQUESTS' : 1
    }

    start_urls = [_INDEX_PAGE_URL]

    def start_requests(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        browser = webdriver.Chrome(options=options)
        pdfs=[]
        for url in self.start_urls:
            browser.get(url)
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
            pdfs.append(i.get_attribute("href") for i in all_pdfs)
        for pdf_group in pdfs:
            for pdf_link in pdf_group:
                    if self._should_skip(pdf_link):
                        continue
                    yield scrapy.Request(pdf_link, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in microsoft.parse(io.BytesIO(response.body), response.url):
            device.data['manufacturer'] = "Mircosoft"
            device.data['sources'] = response.url
            yield device.reorder().data
