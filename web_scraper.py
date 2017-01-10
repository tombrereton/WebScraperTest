#!/usr/bin/env python3
import bs4 as bs
import requests
import json
import collections
import argparse

"""
web_scraper.py:


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


A web crawler program which crawls a specified domain and determines
the assets for every page crawled. Where an asset is an image,
javascript script, css stylesheet, etc.

The pages and their associated assets are saved
in a json file and also outputted to STDOUT.

The starting_url/domain is specified by passing it into the WebCrawler constructor.

The assets are specified by passing a list containing their typical
suffixes or substrings (i.e. '.jpg', '.css', '.js') into the WebCrawler constructor.
"""

__author__ = "Tom Brereton"
__version__ = "1.0"
__email__ = "admin@thomasbrereton.com"
__status__ = "Development"


class WebCrawler:

    def __init__(self, url, asset_specification, debug_limit=None):
        """
        :param url:
            (string) the starting url for the web crawler. This also specifies
            the domain the crawler must remain on.
        :param asset_specification:
            (list of strings) containing the strings specifying what is an asset
            (i.e. '.jpg' means any string containing '.jpg' is an asset).
        :param debug_limit:
            (int) an optional parameter which specifies how many loops the crawler
            should complete.
            For example,
                debug_limit=1 will loop once so it will only get the assets for the starting url.
                debug_limit=2 will loop twice but will traverse every link on the starting url
                and therefore get the assets for all of those links and the starting url.
        """
        self.url = url
        self.asset_specification = asset_specification
        self.asset_json_list = []
        self.links = [self.url]
        self.links_to_parse = [self.url]
        self.page_links = None
        self.page_assets = None
        if debug_limit is None:
            self.debug_limit = -1
        else:
            self.debug_limit = debug_limit

    def crawl_url_domain(self):
        debug_counter = 0
        new_links_to_parse = []

        # We loop until the length of parse_us is 0 which
        # means there are no more links left to crawl on the domain
        while debug_counter != self.debug_limit and len(self.links_to_parse) != 0:

            # For each link (page) in parse_us we get every link and every
            # asset on that page
            for page in self.links_to_parse:

                # We get all the links and assets for page
                self.get_content(page)

                # We separate links (data) from assets and append the new links to links_to_parse
                new_links_to_parse += self.page_links

                # Append the page and it's associated assets to an ordered dictionary
                temp_asset_tree = collections.OrderedDict({"url": page, "assets": self.page_assets})
                self.asset_json_list += [collections.OrderedDict(temp_asset_tree)]

            debug_counter += 1

            # We remove the links already crawled and assign the remaining
            # links to parse_us
            self.links_to_parse = [link for link in new_links_to_parse if link not in self.links]
            self.links += self.links_to_parse

            if len(self.links_to_parse) == 0:
                print("No more links left!")
            elif debug_counter == self.debug_limit:
                print("Debug limit reached!")

    def get_content(self, page):
        """
        We use a function to get all the links and assets on a url.
        :param page:
            (string) this is the page parse to get the 'soup'.
        :return:
        """
        try:
            # We get the response object at the 'url'
            resp = requests.get(page)

            # We parse the response using the BeautifulSoup library
            soup = bs.BeautifulSoup(resp.text, 'lxml')

            # We parse the soup for the links
            self.page_links = self.parse_links_on_page(page, soup)

            # We parse the soup for the assets
            self.page_assets = self.get_assets_on_page(soup)

        # We return an empty list for the handled errors
        except TypeError as e:
            print(e)
            print("\nGot a TypeError, probably got a None that we tried to iterate over\n")
            return []
        except IndexError as e:
            print(e)
            print("\nNo useful links?\n")
            return []
        except AttributeError as e:
            print(e)
            print("\nLikely got None for links\n")
            return []
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("\nEnsure the url is entered correctly and you are connected to the internet.\n")

    def get_assets_on_page(self, soup):
        """
        We use a function to get all the 'assets' for a url.
        Assets are as we defined in the main functions.

        :param soup:
            (string) this is text parsed by the BeautifulSoup library
            and is what we parse further for assets.
        :return:
            (list of strings) where each string is a link to an 'asset'
        """

        # We get the assets, images and scripts
        assets = [asset.get('href') for asset in soup.find_all('link') if asset.get('href') is not None]
        assets += [image.get('src') for image in soup.find_all('img') if image.get('src') is not None]
        assets += [script.get('src') for script in soup.find_all('script') if script.get('src') is not None]

        # We remove any link (asset) that doesn't match the asset_specification
        assets = [asset for asset in assets if self.is_asset(asset)]

        # We concatenate the local asset links (starts with '/') to the url
        assets = [self.handle_local_link(self.url, asset) for asset in assets]

        return assets

    def is_asset(self, asset):
        """
        We use a function to determine if a link (asset) is
        an asset by checking if it contains any of the strings
        defined in the asset_specification.

        :param asset:
            (string) this is a url that we check is an asset or not.
        :return:
            We return a boolean value, true if it is an asset,
            false if it is not.
        """

        # We loop over asset_specification and check if its element
        # is in the 'asset,' we return True if it does, False
        # if not
        for substring in self.asset_specification:
            if substring in asset:
                return True

    def parse_links_on_page(self, page, soup):
        """
        We use a function to parse all the links on a url (webpage).

        :param page:
            (string) this is the page we append local links to and
            also check against to see if the link is still on the
            correct domain.
        :param soup:
            (string) this is text parsed by the BeautifulSoup library
            and is what we parse further for assets.
        :return:
            (list of strings) we return a list of strings,
            where each string is a link on the url.
        """

        # We get all the links on the url
        links = [link.get('href') for link in soup.find_all('a')]

        # We remove any NoneType's in the list
        links = filter(None, links)

        # We concatenate local links (starts with '/') to the url
        links = [self.handle_local_link(self.url, link) for link in links]

        # We remove any links not starting with the url
        # i.e. we stay on the same domain
        links = [check_sub_domain(page, link) for link in links]

        # Removing links not on the sub domain caused NoneTypes
        # to occur in the list so we remove them again, this
        # time as a list so we can operate on the return variable
        links = [link for link in links if link is not None]

        return links

    def handle_local_link(self, page, link):
        """
        We use a function to handle local links
        which start with '/' (i.e. "/about")
        and append it to the url or '//' and append
        it to the starting url protocol (i.e. 'https:')

        :param page:
            (string) this is the url, or domain, that is being crawled.
        :param link:
            (string) and is the local link which is appended to url.
        :return:
            (string) we return a string which is the concatenation of url + link.
        """

        # If the link starts with '/' we append it to page
        # else if the link starts with '//' we append it to the protocol
        # else we return the link as is
        if link.startswith('//'):
            protocol = self.url.split("/")[0]
            return ''.join([protocol, link])
        elif link.startswith('/'):
            return ''.join([page, link[1:]])
        else:
            return link


