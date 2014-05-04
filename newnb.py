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

import sys, json, getopt

from urllib import quote
from urllib2 import URLError

from util import urljoin, get_nblist
from workflow import Workflow, web

def newnb(url, path, copy=None):
    """Create new untitled notebook at 'path'
    
    Server base URL is 'url'

    Returns name of the new notebook file.
    """
    # See IPython/html/services/notebooks/handlers.py for API details.

    # Compare directory contents before and after new notebook creation.
    names = [nb['name'] for nb in get_nblist(url, path) if nb['type'] == 'notebook']

    post_url = urljoin(url, 'api/notebooks', quote(path)).strip('/')
    if copy is not None:
        data = json.dumps({'copy_from': copy})
    else:
        data = ''
    try:
        resp = web.post(post_url, data=data)
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
    optslist, args = getopt.getopt(wf.args, 'c')
    opts = dict(optslist)
    path = args[0]

    url = wf.settings.get('server', 'http://127.0.0.1:8888')

    if '-c' in opts:
        # Copy mode: We were passed either notebook.ipynb or path/to/notebook.ipynb
        pathparts = ('/' + path.strip('/')).split('/')
        from_nbname = pathparts[-1]
        dirpath = urljoin(*pathparts[:-1])
        sys.stderr.write('\n' + repr(pathparts) + '\n')
        nbname = newnb(url, dirpath, copy=from_nbname)
    else:
        # We were passed the path to a directory in which to create a blank notebook.
        dirpath = path
        sys.stderr.write('\n' + dirpath + '\n')
        nbname = newnb(url, dirpath)

    nb_user_url = urljoin(url, 'notebooks', quote(urljoin(dirpath, nbname)))

    sys.stdout.write(nb_user_url)
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
