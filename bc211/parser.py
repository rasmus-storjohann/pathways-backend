import itertools
import logging
import re
import xml.etree.ElementTree as etree
from urllib import parse as urlparse

from bc211 import dtos
from bc211.exceptions import MissingRequiredFieldXmlParseException

LOGGER = logging.getLogger(__name__)

def read_records_from_file(file):
    xml = file.read()
    return parse(xml)

def parse(xml_data_as_string):
    root_xml = etree.fromstring(xml_data_as_string)
    agencies = root_xml.findall('Agency')
    return map(parse_agency, agencies)

def parse_agency(agency):
    id = parse_agency_key(agency)
    name = parse_agency_name(agency)
    description = parse_agency_description(agency)
    website = parse_agency_website_with_prefix(agency)
    email = parse_agency_email(agency)
    LOGGER.debug('Organization "%s" "%s"', id, name)
    locations = parse_sites(agency, id)
    return dtos.Organization(id=id, name=name, description=description, website=website,
                             email=email, locations=locations)

def parse_agency_key(agency):
    return parse_required_field(agency, 'Key')

def parse_required_field(parent, field):
    try:
        return parent.find(field).text
    except AttributeError:
        raise MissingRequiredFieldXmlParseException('Missing required field: "{0}"'.format(field))

def parse_optional_field(parent, field):
    value = parent.find(field)
    return None if value is None else value.text

def parse_agency_name(agency):
    return parse_required_field(agency, 'Name')

def parse_agency_description(agency):
    return parse_required_field(agency, 'AgencyDescription')

def parse_agency_email(agency):
    return parse_optional_field(agency, 'Email/Address')

def parse_agency_website_with_prefix(agency):
    website = parse_optional_field(agency, 'URL/Address')
    return None if website is None else website_with_http_prefix(website)

def website_with_http_prefix(website):
    parts = urlparse.urlparse(website, 'http')
    whole_with_extra_slash = urlparse.urlunparse(parts)
    return whole_with_extra_slash.replace('///', '//')

def parse_sites(agency, organization_id):
    sites = agency.findall('Site')
    return map(SiteParser(organization_id), sites)

class SiteParser:
    def __init__(self, organization_id):
        self.organization_id = organization_id

    def __call__(self, site):
        return parse_site(site, self.organization_id)

def parse_site(site, organization_id):
    id = parse_site_id(site)
    name = parse_site_name(site)
    description = parse_site_description(site)
    spatial_location = parse_spatial_location_if_defined(site)
    services = parse_services(site, organization_id, id)
    physical_address = parse_physical_address(site, id)
    postal_address = parse_postal_address(site, id)
    LOGGER.info('Parsed location: %s %s', id, name)
    return dtos.Location(id=id, name=name, organization_id=organization_id,
                         description=description, spatial_location=spatial_location,
                         services=services, physical_address=physical_address,
                         postal_address=postal_address)

def parse_site_id(site):
    return parse_required_field(site, 'Key')

def parse_site_name(site):
    return parse_required_field(site, 'Name')

def parse_site_description(site):
    return parse_required_field(site, 'SiteDescription')

def parse_spatial_location_if_defined(site):
    latitude = parse_optional_field(site, 'SpatialLocation/Latitude')
    longitude = parse_optional_field(site, 'SpatialLocation/Longitude')
    if latitude is None or longitude is None:
        return None
    return dtos.SpatialLocation(latitude=latitude, longitude=longitude)

def parse_services(site, organization_id, site_id):
    services = site.findall('SiteService')
    return map(ServiceParser(organization_id, site_id), services)

class ServiceParser:
    def __init__(self, organization_id, site_id):
        self.organization_id = organization_id
        self.site_id = site_id

    def __call__(self, service):
        return parse_service(service, self.organization_id, self.site_id)

