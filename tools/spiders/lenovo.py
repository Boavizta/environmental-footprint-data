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
import html
import io
import re
from typing import Any, Iterator
from tools.parsers.lib import data

import scrapy
from scrapy import http

from tools.spiders.lib import spider
from tools.parsers import lenovo


_INDEX_PAGE_URL = 'https://www.lenovo.com/us/en/compliance/eco-declaration'

# Pattern of tab names.
_TAB_NAMES_IN_MAIN_JS_PATTERN = re.compile(
    r'data-toggle="tab".*href="#(?P<tab_id>[^"]+)".*>(?P<title>.*)</a>')

# Pattern for extracting the id attribute.
_ID_ATTR_PATTERN = re.compile(r'id="([^"]+)"')

# Pattern of links to PCF docs in the main.js.
_PCF_LINK_IN_MAIN_JS_PATTERN = re.compile(r'href="([^"]+)">PCF ')

_CATEGORIES = {
    'Notebook': ('Workplace', 'Laptop'),
    'Monitor': ('Workplace', 'Monitor'),
    'Server': ('Datacenter', 'Server'),
    'Workstation': ('Workplace', 'Workstation'),
    'Desktop': ('Workplace', 'Desktop'),
    'Tablet': ('Workplace', 'Tablet'),
}


class LenovoSpider(spider.BoaViztaSpider):

    name = 'Lenovo'

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

        # List existing tabs with their IDs.
        # The list of the tabs is as the top of the file which contains title like
        # "Notebooks & Ultrabooks", "Desktop & All-in-Ones".
        tab_titles = {
            match.group('tab_id'): html.unescape(match.group('title'))
            for match in _TAB_NAMES_IN_MAIN_JS_PATTERN.finditer(response.text)
        }

        # The link to various models grouped into tabs.
        tab_contents = response.text.split('"tab-pane')[1:]
        for tab_content in tab_contents:
            first_line = tab_content.split('\n', 1)[0]
            if 'role="tabpanel"' not in first_line:
                continue
            tab_id_match = _ID_ATTR_PATTERN.search(first_line)
            if not tab_id_match:
                continue
            tab_id = tab_id_match.group(1)
            tab_title = tab_titles[tab_id]

            for match in _PCF_LINK_IN_MAIN_JS_PATTERN.finditer(tab_content):
                pcf_url = match.group(1)
                if self._should_skip(pcf_url):
                    continue
                yield scrapy.Request(
                    pcf_url, callback=self.parse_carbon_footprint,
                    cb_kwargs={'tab_title': tab_title})

    def parse_carbon_footprint(
        self, response: http.Response, tab_title: str, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        for device in lenovo.parse(io.BytesIO(response.body), response.url):
            device.data['sources'] = response.url
            device.data['sources_hash']=data.md5(io.BytesIO(response.body))
            for keyword, category_and_sub in _CATEGORIES.items():
                if keyword in tab_title:
                    device.data['category'], device.data['subcategory'] = category_and_sub
                    break
            yield device.data
