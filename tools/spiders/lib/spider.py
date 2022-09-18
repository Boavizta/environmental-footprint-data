import csv
import logging
from typing import Any, Optional
from scrapy.extensions.httpcache import DummyPolicy

import scrapy


class BoaViztaSpider(scrapy.Spider):
    """A base scrapy spider to factorize code from our multiple spiders."""
    custom_settings = {
        'USER_AGENT': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'),
        'CONCURRENT_REQUESTS' : 1
    }
    class CachePolicy(DummyPolicy):
        def should_cache_response(self, response, request):
            if '.pdf' in response.url:
                print(response.url + " cached.")
                return True
            else:
                print(response.url + " not cached.")
                return False

    def __init__(self, existing: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._existing_sources = set()
        if not existing:
            return

        # Load existing sources from CSV file (pass in argument with -a existing=filename.csv).
        with open(existing, 'rt', encoding='utf-8') as existing_file:
            reader = csv.DictReader(existing_file)
            for row in reader:
                if row.get('sources'):
                    self._existing_sources.add(row['sources'])

    def _should_skip(self, source: str) -> bool:
        if source not in self._existing_sources:
            return False
        logging.info('Source already existing: %s', source)
        return True
