"""Spider to explore HP Carbon footprints.

See a category page here https://h22235.www2.hp.com/hpinfo/globalcitizenship/environment/productdata/ProductCarbonFootprintmonitors.html

This spider:
 - scrapes a category page
 - finds the link to other categories page
 - list the links to all products for this category
 - scrape the corresponding links (except if they were already in existing sources).
 - use the HP parser to extract info.

Note that extracting the whole info is quite long, so be patient.
"""
import io
from typing import Any, Iterator

import scrapy
from scrapy import http

from tools.spiders.lib import spider
from tools.parsers import hp_all


_INDEX_PAGE_URL = 'https://h22235.www2.hp.com/hpinfo/globalcitizenship/environment/productdata/ProductCarbonFootprintmonitors.html'


class HPSpider(spider.BoaViztaSpider):

    name = 'HP'

    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    }

    start_urls = [_INDEX_PAGE_URL]

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse a HP Eco page for a products category."""
        # Find other categories.
        url_descriptor = 'a[class*=dropdown-option]::attr(href)'
        for url_link in response.css(url_descriptor):
            url = response.urljoin(url_link.extract())
            yield scrapy.Request(url)

        # List products.
        url_descriptor = 'a[href*=productcarbonfootprint]::attr(href)'
        for url_link in response.css(url_descriptor):
            url = response.urljoin(url_link.extract())
            if self._should_skip(url):
                continue
            yield scrapy.Request(url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in hp_all(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            yield device.data
