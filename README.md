# WebScraperTest

web_scraper.py:

A web crawler program which crawls a specified domain and determines
the assets for every page crawled. Where an asset is an image,
javascript script, css stylesheet, etc.

The pages and their associated assets are saved
in a json file and also outputted to STDOUT.

The starting_url/domain is specified by passing it into the WebCrawler constructor.

The assets are specified by passing a list containing their typical
suffixes or substrings (i.e. '.jpg', '.css', '.js') into the WebCrawler constructor.



    usage: web_scraper.py [-h] [-url URL] [-d {1,2,3}] [-a ASSET_SPECIFICATION]

    optional arguments:
        -h, --help            show this help message and exit
        -url URL              use this flag to enter a starting url in the format
                                'http{s}://...'
        -d {1,2,3}, --debug {1,2,3}
                              use this flag to debug and limit the pages crawled
        -a ASSET_SPECIFICATION, --asset_specification ASSET_SPECIFICATION
                              Enter the suffixes which specify an asset delimited by
                                a comma: ',' e.g. .jpg,.js,.css


