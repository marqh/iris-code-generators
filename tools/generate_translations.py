# (C) British Crown Copyright 2013, Met Office
#
# This file is part of iris-code-generators.
#
# iris-code-generators is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iris-code-generators is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with iris-code-generators.  If not, see <http://www.gnu.org/licenses/>.
"""
Processing of metarelate content to provide Iris encodings for translation

"""

import datetime
import itertools
import time
from contextlib import contextmanager

import metocean.fuseki as fuseki
import translator.mappings as mappings

_HEADER = """# (C) British Crown Copyright 2012 - {}, Met Office
#
# This file is part of Iris.
#
# Iris is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Iris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris.  If not, see <http://www.gnu.org/licenses/>.
#
# DO NOT EDIT: AUTO-GENERATED

"""

yr = datetime.datetime.utcnow().year
_HEADER = _HEADER.format(yr)


_ICOL = 'import collections\n'

_CF_TUPLE_DEF = '''
CFname = collections.namedtuple('CFname', ['standard_name', 'long_name',
                                           'unit'])
'''


_BUILT_FILES = {'../outputs/um_cf_map.py': [_ICOL, _CF_TUPLE_DEF], }



@contextmanager
def atimer(name):
    """timer context manager for monitoring processes"""
    start = time.time()
    yield
    print '{}:'.format(name), '{}s'.format(int(time.time() - start))

_IRIS_FORMAT = '<http://www.metarelate.net/metOcean/format/cf>'

FORMATS = ['<http://www.metarelate.net/metOcean/format/um>']


def main():
    """
    creates the translations encodings in ../outputs

    """
    with fuseki.FusekiServer(3333) as fu_p:
        # generate translations
        format_maps = {}
        for fformat in FORMATS:
            print fformat, ' retrieving: '
            format_maps[fformat] = {'import': {}, 'export': {}}
            with atimer('imp retrieve_mappings'):
                # return the list of valid mapping from fformat to CF
                imports = fu_p.retrieve_mappings(fformat, _IRIS_FORMAT)
            with atimer('imp make_mappings'):
                # identify types for these mappings
                imp_maps = [mappings.make_mapping(amap) for
                            amap in imports]
                imp_maps.sort(key=type)
                for g_type, grp in itertools.groupby(imp_maps, key=type):
                    format_maps[fformat]['import'][g_type] = list(grp)
            with atimer('exp retrieve mappings'):
                # return the list of valid mapping from CF to fformat
                exports = fu_p.retrieve_mappings(_IRIS_FORMAT, fformat)
            with atimer('exp make_mappings'):
                # identify types for these mappings
                exp_maps = [mappings.make_mapping(amap)
                            for amap in exports]
                exp_maps.sort(key=type)
                for g_type, grp in itertools.groupby(exp_maps, key=type):
                    format_maps[fformat]['export'][g_type] = list(grp)
            print len(imports), ' imports, ', len(exports), 'exports'
        for afile in _BUILT_FILES:
            f = open(afile, 'w')
            f.write(_HEADER)
            for extras in _BUILT_FILES[afile]:
                f.write(extras)
            f.close()

        for fformat in FORMATS:
            # export translations to python code
            for direction in ['import', 'export']:
                with atimer('writing {}, {}'.format(fformat, direction)):
                    ports = format_maps[fformat][direction]
                    pkeys = ports.keys()
                    pkeys.sort(reverse=True, key=lambda acls: acls.__name__)
                    for map_type in pkeys:
                        print direction
                        print map_type.__name__
                        if isinstance(None, map_type):
                            ec = 'Some {} {} mappings not categorised'
                            ec = ec.format(fformat, direction)
                            print ec
                        else:
                            if map_type.in_file not in _BUILT_FILES:
                                ec = '{} writing to unmanaged file {}'
                                ec = ec.format(map_type,
                                               map_type.in_file)
                                raise ValueError(ec)
                            map_str = map_type.encode_mappings(ports[map_type],
                                                               fu_p)
                            with open(map_type.in_file, 'a') as ifile:
                                ifile.write(map_str)


if __name__ == '__main__':
    with atimer('main'):
        main()
