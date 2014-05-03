#   Copyright 2013 Nathan C. Keim
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from urllib2 import URLError
from workflow import web

def urljoin(*args):
    return '/'.join(s.strip('/') for s in args if s)

def get_nblist(url, path=''):
    """Returns list of raw information about objects in 'path'"""
    try:
        resp = web.get(urljoin(url, 'api/notebooks', path))
    except URLError:
        raise URLError('Unable to reach server %s' % url)
    resp.raise_for_status()
    return resp.json()

def get_all_notebooks(url, path=''):
    """Returns list of info about all notebooks, recursively.
    
    Each item is a dict that includes "name" and "path" entries.
    """
    notebooks = get_nblist(url, path)
    dirs = [item['name'] for item in notebooks if item['type'] == 'directory']

    for d in dirs:
        notebooks.extend(get_all_notebooks(url, path.strip('/') + '/' + d))

    return notebooks


