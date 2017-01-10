import unittest
import web_scraper

"""
tests.py:

Note: These tests may only run in Pycharm

Some unit tests to test the Web Crawler class.
They test for getting the assets and link from a web page.
"""

class TestWebCrawler(unittest.TestCase):


    def test_css_asssets(self):
        starting_url = "http://thomasbrereton.com"
        asset_specification = [".css"]
        debug_limit = 1

        # We create a web crawler object
        web_crawler = web_scraper.WebCrawler(starting_url, asset_specification, debug_limit)
        web_crawler.crawl_url_domain()

        # We expect several style sheets
        expected = ["assets/css/bootstrap.css", "assets/css/main.css", "assets/css/font-awesome.min.css",
                    'http://fonts.googleapis.com/css?family=Oswald:400,300,700',
                    'http://fonts.googleapis.com/css?family=EB+Garamond']
        self.assertEqual(web_crawler.page_assets, expected)

    def test_png_asssets_1(self):
        starting_url = "http://thomasbrereton.com"
        asset_specification = [".png"]
        debug_limit = 1

        # We create a web crawler object
        web_crawler = web_scraper.WebCrawler(starting_url, asset_specification, debug_limit)
        web_crawler.crawl_url_domain()

        # We expect there to be .png images
        expected = []

        # Note this is assert not equals
        self.assertNotEqual(web_crawler.page_assets, expected)

    def test_png_asssets_2(self):
        starting_url = "http://thomasbrereton.com"
        asset_specification = [".png"]
        debug_limit = 1

        # We create a web crawler object
        web_crawler = web_scraper.WebCrawler(starting_url, asset_specification, debug_limit)
        web_crawler.crawl_url_domain()

        # We expect some .png images
        expected = ["assets/ico/favicon.png", "assets/img/logo.png"]
        self.assertEqual(web_crawler.page_assets, expected)

    def test_png_asssets_2(self):
        starting_url = "http://thomasbrereton.com"
        asset_specification = ["mail"]
        debug_limit = 1

        # We create a web crawler object
        web_crawler = web_scraper.WebCrawler(starting_url, asset_specification, debug_limit)
        web_crawler.crawl_url_domain()

        # We don't expect to parse the emails
        expected = []
        self.assertEqual(web_crawler.page_assets, expected)

    def test_links_1(self):
        starting_url = "http://thomasbrereton.com"
        asset_specification = [".png"]
        debug_limit = 3

        # We create a web crawler object
        web_crawler = web_scraper.WebCrawler(starting_url, asset_specification, debug_limit)
        web_crawler.crawl_url_domain()

        # There are no further linkes so there should only be one url
        expected = ["http://thomasbrereton.com"]
        self.assertEqual(web_crawler.links, expected)


if __name__ == '__main__':
    unittest.main()
