"""Spider to explore Lenovo Carbon footprints.

See the landing page here https://www.lenovo.com/us/en/compliance/eco-declaration

This spider:
 - scrape the landing page, then
 - find the reference to the eco-declaration/main.js file
 - scrape the corresponding javascript and extract the html content
 - extract all links to Carbon Footprint PDFs
 - scrape the corresponding links (except if they were already in existing sources).
 - use the Lenovo parser to extract info.

Note that extracting the whole info is quite long, so be patient.
"""
import io
import re
from typing import Any, Iterator

import scrapy
from scrapy import http

from tools.spiders.lib import spider


_INDEX_PAGE_URL = 'https://www.lenovo.com/us/en/compliance/eco-declaration'

# Pattern of links to PCF docs in the main.js.
_PCF_LINK_IN_MAIN_JS_PATTERN = re.compile(r'href="([^"]+)">PCF ')


class LenovoSpider(spider.BoaViztaSpider):

    name = 'Lenovo'

    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    }

    start_urls = [_INDEX_PAGE_URL]

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse the Lenovo ECO Declarations index page."""
        src_descriptor = 'script::attr(src)'
        for sript_link in response.css(src_descriptor):
            script_url = response.urljoin(sript_link.extract())
            if script_url.endswith('eco-declaration/main.js'):
                yield scrapy.Request(script_url, callback=self.parse_index_main_js)
                break

    def parse_index_main_js(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[scrapy.Request]:
        """Parse the Lenovo javascript file listing all PDF documents."""
        for match in _PCF_LINK_IN_MAIN_JS_PATTERN.finditer(response.text):
            pcf_url = match.group(1)
            if self._should_skip(pcf_url):
                continue
            yield scrapy.Request(pcf_url, callback=self.parse_carbon_footprint)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        # TODO(pascal): Connect to the Lenovo PDF parser.
        if False:
            yield None
        # for device in lenovo(io.BytesIO(response.body), response.url):
        #    device.data['Sources'] = response.url
        #    yield device.data
