"""Spider to explore Apple Carbon footprints.

This spider:
 - scrape the environment page, then
 - extract all links to PDFs
 - extract all links to Carbon Footprint PDFs
 - use the apple parser to extract info.

Note that extracting the whole info is quite long, so be patient.
"""

import csv
import io
import logging
import time
from os import link
from typing import Any, Iterator

from tools.spiders.lib import spider
from tools.parsers import apple
from tools.parsers.lib import data

import scrapy
from scrapy import http


_BASE_URL = 'https://www.apple.com'
_INDEX_PAGE_URL = f'{_BASE_URL}/environment/'


class AppleSpider(spider.BoaViztaSpider):

    name = 'Apple'

    start_urls = [_INDEX_PAGE_URL]

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse the Apple Environment index page."""
        #we only want to get new PCF and therfore avoid getting archives
        for devices in response.xpath("//div[@id='product-reports-gallery']"):
            for pdf_link in devices.css('li[class="reports-list-item"] a::attr(href)'):
                pdf_url = "%s%s" % (_BASE_URL, pdf_link.get())
                if self._should_skip(pdf_url):
                    continue
                yield scrapy.Request(pdf_url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        """Parse a Apple Product Carbon footprint document."""
        for device in apple.parse(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            yield device.reorder().data
