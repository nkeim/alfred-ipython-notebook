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

import sys, getopt
from urllib import quote

from util import urljoin, get_all_notebooks

from workflow import Workflow, ICON_WEB, ICON_WARNING

def add_root_item(wf, url, mode=None):
    # Make the first item a link to the root path
    nburl = urljoin(url, '')
    if mode == 'new':
        wf.add_item(title='/',
                subtitle='New notebook at ' + nburl, 
                arg='', valid=True, icon=ICON_WEB)
    elif mode == 'copy':
        return # Can't copy the root directory
    else:
        wf.add_item(title='Browse all notebooks',
                subtitle=nburl, arg=nburl, valid=True, icon=ICON_WEB)


def main(wf):
    optslist, args = getopt.getopt(wf.args, 'rdc')
    opts = dict(optslist)
    if args:
        query = args[0]
    else:
        query = None

    sort_by_modtime = '-r' in opts
    if '-d' in opts:
        mode = 'new'
    elif '-c' in opts:
        mode = 'copy'
    else:
        mode = None

    url = wf.settings.get('server', 'http://127.0.0.1:8888')

    def get_nb():
        return get_all_notebooks(url)
    # Retrieve directory and cache for 30 seconds
    nblist = wf.cached_data('nblist', get_nb, max_age=30)

    # Filtering by query
    if query:
        nblist = wf.filter(query, nblist, 
                key=lambda nb: nb['path'] + '/' + nb['name'] )
        # No matches
        if not nblist:
            add_root_item(wf, url, mode=mode)
            wf.add_item('No notebooks found', icon=ICON_WARNING,
                     subtitle='On server %s' % url)
            wf.send_feedback()
            return 0
    elif not sort_by_modtime:
        # If no query and alphabetical sorting, show root.
        add_root_item(wf, url, mode=mode)

    if sort_by_modtime or mode == 'copy':
        # Notebooks only
        nblist = [nb for nb in nblist if nb['type'] == 'notebook']
    elif mode == 'new':
        # Directories only
        nblist = [nb for nb in nblist if nb['type'] == 'directory']

    if sort_by_modtime:
        # Most recent first
        nblist.sort(key=lambda nb: nb['last_modified'], reverse=True)

    # Build results output
    for nb in nblist:
        if nb['name'].endswith('.ipynb'):
            # We use urljoin() twice to get the right behavior when path is empty
            nbname = urljoin(nb['path'], nb['name'][:-len('.ipynb')])
        elif nb['type'] == 'directory':
            nbname = urljoin(nb['path'], nb['name']) + '/'
        else:
            nbname = nb['name']

        nb_user_url = urljoin(url, 'notebooks', urljoin(nb['path'], nb['name']))
        if mode == 'new':
            # We return only the path information, since newnb.py has to use the API anyhow.
            nburl = urljoin(nb['path'], nb['name']) + '/'
            subtitle = 'New notebook at ' + nb_user_url
        elif mode == 'copy':
            nburl = urljoin(nb['path'], nb['name']) + '/'
            subtitle = 'Make a copy of ' + nb_user_url
        else:
            # URL will be passed straight to opener, so must be quoted.
            arg = urljoin(nb['path'], nb['name'])
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            nburl = urljoin(url, 'notebooks', 
                    quote(arg, '/'))
            subtitle = nb_user_url
        wf.add_item(title=nbname,
                subtitle=subtitle,
                arg=nburl,
                valid=True,
                icon=ICON_WEB)

    wf.send_feedback()
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
