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

import metocean.queries as moq

OPEQ = '<http://www.openmath.org/cd/relation1.xhtml#eq>'

def make_concept(definition, fu_p):
    """
    Concept object factory
    selects the appropriate subclass for the inputs
    """

    built_concepts = []
    for concept_type in Concept.__subclasses__():
        if concept_type.type_match(definition, fu_p):
            built_concepts.append(concept_type(definition, fu_p))
    if len(built_concepts) != 1:
        if len(built_concepts) == 0:
            ec = 'no matching Concept type found \n{}'.format(definition)
            #raise ValueError(ec)
            built_concepts = [None]
        else:
            ec = 'multiple matching Concept types found\n {}'
            ec = ec.format(built_concepts)
            raise ValueError(ec)
            built_concepts = [None]
    return built_concepts[0]


class Concept(object):
    """
    a source or target concept
    """
    def __init__(self, definition, fu_p):
        return NotImplemented
    def notation(self, direction):
        ## direction should be 'test' or 'assign' only
        return NotImplemented
    def type_match(definition, fu_p):
        return NotImplemented
    

class StashConcept(Concept):
    """
    a concept which is a UM stash code only
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        val = self.properties[0].get('rdf:value')
        stash = moq.get_label(self.fu_p, val)
        return stash
    @staticmethod
    def type_match(definition, fu_p):
        STASHC = '<http://reference.metoffice.gov.uk/def/um/stash/concept/'
        F3STASH = '<http://reference.metoffice.gov.uk/def/um/umdp/F3/stash>'
        fformat = '<http://www.metarelate.net/metOcean/format/um>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        if ff and len(properties) == 1 and len(components) == 0:
            val = properties[0].get('rdf:value')
            if val:
                stashval = val.startswith(STASHC)
            else:
                stashval = False
            name = properties[0].get('mr:name')
            if name:
                stashname = name == F3STASH
            else:
                stashname = False
            operator = properties[0].get('mr:operator')
            if operator:
                op_eq = operator = OPEQ
            else:
                op_eq = False
            if stashval and stashname and op_eq:
                stash = True
            else:
                stash = False
        else:
            stash = False
        return stash


class FieldcodeConcept(Concept):
    """
    a concept which is a UM field code only
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        val = self.properties[0].get('rdf:value')
        fcode = moq.get_label(self.fu_p, val)
        return fcode
    @staticmethod
    def type_match(definition, fu_p):
        FIELDC = '<http://reference.metoffice.gov.uk/def/um/fieldcode/'
        F3FIELD = '<http://reference.metoffice.gov.uk/def/um/umdp/F3/lbfc>'
        fformat = '<http://www.metarelate.net/metOcean/format/um>'
        ff = definition['mr:hasFormat'] == fformat
        properties = definition.get('mr:hasProperty', [])
        components = definition.get('mr:hasComponent', [])
        if ff and len(properties) == 1 and len(components) == 0:
            val = properties[0].get('rdf:value')
            if val:
                fieldval = val.startswith(FIELDC)
            else:
                fieldval = False
            name = properties[0].get('mr:name')
            if name:
                fieldname = name == F3FIELD
            else:
                fieldname = False
            operator = properties[0].get('mr:operator')
            if operator:
                op_eq = operator = OPEQ
            else:
                op_eq = False
            if fieldval and fieldname and op_eq:
                fieldcode = True
            else:
                fieldcode = False
        else:
            fieldcode = False
        return fieldcode



