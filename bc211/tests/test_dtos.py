import unittest
from bc211 import dtos, exceptions

class TestOrganization(unittest.TestCase):
    def test_throws_on_missing_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.Organization(name='name')

    def test_throws_on_missing_name(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.Organization(id='id')


class TestLocation(unittest.TestCase):
    def test_throws_on_missing_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.Location(name='name', organization_id='organization_id')

    def test_throws_on_missing_name(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.Location(id='id', organization_id='organization_id')

    def test_throws_on_missing_organization_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.Location(id='id', name='name')


class TestSpatialLocation(unittest.TestCase):
    def test_can_create(self):
        location = dtos.SpatialLocation(latitude='123.456', longitude='-23.456')
        self.assertAlmostEqual(location.latitude, 123.456)
        self.assertAlmostEqual(location.longitude, -23.456)

    def test_throws_on_latitude_not_a_number(self):
        with self.assertRaises(exceptions.InvalidFloatXmlParseException):
            dtos.SpatialLocation(latitude='foo', longitude='-23.456')

    def test_throws_on_longitude_not_a_number(self):
        with self.assertRaises(exceptions.InvalidFloatXmlParseException):
            dtos.SpatialLocation(latitude='123.456', longitude='foo')


class TestService(unittest.TestCase):
    def test_can_create(self):
        service = dtos.Service(id='id', name='name', organization_id='organization_id', site_id='site_id', description='description')
        self.assertEqual(service.id, 'id')
        self.assertEqual(service.name, 'name')
        self.assertEqual(service.organization_id, 'organization_id')
        self.assertEqual(service.site_id, 'site_id')
        self.assertEqual(service.description, 'description')

    def test_throws_on_missing_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(name='name', organization_id='organization_id', site_id='site_id', description='description')

    def test_throws_on_missing_name(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(id='id', organization_id='organization_id', site_id='site_id', description='description')

    def test_throws_on_missing_organization_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(id='id', name='name', site_id='site_id', description='description')

    def test_throws_on_missing_site_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(id='id', name='name', organization_id='organization_id', description='description')

class TestTaxonomyTerm(unittest.TestCase):
    def test_can_create(self):
        taxonomy_term = dtos.TaxonomyTerm(taxonomy_id='taxonomy_id', name='name')
        self.assertEqual(taxonomy_term.taxonomy_id, 'taxonomy_id')
        self.assertEqual(taxonomy_term.name, 'name')

    def test_throws_on_missing_taxonomy_id(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(name='name')

    def test_throws_on_missing_name(self):
        with self.assertRaises(exceptions.MissingRequiredFieldXmlParseException):
            dtos.TaxonomyTerm(taxonomy_id='taxonomy_id')
