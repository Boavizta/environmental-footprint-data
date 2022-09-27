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
from tools.parsers import dell_laptop
from tools.parsers.lib import data

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

_INDEX_PAGE_URL = 'https://www.dell.com/en-us/dt/corporate/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm'

class DellSpider(spider.BoaViztaSpider):

    name = 'Dell'

    start_urls = [('Desktop', _INDEX_PAGE_URL + "#tab0=0"),
                  ('Laptop', _INDEX_PAGE_URL + "#tab0=1"),
                  ('Monitor', _INDEX_PAGE_URL + "#tab0=2"),
                  ('Server', _INDEX_PAGE_URL + "#tab0=3"),
                  ('Storage', _INDEX_PAGE_URL + "#tab0=4"),
                  ('Thin client', _INDEX_PAGE_URL + "#tab0=5")]

    def start_requests(self):
        options = Options()
        #options.add_argument("--headless")
        browser = webdriver.Chrome(options=options)
        pdfs={}
        for subcategory,url in self.start_urls:
            browser.get(url)
            browser.refresh()
            WebDriverWait(browser, 50).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class=list-component]')))
            all_pdfs = browser.find_elements(By.XPATH,"//a[contains(@href,'.pdf')]")
            for i in all_pdfs:
                url = i.get_attribute("href")
            pdfs[subcategory] = [i.get_attribute("href") for i in all_pdfs]
        for subcategory,pdf_group in pdfs.items():
            if subcategory in ['Server','Storage']:
                category = 'Datacenter'
            else:
                category = 'Workplace'
            for pdf_link in pdf_group:
                if (not 'lca-' in pdf_link) and (not 'Statement' in pdf_link) :
                    if (not 'http:' in pdf_link) and (not 'https:' in pdf_link):
                        pdf_link="https:" + pdf_link
                    if self._should_skip(pdf_link):
                        continue
                    if category == 'Workplace':
                        yield scrapy.Request(pdf_link, callback=self.parse_carbon_footprint,
                                            cb_kwargs=dict(subcategory=subcategory))
                    # Should add a specific parser call for Datacenter devices

    def parse_carbon_footprint(
        self, response, subcategory, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in dell_laptop.parse(io.BytesIO(response.body), response.url):
            device.data['manufacturer'] = "Dell"
            device.data['sources'] = response.url
            device.data['sources_hash'] = data.md5(io.BytesIO(response.body))
            device.data['subcategory'] = subcategory
            yield device.reorder().data
