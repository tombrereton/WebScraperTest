import bs4 as bs
import requests
import json




def handle_local_links(url, link):
    if link.startswith('/'):
        return ''.join([url, link[1:]])
    else:
        return link


def check_sub_domain(url, link):
    if link.startswith(url):
        return link


def get_assets(url, soup):
    assets = [asset.get('href') for asset in soup.find_all('link')]
    images = [image.get('src') for image in soup.find_all('img') if image.get('src') is not None]
    scripts = [script.get('src') for script in soup.find_all('script') if script.get('src') is not None]
    assets += images + scripts
    assets = [asset for asset in assets if is_asset(asset)]
    assets = [handle_local_links(url, asset) for asset in assets]
    return assets


def is_asset(asset):
    asset_list = [".png", ".jpg", ".jpeg", ".js", ".css"]
    for substring in asset_list:
        if substring in asset:
            return True


def parse_link_on_page(url, soup):
    links = [link.get('href') for link in soup.find_all('a')]
    links = filter(None, links)
    links = [handle_local_links(url, link) for link in links]
    links = [check_sub_domain(url, link) for link in links]
    links = [link for link in links if link is not None]
    #links = filter(None, links)
    return links


def get_content(url):
    """

    :param url:
    :return:
    """
    try:
        resp = requests.get(url)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        #body = soup.body
        links = parse_link_on_page(url, soup)

        assets = get_assets(url, soup)

        return links + assets
    except TypeError as e:
        print(e)
        print("Got a TypeError, probably got a None that we tried to iter")
        return []
    except IndexError as e:
        print(e)
        print("No usefuel links?")
        return []
    except AttributeError as e:
        print(e)
        print("Likely got None for links")
        return []

def main():
    starting_url = "https://gocardless.com/"
    how_many = 1
    parse_us = [starting_url]
    total_data = parse_us
    links = []
    debug_counter = 0
    link_asset_tree = {}

    while len(parse_us) != 0 or debug_counter != 10:

        for link in parse_us:
            data_and_assets = get_content(link)
            assets = [asset for asset in data_and_assets if is_asset(asset)]
            data = [link for link in data_and_assets if not is_asset(link)]
            links = links + data
            temp_asset_tree = {"url": link, "assets": assets}
            if len(link_asset_tree) == 0:
                link_asset_tree = dict(temp_asset_tree)
            else:
                link_asset_tree = dict(link_asset_tree.items() + temp_asset_tree.items())

        #data_and_assets = [get_content(link) for link in parse_us]
        #links = [url for url_list in links for url in url_list]
        debug_counter = debug_counter + 1
        parse_us = [link for link in links if link not in total_data]
        total_data = total_data + parse_us
        if len(parse_us) == 0:
            print("no more links left!")
            break



    with open('url.txt','w') as f:
        f.write(str(total_data))

    with open('assets.json', 'w') as fp:
        json.dump(link_asset_tree, fp, sort_keys=True, indent=4)

if __name__ == '__main__':
    main()
