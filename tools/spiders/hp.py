"""Spider to explore HP Carbon footprints.

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
from tools.parsers import hp_workplace
from tools.parsers.lib import data

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


_INDEX_PAGE_URL = 'https://h20195.www2.hp.com/v2/library.aspx?doctype=95&footer=95&filter_doctype=no&filter_country=no&cc=us&lc=en&filter_oid=no&filter_prodtype=rw&prodtype=ij&showproductcompatibility=yes&showregion=yes&showreglangcol=yes&showdescription=yes3doctype-95&sortorder-popular&teasers-off&isRetired-false&isRHParentNode-false&titleCheck-false#doctype-95&sortorder-revision_date&teasers-off&isRetired-false&isRHParentNode-false&titleCheck-false'

class DellSpider(spider.BoaViztaSpider):

    name = 'HP'

    start_urls = [_INDEX_PAGE_URL]

    def start_requests(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        browser = webdriver.Chrome(options=options)
        pdfs=[]
        for url in self.start_urls:
            browser.get(url)
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
            pdfs.append(i.get_attribute("href") for i in all_pdfs)
        for pdf_group in pdfs:
            for pdf_link in pdf_group:
                    if self._should_skip(pdf_link):
                        continue
                    yield scrapy.Request(pdf_link, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in hp_workplace.parse(io.BytesIO(response.body), response.url):
            device.data['manufacturer'] = "HP"
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            yield device.reorder().data
