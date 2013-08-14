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
Classes for types of metarelate concept, with a factory for creating instances

"""


import metocean.queries as moq

_OPEQ = '<http://www.openmath.org/cd/relation1.xhtml#eq>'


def make_concept(definition):
    """
    Concept object factory
    selects the appropriate subclass for the provided inputs
    creates the correct instance of a Concept object

    Returns:
        an instance of a Concept or None

    """
    matched_types = [concept_type
                     for concept_type in Concept.__subclasses__()
                     if concept_type.type_match(definition)]
    if len(matched_types) != 1:
        if len(matched_types) == 0:
            ec = 'no matching Concept type found \n{}'.format(definition)
            print ec
            built_concept = None
        else:
            ec = 'multiple matching Concept types found\n {}'
            ec = ec.format(built_concepts)
            print ec
            built_concept = None
    else:
        built_concept = matched_types[0](definition)
    return built_concept


class Concept(object):
    """
    abstract class for a source or target concept
    """
    def __init__(self, definition, fu_p):
        return NotImplemented

    def notation(self, direction):
        ## direction should be None, 'test' or 'assign' only
        return NotImplemented

    def type_match(definition):
        return NotImplemented


class StashConcept(Concept):
    """
    a concept which is a UM stash code only
    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']

    def notation(self, fu_p, direction=None):
        val = self.properties[0].get('rdf:value')
        stash = moq.get_label(fu_p, val)
        return stash

    @staticmethod
    def type_match(definition):
        STASHC = '<http://reference.metoffice.gov.uk/def/um/stash/concept/'
        F3STASH = '<http://reference.metoffice.gov.uk/def/um/umdp/F3/stash>'
        fformat = '<http://www.metarelate.net/metOcean/format/um>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        if ff and len(properties) == 1 and len(components) == 0:
            val = properties[0].get('rdf:value')
            stashval = val and val.startswith(STASHC)
            name = properties[0].get('mr:name')
            stashname = name and name == F3STASH
            operator = properties[0].get('mr:operator')
            op_eq = operator and operator == _OPEQ
            stash = stashval and stashname and op_eq
        else:
            stash = False
        return stash


class FieldcodeConcept(Concept):
    """
    a concept which is a UM field code only
    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']

    def notation(self, fu_p, direction=None):
        val = self.properties[0].get('rdf:value')
        fcode = moq.get_label(fu_p, val)
        return fcode

    @staticmethod
    def type_match(definition):
        FIELDC = '<http://reference.metoffice.gov.uk/def/um/fieldcode/'
        F3FIELD = '<http://reference.metoffice.gov.uk/def/um/umdp/F3/lbfc>'
        fformat = '<http://www.metarelate.net/metOcean/format/um>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        if ff and len(properties) == 1 and len(components) == 0:
            val = properties[0].get('rdf:value')
            fieldval = val and val.startswith(FIELDC)
            name = properties[0].get('mr:name')
            fieldname = name and name == F3FIELD
            operator = properties[0].get('mr:operator')
            op_eq = operator and operator == _OPEQ
            fieldcode = fieldval and fieldname and op_eq
        else:
            fieldcode = False
        return fieldcode


class CFPhenomDefConcept(Concept):
    """
    a concept which is only defining a CF Field's base phenomenon
    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']

    def notation(self, fu_p, direction=None):
        cfsn = None
        lname = None
        units = None
        for p in self.properties:
            prop_name = moq.get_label(fu_p, p.get('mr:name'))
            prop_value = moq.get_label(fu_p, p.get('rdf:value'))
            if prop_name == '"standard_name"':
                cfsn = prop_value
                if cfsn.startswith('<'):
                    cfsn = None
            elif prop_name == '"long_name"':
                lname = prop_value
            elif prop_name == '"units"':
                units = prop_value
        return cfsn, lname, units

    @staticmethod
    def type_match(definition):
        fformat = '<http://www.metarelate.net/metOcean/format/cf>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        if ff and len(components) == 0:
            define = {}
            for prop in properties:
                op = prop.get('mr:operator')
                name = prop.get('mr:name', '')
                value = prop.get('rdf:value')
                if op and value and op == _OPEQ:
                    if not define.get(name):
                        define[name] = value
            cfc = 'http://def.cfconventions.org/datamodel/'
            required = set(('<{}units>'.format(cfc),
                            '<{}type>'.format(cfc)))
            eitheror = set(('<{}standard_name>'.format(cfc),
                            '<{}long_name>'.format(cfc)))
            phenom = (set(define.keys()) >= required and
                      set(define.keys()) < (required | eitheror))
        else:
            phenom = False
        return phenom


