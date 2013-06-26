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

from concepts import *

def make_mapping(mapping, fu_p):
    """
    Mapping object factory
    selects the appropriate subclass for the inputs
    """
    built_mappings = []
    for mapping_type in Mapping.__subclasses__():
        source = make_concept(mapping.get('mr:source'), fu_p)
        target = make_concept(mapping.get('mr:target'), fu_p)
        if mapping_type.type_match(source, target):
            built_mappings.append(mapping_type(mapping, source, target, fu_p))
    if len(built_mappings) != 1:
        if len(built_mappings) == 0:
            print 'source: ', source
            print 'target: ', target
#            raise ValueError('no matching Mapping type found')
            built_mappings = [None]
        else:
            raise ValueError('multiple matching Mapping types found')
            built_mappings = [None]
    return built_mappings[0]


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
        cfsname, lname, units =  self.target.notation()
        str_elem = '\t{stash} : CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(stash=stash, cfsname=cfsname,
                                   lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, StashConcept) and \
            isinstance(target,CFPhenomDefConcept):
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
        cfsname, lname, units =  self.target.notation()
        #lname
        str_elem = '\t{fc} : CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(fc=fc, cfsname=cfsname,
                                   lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, FieldcodeConcept) and \
            isinstance(target,CFPhenomDefConcept):
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
        cfsname, lname, units =  self.source.notation()
        str_elem = '\tCFname({cfsname}, {lname}, {units}) : {fc},\n'
        try:
            str_elem = str_elem.format(fc=fc, cfsname=cfsname, units=units)
        except KeyError:
            str_elem = str_elem.format(fc=fc, cfsname=cfsname,
                                   lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, CFPhenomDefConcept) and \
            isinstance(target, FieldcodeConcept):
            typematch = True
        else:
            typematch = False
        return typematch



class Grib1LocalCFParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a GRIB1 parameter source concept, a CF parameter
    target concept and no mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nGRIB1Local_TO_CF = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.fu_p = fu_p
    def encode(self):
        ed, t2version, centre, iparam = self.source.notation()
        cfsname, lname, units =  self.target.notation()
        str_elem = '\tG1Lparam({ed}, {t2version}, {centre}, {iParam}): '
        str_elem += 'CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(ed=ed, t2version=t2version, centre=centre,
                                   iParam=iparam,
                                   cfsname=cfsname, lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, Grib1LocalParamConcept) and \
            isinstance(target, CFPhenomDefConcept):
            typematch = True
        else:
            typematch = False
        return typematch

class Grib1LocalCFConstrainedParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a GRIB1 parameter source concept, a CF parameter
    target concept with a constraint coord and no mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nGRIB1LocalConstrained_TO_CF = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.fu_p = fu_p
    def encode(self):
        ed, t2version, centre, iparam = self.source.notation()
        phenom, con =  self.target.notation()
        str_elem = '\tG1Lparam({ed}, {t2version}, {centre}, {iParam}): '
        str_elem += '(CFname({psname}, {plname}, {punits}), '
        str_elem += 'DimensionCoordinate({csname}, {cunits}, ({cpoints},))),\n'
        str_elem = str_elem.format(ed=ed, t2version=t2version, centre=centre,
                                   iParam=iparam, psname=phenom['cfsn'],
                                   plname='None', punits=phenom['units'],
                                   csname=con['cfsn'], cunits=con['units'],
                                   cpoints=con['points'])
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, Grib1LocalParamConcept) and \
            isinstance(target, CFConstrainedPhenomDefConcept):
            typematch = True
        else:
            typematch = False
        return typematch


## no GRIB1 save capability
class CFGrib1LocalParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nCF_TO_GRIB1Local = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.valuemaps = amap.get('mr:hasValueMaps', [])
        self.fu_p = fu_p
    def encode(self):
        ed, t2version, centre, iparam = self.target.notation()
        cfsname, lname, units =  self.source.notation()
        str_elem = '\tCFname({cfsname}, {lname}, {units}):'
        str_elem += 'G1Lparam({ed}, {t2version}, {centre}, {iParam}),\n'
        str_elem = str_elem.format(ed=ed, t2version=t2version, centre=centre,
                                   iParam=iparam,
                                   cfsname=cfsname, lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, CFPhenomDefConcept) and \
            isinstance(target, Grib1LocalParamConcept):
            typematch = True
        else:
            typematch = False
        return typematch

class CFConstrainedGrib1LocalParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nCFConstrained_TO_GRIB1Local = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.valuemaps = amap.get('mr:hasValueMaps', [])
        self.fu_p = fu_p
    def encode(self):
        ed, t2version, centre, iparam = self.target.notation()
        phenom, con =  self.source.notation()
        str_elem = '(CFname({psname}, {plname}, {punits}), '
        str_elem += 'DimensionCoordinate({csname}, {cunits}, ({cpoints},))): '
        str_elem += 'G1Lparam({ed}, {t2version}, {centre}, {iParam}),\n'
        str_elem = str_elem.format(ed=ed, t2version=t2version, centre=centre,
                                   iParam=iparam, psname=phenom['cfsn'],
                                   plname='None', punits=phenom['units'],
                                   csname=con['cfsn'], cunits=con['units'],
                                   cpoints=con['points'])
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, CFConstrainedPhenomDefConcept) and \
            isinstance(target, Grib1LocalParamConcept):
            typematch = True
        else:
            typematch = False
        return typematch




class Grib2CFParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nGRIB2_TO_CF = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.fu_p = fu_p
    def encode(self):
        ed, disc, param, cat = self.source.notation()
        cfsname, lname, units =  self.target.notation()
        str_elem = '\tG2param({ed}, {disc}, {cat}, {num}): '
        str_elem += 'CFname({cfsname}, {lname}, {units}),\n'
        str_elem = str_elem.format(ed=ed, disc=disc, cat=cat, num=param,
                                   cfsname=cfsname, lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, Grib2ParamConcept) and \
            isinstance(target, CFPhenomDefConcept):
            typematch = True
        else:
            typematch = False
        return typematch

    
class CFGrib2ParamMapping(Mapping):
    """
    a mapping object, obtained from the metarelate repository
    defining a source concept, a target concept and any mapped values
    
    """
    in_file = '../outputs/_grib_cf_map.py'
    container = '\nCF_TO_GRIB2 = {'
    closure = '\n\t}\n'
    to_sort = True
    def __init__(self, amap, source, target, fu_p):
        self.source = source
        self.target = target
        self.valuemaps = amap.get('mr:hasValueMaps', [])
        self.fu_p = fu_p
    def encode(self):
        ed, disc, param, cat = self.target.notation()
        cfsname, lname, units =  self.source.notation()
        str_elem = '\tCFname({cfsname}, {lname}, {units}):'
        str_elem += 'G2param({ed}, {disc}, {cat}, {num}),\n '
        str_elem = str_elem.format(ed=ed, disc=disc, cat=cat, num=param,
                                   cfsname=cfsname, lname=lname, units=units)
        return str_elem
    @staticmethod
    def type_match(source, target):
        if isinstance(source, CFPhenomDefConcept) and \
            isinstance(target, Grib2ParamConcept):
            typematch = True
        else:
            typematch = False
        return typematch


