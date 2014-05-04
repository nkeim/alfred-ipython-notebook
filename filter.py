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

from util import urljoin, get_all_notebooks

from workflow import Workflow, ICON_WEB, ICON_WARNING

def sort_most_recent(nblist):
    # Sort: Notebooks only, most recent first.
    r = [nb for nb in nblist if nb['type'] == 'notebook']
    r.sort(key=lambda nb: nb['last_modified'], reverse=True)
    return r

def add_root_item(wf, url, directories_only=False):
    # Make the first item a link to the root path
    nburl = urljoin(url, '')
    if directories_only:
        wf.add_item(title='/',
                subtitle='New notebook at ' + nburl, 
                arg='', valid=True, icon=ICON_WEB)
    else:
        wf.add_item(title='Browse all notebooks',
                subtitle=nburl, arg=nburl, valid=True, icon=ICON_WEB)


def main(wf):
    optslist, args = getopt.getopt(wf.args, 'rd')
    opts = dict(optslist)
    if args:
        query = args[0]
    else:
        query = None

    sort_by_modtime = '-r' in opts
    directories_only = '-d' in opts

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
            add_root_item(wf, url, directories_only=directories_only)
            wf.add_item('No notebooks found', icon=ICON_WARNING,
                     subtitle='On server %s' % url)
            wf.send_feedback()
            return 0
    elif not sort_by_modtime:
        # If no query and alphabetical sorting, show root.
        add_root_item(wf, url, directories_only=directories_only)

    # Most recent first
    if sort_by_modtime:
        # Notebooks only, most recent first.
        nblist = sort_most_recent(nblist)
    elif directories_only:
        nblist = [nb for nb in nblist if nb['type'] == 'directory']

    # Build results
    for nb in nblist:
        # We use urljoin() twice to get the right behavior when path is blank
        if nb['name'].endswith('.ipynb'):
            nbname = urljoin(nb['path'], nb['name'][:-len('.ipynb')])
        elif nb['type'] == 'directory':
            nbname = urljoin(nb['path'], nb['name']) + '/'
        else:
            nbname = nb['name']

        nb_user_url = urljoin(url, 'notebooks', urljoin(nb['path'], nb['name']))
        if directories_only:
            # We return only the path information, since newnb.py has to use the API anyhow.
            nburl = urljoin(nb['path'], nb['name']) + '/'
            subtitle = 'New notebook at ' + nb_user_url
        else:
            nburl = nb_user_url
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