def parse_service(service, organization_id, site_id):
    id = parse_service_id(service)
    name = parse_service_name(service)
    description = parse_service_description(service)
    taxonomy_terms = parse_service_taxonomy_terms(service, id)
    LOGGER.debug('Service: "%s" "%s"', id, name)
    return dtos.Service(id=id, name=name, organization_id=organization_id,
                        site_id=site_id, description=description,
                        taxonomy_terms=taxonomy_terms)

def parse_service_id(service):
    return parse_required_field(service, 'Key')

def parse_service_name(service):
    return parse_required_field(service, 'Name')

def parse_service_description(service):
    return parse_required_field(service, 'Description')

def parse_service_taxonomy_terms(service, service_id):
    taxonomy_terms = service.findall('Taxonomy')
    return itertools.chain.from_iterable(
        map(ServiceTaxonomyTermParser(service_id), taxonomy_terms)
    )

class ServiceTaxonomyTermParser:
    def __init__(self, service_id):
        self.service_id = service_id

    def __call__(self, service_taxonomy_term):
        return parse_service_taxonomy_term(service_taxonomy_term, self.service_id)

def parse_service_taxonomy_term(service_taxonomy_term, service_id):
    code = parse_required_field(service_taxonomy_term, 'Code')

    LOGGER.debug('Taxonomy term "%s"', code)

    if code and is_bc211_taxonomy_term(code):
        yield from parse_bc211_taxonomy_term(code)
    elif code:
        yield from parse_airs_taxonomy_term(code)

def is_bc211_taxonomy_term(code_str):
    return code_str.startswith('{')

def parse_bc211_taxonomy_term(code_str):
    bc211_json_re = r"(\w+)\:\'([^\']+)\'"
    groups = re.findall(bc211_json_re, code_str)
    for (taxonomy_id, name) in groups:
        full_taxonomy_id = 'bc211-{}'.format(taxonomy_id)
        yield dtos.TaxonomyTerm(taxonomy_id=full_taxonomy_id, name=name)

def parse_airs_taxonomy_term(code_str):
    taxonomy_id = 'airs'
    yield dtos.TaxonomyTerm(taxonomy_id=taxonomy_id, name=code_str)

def parse_physical_address(site, site_id):
    type_id = 'physical_address'
    return parse_address(site.find('PhysicalAddress'), site_id, type_id)

def parse_postal_address(site, site_id):
    type_id = 'postal_address'
    return parse_address(site.find('MailingAddress'), site_id, type_id)

def parse_address(address, site_id, address_type_id):
    address_lines = parse_address_lines(address)
    city = parse_city(address)
    country = parse_country(address)
    if not address_lines or not city or not country:
        LOGGER.warning('Unable to create address for location: "%s". '
                       'Parsed "%s" for address, "%s" for city, and "%s" for country.',
                       site_id, address_lines, city, country)
        return None
    state_province = parse_state_province(address)
    postal_code = parse_postal_code(address)
    return dtos.Address(location_id=site_id, address_lines=address_lines,
                        city=city, state_province=state_province, postal_code=postal_code,
                        country=country, address_type_id=address_type_id)

def parse_address_lines(address):
    line_1 = parse_required_field(address, 'Line1')
    if not line_1:
        return None
    address_lines = [line_1]
    address_children = sorted(address.getchildren(), key=lambda child: child.tag)
    for child in address_children:
        if re.match("Line[2-4]", child.tag):
            address_line = parse_required_field(address, child.tag)
            address_lines.append(address_line)
        if re.match("Line[5-9]", child.tag):
            LOGGER.warning('Tag %s encountered and has not been parsed.', child.tag)
    return '\n'.join(address_lines)

def parse_city(address):
    return parse_required_field(address, 'City')

def parse_country(address):
    return parse_required_field(address, 'Country')

def parse_state_province(address):
    return parse_optional_field(address, 'State')

def parse_postal_code(address):
    return parse_optional_field(address, 'ZipCode')
