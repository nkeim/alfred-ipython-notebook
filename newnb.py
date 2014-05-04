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

import sys

from urllib2 import URLError

from util import urljoin, get_nblist
from workflow import Workflow, web

def newnb(url, path):
    """Create new untitled notebook at 'path'
    
    Server base URL is 'url'

    Returns name of the new notebook file.
    """
    # Compare directory contents before and after new notebook creation.
    names = [nb['name'] for nb in get_nblist(url, path) if nb['type'] == 'notebook']
    post_url = urljoin(url, 'api/notebooks', path).strip('/')
    try:
        resp = web.post(post_url, data='')
    except URLError:
        raise URLError('Unable to reach %s. Try the "nbserver" keyword.' % url)
    resp.raise_for_status()

    new_contents = get_nblist(url, path)
    new_names = [nb['name'] for nb in new_contents if nb['type'] == 'notebook']
    try:
        newnbname = list(set(new_names) - set(names))[0]
    except IndexError:
        raise RuntimeError('Notebook creation at %s appears to have failed.' % post_url)
    return newnbname

def main(wf):
    path = wf.args[0]

    url = wf.settings.get('server', 'http://127.0.0.1:8888')

    nbname = newnb(url, path)
    nb_user_url = urljoin(url, 'notebooks', urljoin(path, nbname))
    #sys.stderr.write('\n' + nb_user_url + '\n')

    sys.stdout.write(nb_user_url)
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
