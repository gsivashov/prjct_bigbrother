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
    with open('user_agent.txt') as ua:
        user_agent_list = [agent.strip() for agent in ua]

    user_agent = random.choice(user_agent_list)
    headers = {"User-Agent": user_agent}

    session = HTMLSession()
    try:
        response = session.get(
            url.strip(),
            headers=headers,
            timeout=20)
        if response.status_code == 200:
            print(url.strip())
            return response
        else:
            print(
                f'-----Skipped {url.strip()} because {response.status_code}-----')
            return url
    except Exception as e:
        print(f'::::: {url.strip()} ERROR -----> {e} :::::')


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

            sleep(random.randrange(2, 5))

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
