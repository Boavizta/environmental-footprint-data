"""Spider to explore HPE Carbon footprints.

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
from tools.parsers import hpe
from tools.parsers.lib import data

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


_INDEX_PAGE_URL = 'https://www.hpe.com/us/en/search-results.html?page=1&q=carbon+footprint+pdf&autocomplete=0&hq=more%3Adocs'

class DellSpider(spider.BoaViztaSpider):

    name = 'HPE'

    start_urls = [_INDEX_PAGE_URL]

    def start_requests(self):
        options = Options()
        #options.add_argument("--headless")
        options.add_argument("--incognito")
        browser = webdriver.Chrome(options=options)
        pdfs=[]
        for url in self.start_urls:
            browser.get(url)
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME,"gsr-result-link")))
            pdf_number=browser.find_element(By.CLASS_NAME,"gsr-list-header").text.replace(" Results for Documents","")
            click_more=True
            current=0
            pdfs=[]
            while click_more:
                try:
                    all_pdfs = browser.find_elements(By.CLASS_NAME,"gsr-result-link")
                    pdfs.append([i.get_attribute("href") for i in all_pdfs])
                    if (current + len(all_pdfs)) < int(pdf_number):
                        browser.find_element(By.CLASS_NAME,"next").click()
                        time.sleep(15)
                        current=current+len(all_pdfs)
                    else:
                        click_more = False
                except TimeoutException:
                    click_more = False
        for pdf_group in pdfs:
            for link in pdf_group:
                    browser.get(link)
                    pdf_link=browser.find_element(By.ID,"downloadPdfLink").get_attribute("href")
                    if self._should_skip(pdf_link):
                        continue
                    yield scrapy.Request(pdf_link, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in hpe.parse(io.BytesIO(response.body), response.url):
            device.data['manufacturer'] = "HP"
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            yield device.reorder().data
