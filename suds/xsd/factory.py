# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )


from suds import *
from suds.xsd import *
from suds.xsd.sxbuiltin import *
from suds.xsd.sxbasic import *
from suds.xsd.query import Query

log = logger(__name__)


class Factory:
    """
    @cvar tags: A factory to create object objects based on tag.
    @type tags: {tag:fn,}
    @cvar builtins: A factory to create object objects based on tag.
    @type builtins: {tag:fn,}
    """

    tags =\
    {
        'import' : lambda x,y=None: Import(x,y), 
        'complexType' : lambda x,y=None: Complex(x,y), 
        'simpleType' : lambda x,y=None: Simple(x,y), 
        'element' : lambda x,y=None: Element(x,y),
        'attribute' : lambda x,y=None: Attribute(x,y),
        'sequence' : lambda x,y=None: Sequence(x,y),
        'complexContent' : lambda x,y=None: ComplexContent(x,y),
        'restriction' : lambda x,y=None: Restriction(x,y),
        'enumeration' : lambda x,y=None: Enumeration(x,y),
        'extension' : lambda x,y=None: Extension(x,y),
        'any' : lambda x,y=None: Any(x,y),
    }

    builtins =\
    {
        'anyType' : lambda x,y=None: Any(x,y),
        'boolean' : lambda x,y=None: XBoolean(x,y),
    }
    
    def __init__(self, schema):
        """
        @param schema: A schema object.
        @type schema: L{schema.Schema} 
        """
        self.schema = schema
        
    def build(self, root, filter=('*',)):
        """
        Build an xsobject representation.
        @param root: An schema XML root.
        @type root: L{sax.Element}
        @param filter: A tag filter.
        @type filter: [str,...]
        @return: A schema object graph.
        @rtype: L{sxbase.SchemaObject}
        """
        result = []
        for node in root.children:
            if '*' in filter or node.name in filter:
                child = self.create(basic=node)
                child.factory = self
                result.append(child)
                child.children = self.build(node, child.valid_children())
        return result
    
    def create(self, basic=None, builtin=None, query=None):
        """
        Create an xsd object.
        @param basic: A root node.  When specified, a object is created.
        @type basic: L{sax.Element}
        @param builtin: The name of an xsd builtin type.  When specified, a 
            object is created.
        @type builtin: basestring
        @return: A I{basic} I{schema.SchemaObject} when I{basic} is specified; An
            L{XBuiltin} builtin when I{builtin} name is specified;
            A L{Query} when I{query} is specified.
        @rtype: L{SchemaObject}
        """
        if basic is not None:
            return self.__create(basic)
        elif builtin is not None:
            return self.__builtin(builtin)
        elif query is not None:
            return Query(query)

    def __create(self, root):
        if root.name in Factory.tags:
            fn = Factory.tags[root.name]
            return fn(self.schema, root)
        else:
            raise Exception('tag (%s) not-found' % root.name)
        
    def __builtin(self, name):
        if name in Factory.builtins:
            fn = Factory.builtins[name]
            return fn(self.schema, name)
        else:
            return XBuiltin(self.schema, name)
