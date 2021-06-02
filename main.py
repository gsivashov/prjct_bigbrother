import re
import os
from pathlib import Path
from crawl import start_crawl
from get_urls import PROJECTS, receive_links, file_name


def write_file(response, project, folder):
    for url, h1, title, description, text in response:
        filename = f'{h1.replace("/","").replace(" ","_")}.txt'

        if not os.path.exists(f'{project}/{folder}'):
            os.makedirs(f'{project}/{folder}')

        with open(Path.cwd() / project / folder / filename, 'w', encoding='utf-8') as txt_file:
            txt_file.write(
                f'URL: {url}\nTitle: {title}\nDescription: {description}\n\n{text}')


def main():
    receive_links()

    for project in PROJECTS:
        for competitor in PROJECTS[project]:
            clean_comp = re.sub('(.com|.ch)', '', competitor)
            response = start_crawl(Path().cwd() / 'links' / file_name(project, competitor),
                                   clean_comp)
            write_file(response, project, clean_comp)


if __name__ == '__main__':
    main()
