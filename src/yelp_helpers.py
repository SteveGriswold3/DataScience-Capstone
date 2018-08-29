from __future__ import print_function

import requests
import urllib
import yaml

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

GRANT_TYPE = 'client_credentials'


def load_api_key(filename='../.gitignore/yelp_api_key.yaml'):
    """Load Yelp API client ID and client secret and return them as a dictionary."""
    with open(filename) as f:
        return yaml.load(f)


def request(host, path, api_key, url_params=None):
    """Given an api_key, send a GET request to the API.

    Parameters
    ----------
    host : str
        The domain host of the API.
    path : str
        The path of the API after the domain.
    api_key: str
        client_secret.
    url_params : dict
        An optional set of query parameters in the request.

    Returns
    -------
    dict
        The JSON response from the request.

    Raises
    ------
    HTTPError
        An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.status_code, response.json()