class CFConstrainedPhenomDefConcept(Concept):
    """
a concept which is defining a CF Field's base phenomenon and
one constraining coordinate
"""
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.components = definition['mr:hasComponent']
        self.id = definition['component']
    def notation(self, fu_p, direction=None):
        phenom = None
        constraint = None
        for comp in self.components:
            points = None
            cfsn = None
            units = None
            for p in comp.get('mr:hasProperty', []):
                if moq.get_label(fu_p, p.get('mr:name')) == '"standard_name"':
                    cfsn = moq.get_label(fu_p, p.get('rdf:value'))
                    if cfsn.startswith('<'):
                        cfsn = None
                elif moq.get_label(fu_p, p.get('mr:name')) == '"units"':
                    units = moq.get_label(fu_p, p.get('rdf:value'))
                elif moq.get_label(fu_p, p.get('mr:name')) == '"points"':
                    points = moq.get_label(fu_p, p.get('rdf:value'))
            if points and cfsn and units:
                constraint = {'cfsn':cfsn, 'units':units, 'points':points}
            else:
                phenom = {'cfsn':cfsn, 'units':units}
        return phenom, constraint
    @staticmethod
    def type_match(definition):
        fformat = '<http://www.metarelate.net/metOcean/format/cf>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        phenom = False
        constraint = False
        if ff and len(properties) == 0 and len(components) == 2:
            for comp in components:
                define = {}
                properties = comp.get('mr:hasProperty', [])
                for prop in properties:
                    op = prop.get('mr:operator')
                    name = prop.get('mr:name', '')
                    value = prop.get('rdf:value')
                    if op and value and op == _OPEQ:
                        if not define.get(name):
                            define[name] = value
                cfc = 'http://def.cfconventions.org/datamodel/'
                preq = set(('<{}units>'.format(cfc),
                            '<{}type>'.format(cfc),
                            '<{}standard_name>'.format(cfc)))
                creq = set(('<{}units>'.format(cfc),
                            '<{}type>'.format(cfc),
                            '<{}standard_name>'.format(cfc),
                            '<{}points>'.format(cfc)))
                if set(define.keys()) == preq:
                    phenom = True
                elif set(define.keys()) == creq:
                    constraint = True
        con_phenom = phenom and constraint
        return con_phenom


def _cfprop(props, fu_p, eq):
    """
    helper method to retrieve cf properties and encode in python
    """
    t_str = ''
    elem_str = ''
    for prop in props:
        if prop.get('mr:name').endswith('/type>'):
            t_str = moq.get_label(fu_p, prop.get('rdf:value', ''))
            t_str = t_str.strip('"')
            t_str += '('
        #elif prop.get('mr:name').endswith('/coordinate>'):
        # print prop
        elif prop.get('mr:hasComponent'):
            comp = prop.get('mr:hasComponent')
            comp_notation = _cfprop(comp.get('mr:hasProperty'), fu_p, eq)
            name = moq.get_label(fu_p, prop.get('mr:name', ''))
            name = name.strip('"')
            elem_str += '{} {} {},'.format(name, eq, comp_notation)
        else:
            name = moq.get_label(fu_p, prop.get('mr:name', ''))
            name = name.strip('"')
            val = moq.get_label(fu_p, prop.get('rdf:value', ''))
            if val:
                elem_str += '{} {} {},'.format(name, eq, val)
            else:
                elem_str += '%s %s {%s},' % (name, eq, name)
    p_str = t_str + elem_str + ')'
    return p_str


