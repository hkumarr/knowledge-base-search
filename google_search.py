from googleapiclient.discovery import build

__author__ = 'chetannaik'


class Google:
    def __init__(self, api_key, cse_id):
        self._api_key = api_key
        self._cse_id = cse_id
        # Build a custom search service
        self._service = build("customsearch", "v1", developerKey=api_key)
        # Get the service as a Google API Resource
        self._cse = self._service.cse()

    def search(self, query, start):
        return self._cse.list(cx=self._cse_id,
                              q=query,
                              num=10,
                              start=start).execute()
