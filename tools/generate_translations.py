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


import itertools
import time
from contextlib import contextmanager

import metocean.queries as moq
import metocean.fuseki as fuseki
import translator.mappings as mappings

HEADER = """# (C) British Crown Copyright 2013, Met Office
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
"""

HEADER += '''
# DO NOT EDIT: AUTO-GENERATED

'''


ICOL = 'import collections\n'

CF_TUPLE_DEF = '''
CFname = collections.namedtuple('CFname', ['standard_name', 'long_name',
                                           'unit'])
'''


# END_DICT = '''
# }
# '''

BUILT_FILES = {'../outputs/um_cf_map.py': [ICOL, CF_TUPLE_DEF], }


def str_line_sort(st):
    sort_st = st.split('\n')
    sort_st.sort()
    st = '\n'.join(sort_st)
    return st


def dict_line_sort(st):
    sort_st = st.split('\n')[0:-2]
    try:
        sort_st.sort(
            key=lambda str: int(str.split(':')[0].strip().replace('"', '')))
        st = '\n'.join(sort_st)
    except ValueError:
        st = str_line_sort(st)
    return st


@contextmanager
def atimer(name):
    start = time.time()
    yield
    print '{}:'.format(name), '{}s'.format(int(time.time() - start))

iris_format = '<http://www.metarelate.net/metOcean/format/cf>'

formats = ['<http://www.metarelate.net/metOcean/format/um>']


def bodc_udunit_fix(units):
    """
    helper function to update syntax in use in BODC server to conform
    to udunits strings

    """
    units = units.strip('"')
    units = units.replace('Dmnless', '1')
    units = units.replace('#', '1')
    units = units.replace('deg', 'degree')
    units = units.replace('degreeree', 'degree')
    if units.startswith("'canonical_units': '/"):
        denom = units.split("'canonical_units': '/")[-1]
        units = "'canonical_units': '1/" + denom
    ## wrong, dB should be a recognised unit
    units = units.replace("'dB'", "'1'")
    return units


def main():
    """
    creates the translations encodings in ../outputs

    """
    with fuseki.FusekiServer(3333) as fu_p:
        # generate translations
        format_maps = {}
        for fformat in formats:
            print fformat, ' retrieving: '
            format_maps[fformat] = {'import': {}, 'export': {}}
            with atimer('imp retrieve_mappings'):
                # return the list of valid mapping from fformat to CF
                imports = fu_p.retrieve_mappings(fformat, iris_format)
            with atimer('imp make_mappings'):
                # identify types for these mappings
                imp_maps = [mappings.make_mapping(amap, fu_p) for
                            amap in imports]
                imp_maps.sort(key=type)
                for g_type, grp in itertools.groupby(imp_maps, key=type):
                    format_maps[fformat]['import'][g_type.__name__] = list(grp)
            with atimer('exp retrieve mappings'):
                # return the list of valid mapping from CF to fformat
                exports = fu_p.retrieve_mappings(iris_format, fformat)
            with atimer('exp make_mappings'):
                # identify types for these mappings
                exp_maps = [mappings.make_mapping(amap, fu_p)
                            for amap in exports]
                exp_maps.sort(key=type)
                for g_type, grp in itertools.groupby(exp_maps, key=type):
                    format_maps[fformat]['export'][g_type.__name__] = list(grp)
            print len(imports), ' imports, ', len(exports), 'exports'
        for afile in BUILT_FILES:
            f = open(afile, 'w')
            f.write(HEADER)
            for extras in BUILT_FILES[afile]:
                f.write(extras)
            f.close()

        for fformat in formats:
            for direction in ['import', 'export']:
                with atimer('writing {}, {}'.format(fformat, direction)):
                    ports = format_maps[fformat][direction]
                    pkeys = ports.keys()
                    pkeys.sort(reverse=True)
                    for map_set in pkeys:
                        print direction
                        print map_set
                        if map_set == 'NoneType':
                            ec = 'Some {} {} mappings not categorised'
                            ec = ec.format(fformat, direction)
                            print ec
                        else:
                            if ports[map_set][0].in_file not in BUILT_FILES:
                                ec = '{} writing to unmanaged file {}'
                                ec = ec.format(map_set,
                                               ports[map_set][0].in_file)
                                raise ValueError(ec)
                            map_str = ''
                            for port_mappings in ports[map_set]:
                                map_str += port_mappings.encode()
                            if ports[map_set][0].to_sort:
                                map_str = dict_line_sort(map_str)
                            if ports[map_set][0].container:
                                map_str = ports[map_set][0].container + map_str
                            if ports[map_set][0].closure:
                                map_str += ports[map_set][0].closure
                            with open(ports[map_set][0].in_file, 'a') as ifile:
                                ifile.write(map_str)


if __name__ == '__main__':
    with atimer('main'):
        main()
