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


def make_concept(definition, fu_p):
    """
    Concept object factory
    selects the appropriate subclass for the provided inputs
    creates the correct instance of a Concept object

    Returns:
        an instance of a Concept or None

    """
    matched_types = [concept_type
                     for concept_type in Concept.__subclasses__()
                     if concept_type.type_match(definition, fu_p)]
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
        built_concept = matched_types[0](definition, fu_p)
    return built_concept


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
            prop_name = moq.get_label(self.fu_p, p.get('mr:name'))
            prop_value = moq.get_label(self.fu_p, p.get('rdf:value'))
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
