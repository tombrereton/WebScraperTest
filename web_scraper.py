import bs4 as bs
import requests
import string

starting_url = "https://gocardless.com/"


def handle_local_links(url, link):
    if link.startswith('/'):
        return ''.join([url, link])
    else:
        return link


def get_links(url):
    """

    :param url:
    :return:
    """
    try:
        resp = requests.get(url)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        body = soup.body
        links = [link.get('href') for link in body.find_all('a')]
        links = [handle_local_links(url, link) for link in links]
        links = [str(link.encode("ascii")) for link in links]
        return links
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
    how_many = 1
    parse_us = [starting_url]

    data = get_links(link for link in parse_us)
    data = [url for url_list in data for url in url_list]

    with open('url.txt','w') as f:
        f.write(str(data))

if __name__ == '__main__':
    main()
