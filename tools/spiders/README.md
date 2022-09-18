# Spiders

This folder contains the [Scrapy](https://scrapy.org/) spider modules in charge of crawling and
scraping the providers' pages.

Each module (file) handles a consistant provider and uses the [parsers](../parsers) to extract
the carbon footprint data. Please keep the logic of extracting the data from a file (PDF or HTML)
in the `parsers` package.

To run a spider in production:

```sh
PYTHONPATH=. scrapy runspider tools/spiders/hp.py  -L INFO -o new_hp.csv -s AUTOTHROTTLE_ENABLED=1 -a existing=boavizta-data-us.csv -a blacklist=tools/monitoring/url_blacklist
```

To run a spider in dev or test mode, you should enable caching with the following command to avoid PDF download every time you lauch the spider

```sh
PYTHONPATH=. scrapy runspider tools/spiders/hp.py  -L INFO -o new_hp.csv -s AUTOTHROTTLE_ENABLED=1 -s HTTPCACHE_ENABLED=True -a existing=boavizta-data-us.csv -a blacklist=tools/monitoring/url_blacklist
```
