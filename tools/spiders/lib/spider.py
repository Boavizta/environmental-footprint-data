import csv
import logging
from typing import Any, Optional

import scrapy


class BoaViztaSpider(scrapy.Spider):
    """A base scrapy spider to factorize code from our multiple spiders."""

    def __init__(self, existing: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._existing_sources = set()
        if not existing:
            return

        # Load existing sources from CSV file (pass in argument with -a existing=filename.csv).
        with open(existing, 'rt', encoding='utf-8') as existing_file:
            reader = csv.DictReader(existing_file)
            for row in reader:
                if row.get('Sources'):
                    self._existing_sources.add(row['Sources'])

    def _should_skip(self, source: str) -> bool:
        logging.warning('Source already existing: %s', source)
        return source in self._existing_sources
