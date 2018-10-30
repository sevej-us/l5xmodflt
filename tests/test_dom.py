"""
Unit tests for low-level XML interface objects.
"""

from l5x import dom
import unittest
import xml.etree.ElementTree as ElementTree


class ElementDict(unittest.TestCase):
    """Unit tests for the ElementDict class."""
    class Dummy(object):
        """Mock dictionary value type."""
        def __init__(self, element, *args):
            self.element = element
            self.args = args

    def test_key_attribute_value(self):
        """Confirm values from the key attribute are used for lookup."""
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        self.assertIs(d['foo'].element, child)

    def test_depth_lookup(self):
        """Confirm only direct children are queried for lookup."""
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'foo'})
        ElementTree.SubElement(child, 'grandchild', {'key':'bar'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(KeyError):
            d['bar']

    def test_key_not_found(self):
        """Confirm a KeyError is raised if a matching key doesn't exist."""
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(KeyError):
            d['bar']

    def test_key_not_found_empty(self):
        """Confirm a KeyError is raised if the parent has no child elements."""
        parent = ElementTree.Element('parent')
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(KeyError):
            d['bar']

    def test_string_lookup(self):
        """Confirm correct lookup with string keys."""
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        self.assertIs(d['foo'].element, child)

    def test_integer_lookup(self):
        """Confirm correct lookup with integer keys."""
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'42'})
        d = dom.ElementDict(parent, 'key', self.Dummy, key_type=int)
        self.assertIs(d[42].element, child)

    def test_value_read_only(self):
        """
        Confirm attempting to assign a different value raises an exception.
        """
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(TypeError):
            d['foo'] = 0

    def test_create_new(self):
        """
        Confirm attempting to create a new key raises an exception.
        """
        parent = ElementTree.Element('parent')
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(TypeError):
            d['bar'] = 'foo'

    def test_names(self):
        """Confirm the names attribute returns a list of keys."""
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo'})
        ElementTree.SubElement(parent, 'child', {'key':'bar'})
        ElementTree.SubElement(parent, 'child', {'key':'baz'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        names = set(d.names)
        self.assertEqual(names, set(['foo', 'bar', 'baz']))

    def test_names_empty(self):
        """
        Confirm the names attribute returns an empty list when the parent has
        no child elements.
        """
        parent = ElementTree.Element('parent')
        d = dom.ElementDict(parent, 'key', self.Dummy)
        self.assertFalse(d.names)

    def test_names_attribute(self):
        """Confirm the key attribute is used to generate the names list."""
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo', 'attr':'spam'})
        ElementTree.SubElement(parent, 'child', {'key':'bar', 'attr':'eggs'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        names = set(d.names)
        self.assertEqual(names, set(['foo', 'bar']))

    def test_names_type(self):
        """Confirm names are converted to the correct key type."""
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'42'})
        d = dom.ElementDict(parent, 'key', self.Dummy, key_type=int)
        self.assertIsInstance(d.names[0], int)

    def test_names_read_only(self):
        """
        Confirm attempting to assign the names attributes raises an exception.
        """
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        with self.assertRaises(AttributeError):
            d.names = 'foo'

    def test_single_value_type(self):
        """
        Confirm an instance of the value type is returned when the value
        type is specified as a class.
        """
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy)
        self.assertIsInstance(d['foo'], self.Dummy)

    def test_single_value_type_args(self):
        """
        Confirm the target element and extra arguments are passed to
        the value class for single-type values.
        """
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child', {'key':'foo'})
        d = dom.ElementDict(parent, 'key', self.Dummy,
                            value_args=['spam', 'eggs'])
        self.assertIs(d['foo'].element, child)
        self.assertEqual(d['foo'].args, ('spam', 'eggs'))

    def test_value_type_by_attribute(self):
        """
        Confirm the type of value returned is selected by the type attribute
        when the value type is specified as a dictionary.
        """
        class Foo(self.Dummy): pass
        class Bar(self.Dummy): pass
        types = {'Foo':Foo, 'Bar':Bar}
        parent = ElementTree.Element('parent')
        ElementTree.SubElement(parent, 'child', {'key':'foo', 'type':'Foo'})
        ElementTree.SubElement(parent, 'child', {'key':'bar', 'type':'Bar'})
        d = dom.ElementDict(parent, 'key', types, type_attr='type')
        self.assertIsInstance(d['foo'], Foo)
        self.assertIsInstance(d['bar'], Bar)

    def test_value_type_by_attribute_args(self):
        """
        Confirm the target element and extra arguments are passed to
        the value class for value types selected by attribute.
        """
        class Foo(self.Dummy): pass
        types = {'Foo':Foo}
        parent = ElementTree.Element('parent')
        child = ElementTree.SubElement(parent, 'child',
                                       {'key':'foo', 'type':'Foo'})
        d = dom.ElementDict(parent, 'key', types, type_attr='type',
                        value_args=['spam', 'eggs'])
        self.assertIs(d['foo'].element, child)
        self.assertEqual(d['foo'].args, ('spam', 'eggs'))


class CDATAElement(unittest.TestCase):
    """Unit tests for the CDATAElement class."""
    def test_existing_get_string(self):
        """Confirm CDATA element content is retrieved as the object's string."""
        pass

    def test_existing_set_string(self):
        """Confirm CDATA element content is updated when set."""
        pass

    def test_existing_empty(self):
        """Confirm an existing empty element returns an empty string."""
        pass

    def test_existing_empty_self_closing(self):
        """Confirm a self-closing tag returns an empty string."""
        pass

    def test_new_cdata_child(self):
        """Confirm a single CDATA child is included when creating an element."""
        pass

    def test_new_tag(self):
        """Confirm tag name when creating a new element."""
        pass

    def test_new_parent(self):
        """Confirm placement under parent when creating a new element."""
        pass

    def test_new_attributes(self):
        """Confirm attribute assignment when creating a new element."""
        pass
