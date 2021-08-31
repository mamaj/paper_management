import yaml
from mendeley import Mendeley
import pathlib

    
def auth(path='mendeley.yml'):

    mendeley_udata = read_yml(path)
    if mendeley_udata is None: return None

    # These values should match the ones supplied when registering your application.
    mendeley = Mendeley(
        mendeley_udata['client_id'],
        client_secret=mendeley_udata['client_secret'],
        redirect_uri=mendeley_udata['redirect_uri']
    )
    auth = mendeley.start_authorization_code_flow()

    # The user needs to visit this URL, and log in to Mendeley.
    login_url = auth.get_login_url()

    print(login_url)

    auth_response = input("Enter URL")
    # auth_response = "http://localhost:8090/?code=Mi39zAvPbt7jTTKXygM-HfQeQxg&state=TYKGB2JYY60CY96Y91U2TAYHZD0EZZ"

    # After logging in, the user will be redirected to a URL, auth_response.
    session = auth.authenticate(auth_response)

    print(session.profiles.me.display_name)

    return session


def ccauth(path='mendeley.yml'):

    mendeley_udata = read_yml(path)
    if mendeley_udata is None: return None

    mendeley = Mendeley(
        mendeley_udata['client_id'],
        client_secret=mendeley_udata['client_secret'],
    )

    auth = mendeley.start_client_credentials_flow()
    return auth.authenticate()


def read_yml(path='mendeley.yml'):
    path = pathlib.Path(path)
    if path.exists():
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)


def get_folders(session):
        url = session.host + '/folders'
        folders = []
        while True:
            res = session.get(url) 
            folders += res.json() 
            if 'next' not in res.links.keys():
                break
            else:
                url = res.links['next']['url']

        id2name = {f['id']:f['name'] for f in folders}
        name2parent = {f['name']: id2name[f.get('parent_id', f.get('id'))] for f in folders}
        return folders, id2name, name2parent