class CFPhenomDefConcept(Concept):
    """
    a concept which is only defining a CF Field's base phenomenon
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        cfsn = None
        lname = None
        units = None
        for p in self.properties:
            if moq.get_label(self.fu_p, p.get('mr:name')) == '"standard_name"':
                cfsn = moq.get_label(self.fu_p, p.get('rdf:value'))
                if cfsn.startswith('<'):
                    cfsn = None
            elif moq.get_label(self.fu_p, p.get('mr:name')) == '"long_name"':
                lname = p.get('rdf:value')
            elif moq.get_label(self.fu_p, p.get('mr:name')) == '"units"':
                units = moq.get_label(self.fu_p, p.get('rdf:value'))
        return cfsn, lname, units
    @staticmethod
    def type_match(definition, fu_p):
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
                if op and value and op == OPEQ:
                    # name_label = moq.get_label(fu_p, name)
                    # value_label = moq.get_label(fu_p, value)
                    # if not define.get(name_label):
                    #     define[name_label] = value_label
                    if not define.get(name):
                        define[name] = value
            # required = set(('"units"', '"type"'))
            # eitheror = set(('"standard_name"', '"long_name"'))
            required = set(('<http://def.cfconventions.org/datamodel/units>',
                            '<http://def.cfconventions.org/datamodel/type>'))
            eitheror = set(('<http://def.cfconventions.org/datamodel/standard_name>',
                            '<http://def.cfconventions.org/datamodel/long_name>'))
            if set(define.keys()).issuperset(required) and \
                set(define.keys()).issubset(required.union(eitheror)):
                phenom = True
            else:
                phenom = False
        else:
            phenom = False
        return phenom

class CFConstrainedPhenomDefConcept(Concept):
    """
    a concept which is defining a CF Field's base phenomenon and
    one constraining coordinate
    
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.components = definition['mr:hasComponent']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        phenom = None
        constraint = None
        for comp in self.components:
            points = None
            cfsn = None
            units = None
            for p in comp.get('mr:hasProperty', []):
                if moq.get_label(self.fu_p, p.get('mr:name')) == '"standard_name"':
                    cfsn = moq.get_label(self.fu_p, p.get('rdf:value'))
                    if cfsn.startswith('<'):
                        cfsn = None
                elif moq.get_label(self.fu_p, p.get('mr:name')) == '"units"':
                    units = moq.get_label(self.fu_p, p.get('rdf:value'))
                elif moq.get_label(self.fu_p, p.get('mr:name')) == '"points"':
                    points = moq.get_label(self.fu_p, p.get('rdf:value'))
            if points and cfsn and units:
                constraint = {'cfsn':cfsn, 'units':units, 'points':points}
            else:
                phenom = {'cfsn':cfsn, 'units':units}
        return phenom, constraint
    @staticmethod
    def type_match(definition, fu_p):
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
                    if op and value and op == OPEQ:
                        # name_label = moq.get_label(fu_p, name)
                        # value_label = moq.get_label(fu_p, value)
                        # if not define.get(name_label):
                        #     define[name_label] = value_label
                        if not define.get(name):
                            define[name] = value
                preq = set(('<http://def.cfconventions.org/datamodel/units>',
                            '<http://def.cfconventions.org/datamodel/type>',
                            '<http://def.cfconventions.org/datamodel/standard_name>'))
                creq = set(('<http://def.cfconventions.org/datamodel/units>',
                            '<http://def.cfconventions.org/datamodel/type>',
                            '<http://def.cfconventions.org/datamodel/standard_name>',
                            '<http://def.cfconventions.org/datamodel/points>'))
                # preq = set(('"units"', '"type"', '"standard_name"'))
                # creq = set(('"units"', '"type"', '"standard_name"', '"points"'))
                if set(define.keys()) == preq:
                    phenom = True
                elif set(define.keys()) == creq:
                    constraint = True
        con_phenom = phenom and constraint
        return con_phenom


def _cfprop(props, fu_p, eq):
    """
    """
    t_str = ''
    elem_str = ''
    for prop in props:
        if prop.get('mr:name').endswith('/type>'):
            t_str = moq.get_label(fu_p, prop.get('rdf:value', ''))
            t_str = t_str.strip('"')
            t_str += '('
        #elif prop.get('mr:name').endswith('/coordinate>'):
        #    print prop
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

