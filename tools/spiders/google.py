"""Spider to explore Google Product Carbon footprints.

See the landing page here https://sustainability.google/reports/

This spider:
 - scrape the landing page, then
 - find the reference to the eco-declaration/main.js file
 - scrape the corresponding javascript and extract the html content
 - extract all links to Carbon Footprint PDFs
 - scrape the corresponding links (except if they were already in existing sources).
 - use the Lenovo parser to extract info.

Note that extracting the whole info is quite long, so be patient.
"""
import html
import io
import re
from typing import Any, Iterator
from tools.parsers.lib import data

import scrapy
from scrapy import http

from tools.spiders.lib import spider
from tools.parsers import google

_INDEX_PAGE_URL = 'https://sustainability.google/reports/'


class GoogleSpider(spider.BoaViztaSpider):

    name = 'Google'

    start_urls = [_INDEX_PAGE_URL]

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse the Google Sustainibility Report index page."""
        for sript_link in response.css('tr[data-type*="Product report"] a::attr(href)'):
            script_url = response.urljoin(sript_link.extract())
            if self._should_skip(script_url):
                continue
            yield scrapy.Request(script_url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        """Parse a Google Product Carbon footprint document."""
        for device in google.parse(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            yield device.reorder().data
