
import json
import urllib
from urlparse import urljoin


class Octopart:
    class PartsMatch:
        def __init__(self, octopart):
            self._octopart = octopart
            self._queries = []

        def query_mpn(self, mpn, brand, reference):
            self._queries.append({
                "mpn": mpn,
                "brand": brand,
                "reference": reference}
            )
            return self

        def execute(self):
            return self._octopart.execute("parts/match", {
                "queries": json.dumps(self._queries)
            })

    def __init__(self, baseuri, apikey):
        self._baseuri = baseuri
        self._apikey = apikey

    def partsmatch(self):
        return Octopart.PartsMatch(self)

    def execute(self, path, parameters):
        parameters.update({"apikey": self._apikey})
        params = urllib.urlencode(parameters)
        url = urljoin(self._baseuri, path)

        response = urllib.urlopen("%s?%s" % (url, params))
        if response.getcode() != 200:
            raise IOError("Unable to comply... code=" + str(response.getcode()) + ": " + str(response.info()))

        return json.loads(response.read())