class CFConcept(Concept):
    """
    a cf concept which doesn't match the specialised cf concepts
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition.get('mr:hasProperty', [])
        self.components = definition.get('mr:hasComponent', [])
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction):
        # prop_notation = ''
        # assign_keys = []
        eq = '='
        if direction == 'test':
            if len(self.components) == 0:
                prop_notation = '\n        engine.cube.{}'.format(_cfprop(self.properties, self.fu_p, eq))
            elif len(self.properties) == 0:
                prop_notation = ''
                for comp in self.components:
                    prop_notation += '\n        engine.cube.'
                    props = comp.get('mr:hasProperty')
                    if props:
                        prop_notation += _cfprop(props, self.fu_p, eq) 
                prop_notation += ')'
            else:
                raise ValueError('components and properties cannot coexist on',
                                 ' a cf concept')
        elif direction == 'assign':
            if len(self.components) == 0:
                prop_notation = '\n        python engine.bucket.append({})'.format(_cfprop(self.properties, self.fu_p, eq))
            elif len(self.properties) == 0:
                prop_notation = ''
                for comp in self.components:
                    prop_notation += '\n        python engine.bucket.append('
                    props = comp.get('mr:hasProperty')
                    if props:
                        prop_notation += _cfprop(props, self.fu_p, eq) 
                prop_notation += ')'
            else:
                raise ValueError('components and properties cannot coexist on',
                                 ' a cf concept')
        return prop_notation
    @staticmethod
    def type_match(definition, fu_p):
        fformat = '<http://www.metarelate.net/metOcean/format/cf>'
        ff = definition['mr:hasFormat'] == fformat
        pd =  CFPhenomDefConcept.type_match(definition, fu_p)
        pcd = CFConstrainedPhenomDefConcept.type_match(definition, fu_p)
        if ff and not pd and not pcd:
            cfc = True
        else:
            cfc = False
        return cfc
    
        
class GribConcept(Concept):
    """
    a grib concept which doesn't match the specialised grib concepts
    and has only properties, not components
    """
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction):
        prop_notation = ''
#        assign_keys = []
        for prop in self.properties:
            name = moq.get_label(self.fu_p, prop.get('mr:name'))
            name = name.strip('"')
            op = prop.get('mr:operator') == OPEQ
            val = prop.get('rdf:value')
            n = ''
            if name and op and val:
                if direction == 'test':
                    n = '\n        factbase.{}({})'.format(name, val)
                elif direction == 'assign':
                    n = '\n        python engine.agrib.{} = {}'.format(name, val)
                
            elif name:
                if direction == 'test':
                    n = '\n        factbase.{}'.format(name)
                elif direction == 'assign':
                    n = '\n        python engine.agrib.{}'.format(name)
                    n += ' = {%s} ' % prop.get('mr:name')
#                    assign_keys.append(prop.get('mr:name'))
            prop_notation += n
        if direction == 'test':
            r_val = prop_notation
        elif direction == 'assign':
            r_val = prop_notation#, assign_keys

        return r_val
    @staticmethod
    def type_match(definition, fu_p):
        fformat = '<http://www.metarelate.net/metOcean/format/grib>'
        ff = definition['mr:hasFormat'] == fformat
        components = definition.get('mr:hasComponent', [])
        g2param = Grib2ParamConcept.type_match(definition, fu_p)
        g1lparam = Grib1LocalParamConcept.type_match(definition, fu_p)
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
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        for prop in self.properties:
            name = prop.get('mr:name', '')
            if name == '<http://def.ecmwf.int/api/grib/keys/editionNumber>':
                ed = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/table2Version>':
                t2version = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/centre>':
                centre = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/indicatorOfParameter>':
                iparam = prop.get('rdf:value')
        return ed, t2version, centre, iparam
    @staticmethod
    def type_match(definition, fu_p):
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
    def __init__(self, definition, fu_p):
        self.fformat = definition['mr:hasFormat']
        self.properties = definition['mr:hasProperty']
        self.id = definition['component']
        self.fu_p = fu_p
    def notation(self, direction=None):
        for prop in self.properties:
            name = prop.get('mr:name', '')
            if name == '<http://def.ecmwf.int/api/grib/keys/editionNumber>':
                ed = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/discipline>':
                disc = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/parameterNumber>':
                param = prop.get('rdf:value')
            elif name == '<http://def.ecmwf.int/api/grib/keys/parameterCategory>':
                cat = prop.get('rdf:value')
        return ed, disc, param, cat
    @staticmethod
    def type_match(definition, fu_p):
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


