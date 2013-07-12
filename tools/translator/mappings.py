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


def make_mapping(mapping, fu_p):
    """
    Mapping object factory
    selects the appropriate subclass for the inputs
    """
    source = concepts.make_concept(mapping.get('mr:source'), fu_p)
    target = concepts.make_concept(mapping.get('mr:target'), fu_p)
    matched_types = [mapping_type 
                     for mapping_type in Mapping.__subclasses__ 
                     if type.type_match(source, target)]
    if len(matched_types) != 1:
        if len(matched_types) == 0:
            print 'source: ', source
            print 'target: ', target
            mapping = None
        else:
            raise ValueError('multiple matching Mapping types found')
            mapping = None
    else:
        mapping = matched_types[0](mapping, source, target, fu_p)
    return mapping
    # built_mappings = []
    # for mapping_type in Mapping.__subclasses__():
    #     source = concepts.make_concept(mapping.get('mr:source'), fu_p)
    #     target = concepts.make_concept(mapping.get('mr:target'), fu_p)
    #     if mapping_type.type_match(source, target):
    #         built_mappings.append(mapping_type(mapping, source, target, fu_p))
    # if len(built_mappings) != 1:
    #     if len(built_mappings) == 0:
    #         print 'source: ', source
    #         print 'target: ', target
    #         built_mappings = [None]
    #     else:
    #         raise ValueError('multiple matching Mapping types found')
    #         built_mappings = [None]
    # return built_mappings[0]


class Mapping(object):
    """
    abstract Mapping class
    """
    in_file = None
    container = None
    closure = None
    to_sort = None

    def __init__(self, amap, source, target, fu_p):
        return NotImplemented

    def encode(self):
        return NotImplemented

    def type_match(definition):
        return NotImplemented


class StashCFMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values

    """
    in_file = '../outputs/um_cf_map.py'
    container = '\nSTASH_TO_CF = {'
    closure = '\n\t}\n'
    to_sort = True

    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.valuemaps = amap.get('mr:hasValueMaps')
        self.fu_p = fu_p

    def encode(self):
        stash = self.source.notation()
        cfsname, lname, units = self.target.notation()
        str_elem = '\t{stash} : CFname({cfsname}, {lname}, {units}),\n'
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

    """
    in_file = '../outputs/um_cf_map.py'
    container = '\nLBFC_TO_CF = {'
    closure = '\n\t}\n'
    to_sort = True

    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        #self.valuemaps = amap.get('mr:hasValueMaps')
        self.fu_p = fu_p

    def encode(self):
        fc = self.source.notation()
        cfsname, lname, units = self.target.notation()
        #lname
        str_elem = '\t{fc} : CFname({cfsname}, {lname}, {units}),\n'
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

    """
    in_file = '../outputs/um_cf_map.py'
    container = '\nCF_TO_LBFC = {'
    closure = '\n\t}\n'
    to_sort = True

    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        #self.valuemaps = amap.get('mr:hasValueMaps')
        self.fu_p = fu_p

    def encode(self):
        fc = self.target.notation()
        cfsname, lname, units = self.source.notation()
        str_elem = '\tCFname({cfsname}, {lname}, {units}) : {fc},\n'
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
