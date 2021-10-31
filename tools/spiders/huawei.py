"""Spider to explore Huawei Carbon footprints.

See the index page here https://consumer.huawei.com/en/support/product-environmental-information/

This spider:
 - scrapes the index page
 - finds the type IDs for the product types
 - create the JSONP queries to get the list of models
 - list all models per product type and finds the IDs of those model types
 - create the JSONP queries to get the info for each model
 - scrape the download URLs (except if they were already in existing sources).
 - use the Huawei to extract info.

Note that extracting the whole info is quite long, so be patient.
"""
import io
import json
import time
from typing import Any, Iterator
from urllib import parse

import scrapy
from scrapy import http

from tools.spiders.lib import spider


_INDEX_PAGE_URL = 'https://consumer.huawei.com/en/support/product-environmental-information/'
_LIST_MODELS_URL = 'https://consumer.huawei.com/support/services/service/file/proModel/list'
_LIST_FILES_URL = 'https://consumer.huawei.com/support/services/service/file/list'


class HPSpider(spider.BoaViztaSpider):

    name = 'Huawei'

    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    }

    start_urls = [_INDEX_PAGE_URL]

    def _create_list_files_request(self, url: str, product_id: str) -> str:
        timestamp = int(time.time())
        request_data = {
            'jsonp': f'jQuery360006362190868530293_{timestamp}',
            'siteCode': 'worldwide',
            'productId': product_id,
            'fileType': 'manual',
            'subFileType': 'ProductEnvReport',
            '_': timestamp,
        }
        return f'{url}?{parse.urlencode(request_data)}'

    def parse(self, response: http.Response, **unused_kwargs: Any) -> Iterator[scrapy.Request]:
        """Parse the Huawei Product Environmental Information index page."""
        type_descriptor = 'li[typeid]::attr(typeid)'
        for type_id_ref in response.css(type_descriptor):
            product_id = type_id_ref.extract()
            yield scrapy.Request(
                self._create_list_files_request(_LIST_MODELS_URL, product_id),
                callback=self.parse_list_models)

    def parse_list_models(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[scrapy.Request]:
        jsonp = response.text
        json_content = jsonp[jsonp.index('(') + 1:jsonp.rindex(')')]
        for product in json.loads(json_content):
            if 'downloadUrl' in product:
                download_url = product['downloadUrl']
                if not self._should_skip(download_url):
                    yield scrapy.Request(download_url, self.parse_carbon_footprint)
                continue
            if 'productId' in product:
                yield scrapy.Request(
                    self._create_list_files_request(_LIST_FILES_URL, product['productId']),
                    callback=self.parse_list_models)

    def parse_carbon_footprint(
        self, response: http.Response, **unused_kwargs: Any,
    ) -> Iterator[Any]:
        # TODO(pascal): implement a Huawei PDF scraper and connect it here.
        ...
