# Spiders

This folder contains the [Scrapy](https://scrapy.org/) spider modules in charge of crawling and
scraping the providers' pages.

Each module (file) handles a consistant provider and uses the [parsers](../parsers) to extract
the carbon footprint data. Please keep the logic of extracting the data from a file (PDF or HTML)
in the `parsers` package.

To run a spider:

```sh
PYTHONPATH=. scrapy runspider tools/spiders/dell.py -L INFO -o new_dell.csv -s AUTOTHROTTLE_ENABLED=1 -a existing=dell.csv
```
