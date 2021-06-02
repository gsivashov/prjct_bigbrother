import os
import csv
import random
import logging

from time import sleep
from pathlib import Path
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor


def get_response(url):
    user_agent_list = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    ]

    # proxy_list = [
    #     "178.198.228.58:808",
    #     "185.12.6.76:3128",
    #     "64.110.145.126:3128",
    #     "178.22.70.89:3128",
    #     "185.12.6.87:3128",
    #     "185.12.6.95:3128",
    #     "213.167.224.56:3838",
    #     "178.22.70.66:3128",
    #     "141.8.224.29:80",
    #     "89.186.193.238:80",
    #     "141.8.224.194:80",
    #     "185.12.6.85:3128",
    #     "178.22.70.38:3128",
    #     "141.8.226.175:80",
    #     "213.167.224.91:3838",
    #     "213.167.224.216:3838",
    #     "178.192.251.188:3128",
    #     "185.12.6.254:3128",
    #     "178.22.70.126:3128",
    #     "212.243.94.98:8080"
    # ]

    user_agent = random.choice(user_agent_list)
    # proxy = random.choice(proxy_list)
    headers = {"User-Agent": user_agent}
    session = HTMLSession()
    try:
        response = session.get(
            url.strip(),
            headers=headers,
            # proxies={'https': proxy},
            timeout=5)
        if response.status_code == 200:
            print(url.strip())
            return response
        else:
            print(
                f'-----Skipped {url.strip()} because {response.status_code}-----')
            return url
    except:
        print(f'{url.strip()} timed out')


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
        # next(reader)

        for line in reader:
            # line = line.strip()
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
        h1 = ''.join(response.html.xpath('//h1/text()')
                     ).replace('?', '_').replace(':', '_').strip()
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

                    # filename = f'{h1.replace("/","").replace(" ","_")}.txt'

                    # if not os.path.exists(folder):
                    #     os.makedirs(folder)

                    # with open(Path.cwd() / folder / filename, 'w', encoding='utf-8') as txt_file:
                    #     txt_file.write(
                    #         f'URL: {link.url}\nTitle: {title}\nDescription: {description}\n\n{text}')


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
