import csv
import logging
from typing import Any, Optional
from scrapy.extensions.httpcache import DummyPolicy
import os
from urllib.parse import urlparse

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
                return True
            else:
                return False

    def __init__(self, existing: Optional[str] = None, blacklist: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._existing_sources = set()
        self._existing_blacklist = set()
        if existing:
            # Load existing sources from CSV file (pass in argument with -a existing=filename.csv).
            with open(existing, 'rt', encoding='utf-8') as existing_file:
                reader = csv.DictReader(existing_file)
                for row in reader:
                    if row.get('sources'):
                        self._existing_sources.add(os.path.basename(urlparse(row['sources']).path))
        if blacklist:
            # Load existing files to blacklist
            with open(blacklist, 'rt', encoding='utf-8') as blacklist_file:
                for line in blacklist_file:
                    self._existing_blacklist.add(line.strip())

    def _should_skip(self, source: str) -> bool:
        if os.path.basename(urlparse(source).path) in self._existing_sources:
            logging.info('Source already existing: %s', source)
            return True
        if os.path.basename(urlparse(source).path) in self._existing_blacklist:
            logging.info('Source is blacklisted: %s', source)
            return True
        return False
