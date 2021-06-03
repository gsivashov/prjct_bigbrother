import csv
import random
import logging

from time import sleep
from pathlib import Path
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor


def nature_header():

    return {
        # ':scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru-UA;q=0.7,ru;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': 'launchDarklyUserID=1be25e74-b25e-4388-8d35-2113a991f1c3; _gcl_au=1.1.632620136.1622454271; _ga=GA1.2.1920239414.1622454271; _hjid=e6b8b746-6d0e-4a85-87b3-6d07552132a1; dakt_2_uuid=eff18eb25800201a41f1a711d5101566; dakt_2_uuid_ts=1622454273518; dakt_2_version=0.8.4; __gads=ID=288f7e06bc2d46c2:T=1622453928:S=ALNI_MajeY-MIb4qEHk9MKAhy8ewtAutpA; _gid=GA1.2.1673944572.1622630398; _hjTLDTest=1; _fbp=fb.1.1622630398604.348514564; __cf_bm=240c928594a228c8a25fbaa74f3744ba7547c484-1622638471-1800-AXEhW+pu8phbOeYB7RrZtyK+Sq+OCcIZ30KAThkVDQGkDIPZoMcm4U9Xr/2mOshbFd9Wy4s9j1U5p7Fedpw6s2AkfMMdK168CEEsH2aGoAVw3G3zdPqKB86vsrfZHVaCyw==; _hjIncludedInSessionSample=1; _hjAbsoluteSessionInProgress=0; _dc_gtm_UA-511168-1=1; _uetsid=e07e56c0c38e11eb9fbf0db21e1b8d37; _uetvid=cd0ca1d0c1f411eb907fbfdb73231545; outbrain_cid_fetch=true; _gat_UA-511168-1=1; dakt_2_session_id=902c253e2a6e589e006392a2928c544a',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }


def get_response(url):
    with open('user_agent.txt') as ua:
        user_agent_list = [agent for agent in ua]

    user_agent = random.choice(user_agent_list)
    headers = {"User-Agent": user_agent}
    # headers = nature_header()

    session = HTMLSession()
    try:
        response = session.get(
            url.strip(),
            headers=headers,
            timeout=10)
        if response.status_code == 200:
            print(url.strip())
            return response
        else:
            print(
                f'-----Skipped {url.strip()} because {response.status_code}-----')
            return url
    except:
        print(f'-----{url.strip()} timed out-----')


def chunkinator(file, size, index=0, delimiter='|'):
    '''
    Spilts file to chunks
    You need to pass:
    size of chunk;
    index of column with keywords;
    delimiter for columns
    '''
    chunk = []
    with open(file) as file:
        reader = csv.reader(file, delimiter=delimiter)

        for line in reader:
            if not line:
                continue

            keyword = line[index].strip().lower()
            chunk.append(keyword)
            if len(chunk) % size == 0:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


def getTags(response):

    try:
        h1 = ' '.join(response.html.xpath('//h1')
                      [0].full_text.split('\n')).strip()
        # if response.html.xpath('//h1/span/text()'):
        #     h1 = response.html.xpath('//h1/span/text()')[0]
        # else:
        #     h1 = response.html.xpath('//h1/text()')[0].strip()
    except:
        h1 = 'No h1 found'

    try:
        title = response.html.xpath('//title/text()')[0]
    except:
        title = 'No Title found'

    try:
        description = response.html.xpath(
            '//meta[@name="description"]/@content')[0]
    except:
        description = 'No Description found'

    return h1, title, description


def getTextContent(response):

    try:
        article = response.html
    except:
        return None

    soup = BeautifulSoup(article.html, features='lxml')

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.body.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text


# def start_crawl(params):
#     start_file = str(params.file)
#     folder = str(params.folder)

def start_crawl(file, folder):
    start_file = str(file)
    folder = str(folder)

    size = 5
    with ThreadPoolExecutor(max_workers=size) as executor:
        for chunk in chunkinator(start_file, size):
            f = executor.map(get_response, chunk, chunksize=size)

            sleep(random.randrange(4))

            for link in f:
                h1, title, description = getTags(link)

                text = getTextContent(link)

                if text:
                    yield link.url, h1, title, description, text


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        help='file path',
        default='homegate_links.txt',
    )
    parser.add_argument(
        '--folder',
        type=str,
        help='folder path',
        default='homegate',
    )
    params = parser.parse_args()

    logging.basicConfig(
        filename=Path().cwd() / 'logs' / 'errors.log',
        filemode='a',
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    start_crawl(params)
