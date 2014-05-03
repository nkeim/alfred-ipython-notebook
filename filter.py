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

def add_root_item(wf, url):
    # Make the first item a link to the root path
    nburl = urljoin(url, '')
    wf.add_item(title='Browse all notebooks',
            subtitle=nburl, arg=nburl, valid=True, icon=ICON_WEB)


def main(wf):
    opts, args = getopt.getopt(wf.args, 'r')
    if args:
        query = args[0]
    else:
        query = None

    sort_by_modtime = '-r' in dict(opts)

    url = wf.settings.get('server', 'http://127.0.0.1:8888')

    def get_nb():
        return get_all_notebooks(url)
    # Retrieve directory and cache for 30 seconds
    nblist = wf.cached_data('nblist', get_nb, max_age=30)

    if query:
        nblist = wf.filter(query, nblist, 
                key=lambda nb: nb['path'] + '/' + nb['name'] )
    elif not sort_by_modtime:
        add_root_item(wf, url)

    if not nblist:
        add_root_item(wf, url)
        wf.add_item('No notebooks found', icon=ICON_WARNING,
                 subtitle='On server %s' % url)
        wf.send_feedback()
        return 0

    if sort_by_modtime:
        # Notebooks only, most recent first.
        nblist = sort_most_recent(nblist)

    for nb in nblist:
        # We use urljoin() twice to get the right behavior when path is blank
        nburl = urljoin(url, 'notebooks', urljoin(nb['path'], nb['name']))
        if nb['name'].endswith('.ipynb'):
            nbname = urljoin(nb['path'], nb['name'][:-len('.ipynb')])
        elif nb['type'] == 'directory':
            nbname = nb['name'] + '/'
        else:
            nbname = nb['name']
        wf.add_item(title=nbname,
                subtitle=nburl,
                arg=nburl,
                valid=True,
                icon=ICON_WEB)

    wf.send_feedback()
    return 0

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
