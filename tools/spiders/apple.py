"""Spider to explore Apple Carbon footprints.

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
#from tools.parsers import apple
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
        for pdf_link in response.css('li[class="reports-list-item"] a::attr(href)'):
            pdf_url = "%s%s" % (_BASE_URL, pdf_link.get())
            yield scrapy.Request(pdf_url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        """Parse a Google Product Carbon footprint document."""
        """
        for device in apple.parse(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            yield device.reorder().data
        """
        return
