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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with iris-code-generators. If not, see <http://www.gnu.org/licenses/>.
"""
Classes for types of mapping, with a factory for creating instances

"""


import concepts


def _str_line_sort(st):
    """Helper function to sort a multi line string alphabetically"""
    sort_st = st.split('\n')
    sort_st.sort()
    st = '\n'.join(sort_st)
    return st


def _dict_line_sort(st):
    """Helper function to sort a multi line string numerically, if porssible,
    then alphabetically as a reserve

    """
    sort_st = st.split('\n')[0:-2]
    try:
        sort_st.sort(
            key=lambda str: int(str.split(':')[0].strip().replace('"', '')))
        st = '\n'.join(sort_st)
    except ValueError:
        st = _str_line_sort(st)
    return st


def make_mapping(mapping):
    """
    Mapping object factory
    selects the appropriate subclass for the provided inputs
    creates the correct instance of a Mapping object

    Returns:
        an instance of a Mapping or None

    """
    source = concepts.make_concept(mapping.get('mr:source'))
    target = concepts.make_concept(mapping.get('mr:target'))
    matched_types = [mapping_type
                     for mapping_type in Mapping.__subclasses__()
                     if mapping_type.type_match(source, target)]
    if len(matched_types) != 1:
        if len(matched_types) == 0:
            print 'source: ', source
            print 'target: ', target
            mapping = None
        else:
            ec = 'multiple matching Mapping types found {}'
            print ec.format(','.join(matched_types))
            mapping = None
    else:
        mapping = matched_types[0](mapping, source, target)
    return mapping


class Mapping(object):
    """
    abstract Mapping class
    """
    in_file = ''
    _container = ''
    _closure = ''
    to_sort = False

    def __init__(self, amap, source, target):
        return NotImplemented

    def encode(self, fu_p):
        return NotImplemented

    def type_match(definition):
        return NotImplemented

    @classmethod
    def encode_mappings(cls, mapping_list, fu_p):
        map_str = ''
        for port_mappings in mapping_list:
            map_str += port_mappings.encode(fu_p)
        if cls.to_sort:
            map_str = _dict_line_sort(map_str)
        map_str = cls._container + map_str
        map_str += cls._closure
        return map_str


class StashCFMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    for a UM STASH code translating to a CF standard name and unit

    """
    in_file = '../outputs/iris/fileformats/um_cf_map.py'
    _container = '\nSTASH_TO_CF = {'
    _closure = '\n    }\n'
    to_sort = True

    def __init__(self, amap, source, target):
        self.source = source
        self.target = target
        self.valuemaps = amap.get('mr:hasValueMaps')

    def encode(self, fu_p):
        stash = self.source.notation(fu_p)
        cfsname, lname, units = self.target.notation(fu_p)
        str_elem = '    {stash}: CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(stash=stash, cfsname=cfsname,
                                   lname=lname, units=units)
        return str_elem

    @staticmethod
    def type_match(source, target):
        if isinstance(source, concepts.StashConcept) and \
           isinstance(target, concepts.CFPhenomDefConcept):
            typematch = True
        else:
            typematch = False
        return typematch


class FieldcodeCFMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    for a UM field code translating to a CF standard name and unit

    """
    in_file = '../outputs/iris/fileformats/um_cf_map.py'
    _container = '\nLBFC_TO_CF = {'
    _closure = '\n    }\n'
    to_sort = True

    def __init__(self, amap, source, target):
        self.source = source
        self.target = target

    def encode(self, fu_p):
        fc = self.source.notation(fu_p)
        cfsname, lname, units = self.target.notation(fu_p)
        str_elem = '    {fc}: CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(fc=fc, cfsname=cfsname,
                                   lname=lname, units=units)
        return str_elem

    @staticmethod
    def type_match(source, target):
        if isinstance(source, concepts.FieldcodeConcept) and \
           isinstance(target, concepts.CFPhenomDefConcept):
            typematch = True
        else:
            typematch = False
        return typematch


class CFFieldcodeMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    for CF standard name and unit translating to a UM field code

    """
    in_file = '../outputs/iris/fileformats/um_cf_map.py'
    _container = '\nCF_TO_LBFC = {'
    _closure = '\n    }\n'
    to_sort = True

    def __init__(self, amap, source, target):
        self.source = source
        self.target = target

    def encode(self, fu_p):
        fc = self.target.notation(fu_p)
        cfsname, lname, units = self.source.notation(fu_p)
        str_elem = '    CFname({cfsname}, {lname}, {units}): {fc},\n'
        try:
            str_elem = str_elem.format(fc=fc, cfsname=cfsname, units=units)
        except KeyError:
            str_elem = str_elem.format(fc=fc, cfsname=cfsname,
                                       lname=lname, units=units)
        return str_elem

    @staticmethod
    def type_match(source, target):
        if isinstance(source, concepts.CFPhenomDefConcept) and \
           isinstance(target, concepts.FieldcodeConcept):
            typematch = True
        else:
            typematch = False
        return typematch
