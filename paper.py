import requests
import pprint

class Paper():
    def __init__(self, **kw):
        self.title = kw.get('title')
        self.abstract = kw.get('abstract')
        self.proceeding = kw.get('proceeding')
        self.citations = kw.get('citations')
        self.influential_citations = kw.get('influential_citations')
        self.authors = kw.get('authors', [])
        self.published = kw.get('published')
        self.folders = kw.get('folders', [])
        self.urls = kw.get('urls', [])
        self.sc_id = kw.get('sc_id')
        self.arxiv_id = kw.get('arxiv_id')
        self.pwc_id = kw.get('pwc_id')
        self.mendeley_id = kw.get('mendeley_id')
        self.doi = kw.get('doi')

        assert type(self.folders) == type(self.urls) == type(self.authors) == list

    def search_sc(self):
        url = 'https://api.semanticscholar.org/graph/v1/paper'
        params = {'fields': ','.join(
            ['citationCount',
            'influentialCitationCount',
            'externalIds',
            'url',
            'year',
            'title',
            'abstract',
            'authors']
        )}
        
        if self.sc_id: id = self.sc_id 
        elif self.arxiv_id: id = f"ARXIV:{self.arxiv_id}"
        elif self.doi: id = f"DOI:{self.doi}" 
        else: id = None

        if id:
            resp = requests.get(f'{url}/{id}', params=params)
            if resp.ok: return resp.json()

        if self.title:
            print('searching by title')
            params['query'] = self.title 
            params['limit'] = 1
            resp = requests.get(f'{url}/search', params=params)
            if resp.ok:
                return resp.json().get('data')[0]   

    
    def fill_sc(self, doc=None):
        doc = doc or self.search_sc()

        self.title = self.title or doc.get('title')
        self.abstract = self.abstract or doc.get('abstract')
        self.citations = self.citations or doc.get('citationCount')
        self.influential_citations = self.influential_citations or doc.get('influentialCitationCount')
        self.published = self.published or doc.get('year')
        self.sc_id = self.sc_id or doc.get('paperId')
        self.arxiv_id = self.arxiv_id or doc.get('externalIds', {}).get('ArXiv')
        self.authors = self.authors or self.sc_author_list(doc.get('authors'))
        self.update_urls(doc.get('url'))

        return self

    def search_arxiv(self):
        pass

    def fill_arxiv(self, doc):
        pass
        
    def search_pwc(self):
        url = 'https://paperswithcode.com/api/v1/papers/'
        if self.pwc_id:
            resp = requests.get(url + self.pwc_id)
            return resp.json()

        elif self.arxiv_id:
            params = {'arxiv_id': self.arxiv_id}
            resp = requests.get(url, params=params)

        elif self.title:
            params = {'items_per_page': 1, 'title': self.title}
            resp = requests.get(url, params=params)
        else:
            return None

        if resp.ok and resp.json().get('count'):
            return resp.json()['results'][0]
            
        

    def fill_pwc(self, doc=None):
        doc = doc or self.search_pwc()

        self.title = self.title or doc.get('title')
        self.abstract = self.abstract or doc.get('abstract')
        self.proceeding = self.proceeding or doc.get('proceeding')
        self.citations = self.citations or doc.get('citations')
        self.influential_citations = self.influential_citations or doc.get('influential_citations')
        self.authors = self.authors or doc.get('authors')
        self.published = self.published or doc.get('published')
        self.sc_id = self.sc_id or doc.get('id')
        self.arxiv_id = self.arxiv_id or doc.get('arxiv_id')
        self.update_urls(doc.get('url_abs'))
        self.update_urls(doc.get('conference_url_abs'))

        return self

    def search_mendeley_catalog(self, session):
        url = 'https://api.mendeley.com/metadata'

        params = {}
        if self.title: params['title'] = self.title
        if self.arxiv_id: params['arxiv'] = self.arxiv_id
        if self.doi: params['doi'] = self.doi
        if self.authors: params['authors'] = self.authors[0]

        resp = session.get(url, params=params)
        if resp.ok:
            if 'score' in resp.json():
                if resp.json().get('score') > 60:
                    cat_id = resp.json().get('catalog_id')
                    url = f'https://api.mendeley.com/catalog/{cat_id}'
                    resp = session.get(url)
                else: 
                    return None
            return resp.json()

        

    def fill_mendeley(self, fnames, doc=None, session=None):
        doc = doc or self.search_mendeley_catalog(session)
        if type(doc) is not dict:
            doc = vars(doc)

        self.title = self.title or doc.get('title')
        self.authors = self.authors or self.mendeley_author_list(doc.get('authors'))
        self.published = self.published or doc.get('year')
        self.folders = self.folders or self.mendeley_folder_list(doc, fnames)
        self.abstract = self.abstract or doc.get('abstract')
        self.mendeley_id = self.mendeley_id or doc.get('id')
        self.proceeding = self.proceeding or doc.get('source')
        self.update_urls(doc.get('websites'))
        self.arxiv_id = self.arxiv_id or doc.get('identifiers', {}).get('arxiv')
        return self

    def mendeley_author_list(self, authors):
        if not authors: return []
        res = []
        for a in authors:
            res.append(f"{a.get('first_name')} {a.get('last_name')}".strip())
        return res

    def sc_author_list(self, authors):
        if not authors: return []
        return [a['name'] for a in authors]

    def mendeley_folder_list(self, doc, fnames):
        if 'folder_uuids' in doc.get('json', {}).keys():
            return [fnames[fuuid] for fuuid in doc.get('json')['folder_uuids']]
        else:
            return []

    def update_urls(self, url):
        if not url: return
        if type(url) is str:
            if url not in self.urls:
                self.urls.append(url)
        elif hasattr(url, '__iter__'):
            self.urls.extend(u for u in url if u not in self.urls)

    def __repr__(self):
        params = vars(self)
        params = {k: v for k, v in params.items() if v }
        return pprint.pformat(params)