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
from typing import Any, Iterator

import scrapy
from scrapy import http

from tools.spiders.lib import spider
from tools.parsers import dell_laptop


_INDEX_PAGE_URL = 'https://corporate.delltechnologies.com/en-us/social-impact/advancing-sustainability/sustainable-products-and-services/product-carbon-footprints.htm'


class DellSpider(spider.BoaViztaSpider):

    name = 'Dell'

    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    }

    start_urls = [_INDEX_PAGE_URL]

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse the index page."""
        url_descriptor = 'a::attr(data-tab-content-url)'
        for link_href in response.css(url_descriptor):
            link_url = link_href.extract()
            if 'product-carbon-footprints/jcr:content' in link_url:
                link_url = link_url.replace('/content/emc', '').replace('/corporate', '')
                yield scrapy.Request(response.urljoin(link_url), callback=self.parse_category_page)

    def parse_category_page(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[scrapy.Request]:
        """Parse a Dell category page."""
        href_descriptor = 'a::attr(href)'
        for link_href in response.css(href_descriptor):
            link_url = response.urljoin(link_href.extract())
            if self._should_skip(link_url):
                continue
            if '/carbon-footprint' in link_url and link_url.endswith('.pdf'):
                yield scrapy.Request(link_url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in dell_laptop(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            yield device.data
