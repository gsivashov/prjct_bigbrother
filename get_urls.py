import re
from pathlib import Path
from datetime import date
from google.cloud import bigquery

DATE = date.today().strftime('%Y-%m-%d')

PROJECTS = {
    'anibis': ['ebay.ch', 'tutti.ch'],
    'immoscout24': ['homegate.ch', 'immostreet.ch', 'comparis.ch'],
    'autoscout24': ['carforyou.ch', 'autolina.ch', 'comparis.ch'],
    'motoscout24': ['carforyou.ch', 'autolina.ch', 'comparis.ch'],
    'financescout24': ['ubs.com', 'comparis.ch', 'bonus.ch', 'migrosbank.ch']
}


def compose_query(date, project, competitor):
    client = bigquery.Client.from_service_account_json(
        'gabq_client_secrets.json')

    query = f'''
        SELECT
            DISTINCT url
        FROM
            `project-owl-277008.real_visibility.{project}_serp`
        WHERE
            date = '{date}'
            AND type = 'organic'
            AND domain = 'www.{competitor}'
            '''
    query_job = client.query(query)

    results = query_job.result()

    return results


def file_name(project, competitor):
    return f'{project}_{re.sub("(.com|.ch)", "", competitor)}_links.txt'


def get_url_list(project, competitor):
    try:
        with open(Path().cwd() / 'links' / file_name(project, competitor)) as f:
            res = [row.strip() for row in f]
            return res
    except:
        with open(Path().cwd() / 'links' / file_name(project, competitor), 'w'):
            return []


def receive_links():

    for project in PROJECTS:
        for competitor in PROJECTS[project]:
            new_urls = [row.url for row in compose_query(
                DATE, project, competitor)]

            old_urls = get_url_list(project, competitor)

            with open(Path().cwd() / 'links' / file_name(project, competitor), 'w', encoding='utf-8') as out:
                for url in set(new_urls + old_urls):
                    out.write(f'{url}\n')


if __name__ == '__main__':
    receive_links()
