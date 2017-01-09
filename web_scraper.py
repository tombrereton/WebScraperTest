#!/usr/bin/env python3
import bs4 as bs
import requests
import json
import collections

__author__ = "Tom Brereton"
__version__ = "1.0"
__email__ = "admin@thomasbrereton.com"
__status__ = "Development"


class WebCrawler:

    def __init__(self, url, asset_specification, debug_limit=None):
        self.url = url
        self.asset_specification = asset_specification
        self.asset_json_list = []
        self.links = [self.url]
        self.links_to_parse = [self.url]
        self.soup = None
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
                links_and_assets = self.get_content(page)

                # We separate links (data) from assets and append the new links to links_to_parse
                # assets = [asset for asset in links_and_assets if is_asset(asset, self.asset_specification)]
                # data = [link for link in links_and_assets if not is_asset(link, self.asset_specification)]
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

        :param url:
            (string) this is the url we are parsing.
        :param asset_specification:
            (list of strings) a list which specifies what is an asset.
        :return:
            (list of strings) We return a list containing all the links and assets for the url.
        """
        try:

            # We get the response object at the 'url'
            resp = requests.get(page)

            # We parse the response using the BeautifulSoup library
            soup = bs.BeautifulSoup(resp.text, 'lxml')

            # We parse the soup for the links
            self.page_links = parse_links_on_page(page, soup)

            # We parse the soup for the assets
            self.page_assets = get_assets(page, soup, self.asset_specification)

            # We concatenate the links and assets lists and return it
            # return links + assets

        # We return an empty list for the handled errors
        except TypeError as e:
            print(e)
            print("Got a TypeError, probably got a None that we tried to iterate over")
            return []
        except IndexError as e:
            print(e)
            print("No useful links?")
            return []
        except AttributeError as e:
            print(e)
            print("Likely got None for links")
            return []


def handle_local_links(url, link):
    """
    We use a function to handle local links
    which start with '/' (i.e. "/about")
    and append it to the url.

    :param url:
        (string) this is the url, or domain, that is being crawled.
    :param link:
        (string) and is the local link which is appended to url.
    :return:
        (string) we return a string which is the concatenation of url + link.
    """

    # Appends the link if  it starts with '/' else
    # it returns the link as is
    if link.startswith('/'):
        return ''.join([url, link[1:]])
    else:
        return link


def check_sub_domain(url, link):
    """
    We use a function to check if the link is on the specified domain (url).

    :param url:
        (string) this is the url, or domain, that is being crawled.
    :param link:
        (string) and it is checked to be on the specified domain (url).
    :return:
        (string) we return a link if it is on the domain (url), we return
        nothing if it is not.
    """

    # If the link starts with the domain (url)
    # we return the link
    if link.startswith(url):
        return link


def get_assets(url, soup, asset_specification):
    """
    We use a function to get all the 'assets' for a url.
    Assets are as we defined in the main functions.

    :param asset_specification:
        (list of strings) the list contains the asset specification
        (i.e. '.jpg' means any string containing '.jpg' is an asset).
    :param url:
        (string) this is the url we get the assets from.
    :param soup:
        (string) this is text parsed by the BeautifulSoup library
        and is what we parse further for assets.
    :return:
        (list of strings) where each string is a link to an 'asset'
    """

    # We get the assets, images and scripts
    assets = [asset.get('href') for asset in soup.find_all('link')]
    images = [image.get('src') for image in soup.find_all('img') if image.get('src') is not None]
    scripts = [script.get('src') for script in soup.find_all('script') if script.get('src') is not None]

    # We concatenate the assets, images and scripts into one list
    assets += images + scripts

    # We remove any link (asset) that doesn't match the asset_specification
    assets = [asset for asset in assets if is_asset(asset, asset_specification)]

    # We concatenate the local asset links (starts with '/') to the url
    assets = [handle_local_links(url, asset) for asset in assets]

    return assets


def is_asset(asset, asset_specification):
    """
    We use a function to determine if a link (asset) is
    an asset by checking if it contains any of the strings
    defined in the asset_specification.

    :param asset:
        (string) this is a url that we check is an asset or not.
    :param asset_specification:
        (list of strings) containing the strings specifying what is an asset
        (i.e. '.jpg' means any string containing '.jpg' is an asset).
    :return:
        We return a boolean value, true if it is an asset,
        false if it is not.
    """

    # We loop over asset_specification and check if its element
    # is in the 'asset,' we return True if it does, False
    # if not
    for substring in asset_specification:
        if substring in asset:
            return True


def parse_links_on_page(url, soup):
    """
    We use a function to parse all the links on a url (webpage).

    :param url:
        (string) this is the url we are parsing for links.
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
    links = [handle_local_links(url, link) for link in links]

    # We remove any links not starting with the url
    # i.e. we stay on the same domain
    links = [check_sub_domain(url, link) for link in links]

    # Removing links not on the sub domain caused NoneTypes
    # to occur in the list so we remove them again, this
    # time as a list so we can operate on the return variable
    links = [link for link in links if link is not None]

    return links


def main():

    # We define the domain which the web crawler will crawl
    starting_url = "http://gocardless.com/"
    # We define what is considered an asset
    asset_specification = [".png", ".jpg", ".jpeg", ".js", ".css"]
    # We define a debug limit so it doesn't traverse the whole domain
    debug_limit = 1

    web_crawler = WebCrawler(starting_url, asset_specification, debug_limit)

    web_crawler.crawl_url_domain()

    assets_for_json = web_crawler.asset_json_list
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