class GribConcept(Concept):
    """
    a grib concept which doesn't match the specialised grib concepts
    and has only properties, not components

    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
    def notation(self, fu_p, direction):
        prop_notation = ''
        for prop in self.properties:
            name = moq.get_label(fu_p, prop.get('mr:name'))
            name = name.strip('"')
            op = prop.get('mr:operator') == _OPEQ
            val = prop.get('rdf:value')
            n = ''
            if name and op and val:
                if direction == 'test':
                    n = '\n factbase.{}({})'.format(name, val)
                elif direction == 'assign':
                    n = '\n python engine.agrib.{} = {}'.format(name, val)
                
            elif name:
                if direction == 'test':
                    n = '\n factbase.{}'.format(name)
                elif direction == 'assign':
                    n = '\n python engine.agrib.{}'.format(name)
                    n += ' = {%s} ' % prop.get('mr:name')
            prop_notation += n
        if direction == 'test':
            r_val = prop_notation
        elif direction == 'assign':
            r_val = prop_notation
        return r_val
    @staticmethod
    def type_match(definition):
        fformat = '<http://www.metarelate.net/metOcean/format/grib>'
        ff = definition['mr:hasFormat'] == fformat
        components = definition.get('mr:hasComponent', [])
        g2param = Grib2ParamConcept.type_match(definition)
        g1lparam = Grib1LocalParamConcept.type_match(definition)
        if ff and len(components) == 0 and not g2param and not g1lparam:
            grib_c = True
        else:
            grib_c = False
        return grib_c

class Grib1LocalParamConcept(Concept):
    """
    a concept which is only defining a GRIB1 local parameter code
    ed, t2version, centre, iparam = self.source.notation()

    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
    def notation(self, fu_p, direction=None):
        for prop in self.properties:
            name = prop.get('mr:name', '')
            gpref = 'http://def.ecmwf.int/api/grib/keys/'
            if name == '<{}editionNumber>'.format(gpref):
                ed = prop.get('rdf:value')
            elif name == '<{}table2Version>'.format(gpref):
                t2version = prop.get('rdf:value')
            elif name == '<{}centre>'.format(gpref):
                centre = prop.get('rdf:value')
            elif name == '<{}indicatorOfParameter>'.format(gpref):
                iparam = prop.get('rdf:value')
        return ed, t2version, centre, iparam
    @staticmethod
    def type_match(definition):
        fformat = '<http://www.metarelate.net/metOcean/format/grib>'
        ed = '<http://def.ecmwf.int/api/grib/keys/editionNumber>'
        t2version = '<http://def.ecmwf.int/api/grib/keys/table2Version>'
        centre = '<http://def.ecmwf.int/api/grib/keys/centre>'
        iparam = '<http://def.ecmwf.int/api/grib/keys/indicatorOfParameter>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        def_keys = set([p.get('mr:name', '') for p in properties])
        param_keys = set((ed, t2version, centre, iparam))
        if ff and len(components) == 0 and def_keys == param_keys:
            grib1lparam = True
        else:
            grib1lparam = False
        return grib1lparam

class Grib2ParamConcept(Concept):
    """
    a concept which is only defining a GRIB2 parameter code
    """
    def __init__(self, definition):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
    def notation(self, fu_p, direction=None):
        for prop in self.properties:
            gpref = 'http://def.ecmwf.int/api/grib/keys/'
            name = prop.get('mr:name', '')
            if name == '<{}editionNumber>'.format(gpref):
                ed = prop.get('rdf:value')
            elif name == '<{}discipline>'.format(gpref):
                disc = prop.get('rdf:value')
            elif name == '<{}parameterNumber>'.format(gpref):
                param = prop.get('rdf:value')
            elif name == '<{}parameterCategory>'.format(gpref):
                cat = prop.get('rdf:value')
        return ed, disc, param, cat
    @staticmethod
    def type_match(definition):
        fformat = '<http://www.metarelate.net/metOcean/format/grib>'
        ed = '<http://def.ecmwf.int/api/grib/keys/editionNumber>'
        disc = '<http://def.ecmwf.int/api/grib/keys/discipline>'
        param = '<http://def.ecmwf.int/api/grib/keys/parameterNumber>'
        cat = '<http://def.ecmwf.int/api/grib/keys/parameterCategory>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        def_keys = set([p.get('mr:name', '') for p in properties])
        param_keys = set((ed, disc, param, cat))
        if ff and len(components) == 0 and def_keys == param_keys:
            grib2param = True
        else:
            grib2param = False
        return grib2param
