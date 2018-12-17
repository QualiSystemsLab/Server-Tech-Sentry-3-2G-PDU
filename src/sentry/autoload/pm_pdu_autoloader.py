# from sentry.snmp_handler import SnmpHandler
from cloudshell.shell.core.driver_context import AutoLoadResource, AutoLoadDetails, AutoLoadAttribute
# from cloudshell.shell.core.driver_context import AutoLoadDetails
# from data_model import *


class PmPduAutoloader:
#    def __init__(self, address, resource, logger):
    def __init__(self, snmp_handler, logger):
        self.snmp_handler = snmp_handler.get_raw_handler('get')
        self.logger = logger

#        self.snmp_handler = SnmpHandler(address, resource, self.logger).get_raw_handler('get')

    def autoload(self):
        rv = AutoLoadDetails(resources=[], attributes=[])

        rv.attributes.append(self.makeattr('', 'CS_PDU.Location', self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', 0)))
        # rv.attributes.append(self.makeattr('', 'Location', self.snmp_handler.get_property('SNMPv2-MIB', 'systemLocation', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Model', self.snmp_handler.get_property('Sentry3-MIB', 'towerModelNumber', 0)))
        rv.attributes.append(self.makeattr('', 'SentryPdu.Serial Number', self.snmp_handler.get_property('Sentry3-MIB', 'towerProductSN', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Vendor', 'Sentry'))
        rv.attributes.append(self.makeattr('', 'SentryPdu.System Version', self.snmp_handler.get_property('Sentry3-MIB', 'systemVersion', 0)))

        pdu_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', 0)

        outlet_table = self.snmp_handler.get_table('Sentry3-MIB', 'outletTable')
        for index, attribute in outlet_table.iteritems():
            name = 'Outlet %s' % index
            relative_address = index
            unique_identifier = '%s.%s' % (pdu_name, index)

            rv.resources.append(self.makeres(name, 'SentryPdu.PowerSocket', relative_address, unique_identifier))
            #rv.attributes.append(self.makeattr(relative_address, 'CS_PowerSocket.Model Name', attribute['outletName']))

        return rv

    def makeattr(self, relative_address, attribute_name, attribute_value):
        return AutoLoadAttribute(relative_address=relative_address,
                                 attribute_name=attribute_name,
                                 attribute_value=attribute_value)

    def makeres(self, name, model, relative_address, unique_identifier):
        return AutoLoadResource(name=name, model=model,
                                relative_address=relative_address,
                                unique_identifier=unique_identifier)
