# (C) British Crown Copyright 2013 - 2014, Met Office
#
# This file is part of Iris-code-generators.
#
# Iris-code-generators is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Iris-code-generators is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris-code-generators.  If not, see <http://www.gnu.org/licenses/>.

import metarelate.fuseki as fuseki
from iris.fileformats.pp import STASH

import gen_helpers


HEADER = '''
"""
Auto-generated from SciTools/iris-code-generators:tools/gen_stash_refs.py
Relates grid code and field code to the stash code.

"""
'''


CODE_PREAMBLE = ("from collections import namedtuple\n\n\n"
                 "Stash = namedtuple('Stash', 'grid_code field_code')\n\n\n")


def write_cross_reference_module(module_path, xrefs):
    gen_helpers.prep_module_file(module_path)
    with open(module_path, 'a') as module_file:
        module_file.write(HEADER)
        module_file.write(CODE_PREAMBLE)
        module_file.write('STASH_TRANS = {\n')
        for xref in xrefs:
            stash = xref.get('stash')
            try:
                STASH.from_msi(stash.replace('"', ''))
            except ValueError:
                msg = ('stash code is not of a recognised'
                       '"m??s??i???" form: {}'.format(stash))
                print msg
            grid = xref.get('grid')
            try:
                int(grid)
            except ValueError:
                msg = ('grid code retrieved from STASH lookup'
                       'is not an interger: {}'.format(grid))
                print msg
            lbfc = xref.get('lbfcn')
            try:
                int(lbfc)
            except (ValueError, TypeError):
                lbfc = 0
            module_file.write(
                "    {}: Stash({}, {}),\n".format(stash, grid, lbfc))
        module_file.write('}\n')


def stash_grid_codes(fu_p):
    query = '''
    SELECT ?stash ?grid ?lbfcn
    WHERE
    {
      GRAPH <http://um/stashconcepts.ttl>
        {
          ?stashcode moumdpC4:Grid ?grid ;
          <http://www.w3.org/2004/02/skos/core#notation> ?stash .
          OPTIONAL {?stashcode moumdpC4:PPFC ?lbfc .}
        }
      OPTIONAL
      {
        GRAPH <http://um/fieldcode.ttl>
          {
            ?lbfc <http://www.w3.org/2004/02/skos/core#notation> ?lbfcn
          }
      }
    }
    order by ?stashcode
    '''
    xrefs = fu_p.run_query(query)
    return xrefs


if __name__ == '__main__':
    with fuseki.FusekiServer() as fu_p:
        xrefs = stash_grid_codes(fu_p)
        outfile = '../outputs/iris/fileformats/_ff_cross_references.py'
        write_cross_reference_module(outfile, xrefs)
