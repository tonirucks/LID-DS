import requests
import json

from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3 import Retry


class Request:
    def __init__(self, host, user, password):
        retry_strategy = Retry(
            total=10,
            # status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)
        self._auth = HTTPBasicAuth(user, password)
        self.http.auth = self._auth

        if host.startswith("http"):
            self._conn_string = host
        else:
            self._conn_string = "http://%s" % host

    def extend(self, path):
        return Request(self._join_urls(path), self._auth.username, self._auth.password)

    def get(self, path="", **kwargs):
        return self.http.get(self._join_urls(path), **kwargs)

    def put(self, path="", **kwargs):
        return self.http.put(self._join_urls(path), **kwargs)

    def post(self, path="", **kwargs):
        return self.http.post(self._join_urls(path), headers={'Content-Type': 'application/json'}, **kwargs)

    def head(self, path, **kwargs):
        return self.http.head(self._join_urls(path), **kwargs)

    def _join_urls(self, *args):
        return "/".join([self._conn_string, *args])


class Server:
    def __init__(self, host, user, password):
        self.request = Request(host, user, password)

    def create(self, name):
        self.request.put(name)
        return Database(self.request.extend(name))

    def get(self, name):
        self.request.head(name)
        return Database(self.request.extend(name))

    def info(self):
        return self.request.get().json()


class Database:
    def __init__(self, request):
        self.request = request

    def all_ids(self):
        rows = self.request.get("_all_docs").json()['rows']
        return list(map(lambda x: x['id'], rows))

    def get(self, id):
        return self.request.get(id).json()

    def save(self, doc):
        res = self.request.post(data=json.dumps(doc)).json()
        if res['ok']:
            return {**doc, '_id': res['id'], '_rev': res['rev']}
        else:
            raise Exception("Could not be saved")


if __name__ == '__main__':
    y = Server("localhost:5984", "admin", "admin").info()
    print(y)