def check_sub_domain(page, link):
    """
    We use a function to check if the link is on the specified domain (url).

    :param page:
        (string) this is the url, or domain, that is being crawled.
    :param link:
        (string) and it is checked to be on the specified domain (url).
    :return:
        (string) we return a link if it is on the domain (url), we return
        nothing if it is not.
    """

    # If the link starts with the domain (url)
    # we return the link
    if link.startswith(page):
        return link


def format_starting_url(url):
    if not url.endswith('/'):
        return ''.join([url, '/'])
    else:
        return url


def main():

    # We use the ArgumentParser library to run it from the command line
    # To see how to run this program change to the same directory as
    # 'web_scraper.py' and type './web_scraper -h'
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", type=str, default="https://gocardless.com/",
                        help="use this flag to enter a starting url in the format 'http{s}://...'")
    parser.add_argument("-d", "--debug", type=int, choices=[1, 2, 3], default=-1,
                        help="use this flag to debug and limit the pages crawled")
    parser.add_argument("-a", "--asset_specification", type=str,
                        default=".png,.jpg,.jpeg,.js,.css",
                        help="Enter the suffixes which specify an asset delimited by a comma: "
                             "','\n e.g. .jpg,.js,.css\n"
                        )
    args = parser.parse_args()

    if args.url:
        starting_url = format_starting_url(args.url)
    if args.debug:
        debug_limit = args.debug
    if args.asset_specification:
        arg_values = args.asset_specification
        asset_specification = [spec for spec in arg_values.split(",")]

    # We define what is considered an asset
    # asset_specification = [".png", ".jpg", ".jpeg", ".js", ".css"]

    # We create a web crawler object
    web_crawler = WebCrawler(starting_url, asset_specification, debug_limit)

    # We tell the web crawler to crawl the domain
    web_crawler.crawl_url_domain()

    # We get the urls and their assets from the web crawler object
    assets_for_json = web_crawler.asset_json_list

    # We get the total urls crawled from the web crawler object
    total_links = web_crawler.links

    # We write all the links to the file, 'url.txt'
    with open('url.txt','w') as f:
        f.write(str(total_links))

    # We write all the urls and their assets to a json file, 'assets.json'
    with open('assets.json', 'w') as fp:
        json.dump(assets_for_json, fp, sort_keys=True, indent=4)
        print(json.dumps(assets_for_json, sort_keys=True, indent=4))

if __name__ == '__main__':
    main()
