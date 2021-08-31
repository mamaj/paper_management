from notion_client import Client
import pathlib
from paper import Paper
import yaml


def auth(secret_path='./notion.yml'):
    secret = read_yml(secret_path)
    return Client(auth=secret['NOTION_SECRET'])

def get_dbid(secret_path='./notion.yml'):
    return read_yml(secret_path)['db_id']

def get_papers(notion, db_id):
    papers = notion.databases.query(db_id)

    for paper in papers['results']:
        paper = paper['properties']

        papers_list = []
        if 'citations' not in paper:
            title = paper['title']['title'][0]['plain_text']
            urls = paper['urls']['url'].split(',')
            arxiv_url = [u for u in urls if 'arxiv' in u]
            if arxiv_url:
                arxiv_id = arxiv_url[0].split('/')[-1]
            else:
                arxiv_id = ''  

            p = Paper(title=title, arxiv_id=arxiv_id)
            p.fill_sc()
            papers_list.append(p)    


def read_yml(path):
    path = pathlib.Path(path)
    if path.exists():
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)