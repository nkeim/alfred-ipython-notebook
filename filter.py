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

from util import urljoin, get_all_notebooks

from workflow import Workflow, ICON_WEB, ICON_WARNING

def main(wf):
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    url = wf.settings.get('server', 'http://127.0.0.1:8888')

    def get_nb():
        return get_all_notebooks(url)
    # Retrieve directory and cache for 30 seconds
    nblist = wf.cached_data('nblist', get_nb, max_age=30)

    if query:
        nblist = wf.filter(query, nblist, 
                key=lambda nb: nb['path'] + '/' + nb['name'] )
    else:
        # Return all notebooks, but make the first item a link to the root path
        nburl = urljoin(url, '')
        wf.add_item(title='Browse all notebooks',
                subtitle=nburl, arg=nburl, valid=True, icon=ICON_WEB)

    if not nblist:
         wf.add_item('No notebooks found', icon=ICON_WARNING,
                 subtitle='On server %s' % url)
         wf.send_feedback()
         return 0

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
