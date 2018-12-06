from sentry.snmp_handler import SnmpHandler
from cloudshell.shell.core.driver_context import AutoLoadResource, AutoLoadDetails, AutoLoadAttribute
from log_helper import LogHelper
from data_model import *


class PmPduAutoloader:
    def __init__(self, context):
        self.context = context
        self.logger = LogHelper.get_logger(self.context)
        self.snmp_handler = SnmpHandler(self.context).get_raw_handler('get')
        self.resource = Sentry3G2Pdu.create_from_context(context)

    def autoload(self):
        rv = AutoLoadDetails(resources=[], attributes=[])

        sysobject = self.snmp_handler.get_property('SNMPv2-MIB', 'sysObjectID', 0, return_type="str")
        if sysobject != 'Sentry3-MIB::sentry3':
            raise AssertionError("Device does not appear to be a Sentry3")

        # rv.attributes.append(self.makeattr('', 'CS_PDU.Location', self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Location', self.snmp_handler.get_property('Sentry3-MIB', 'systemLocation', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Model',  'Sentry3'))
        rv.attributes.append(self.makeattr('', 'Sentry3G2Pdu.NIC Serial Number', self.snmp_handler.get_property('Sentry3-MIB', 'systemNICSerialNumber', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Vendor', 'ServerTech'))
        rv.attributes.append(self.makeattr('', 'Sentry3G2Pdu.System Version', self.snmp_handler.get_property('Sentry3-MIB', 'systemVersion', 0)))

        pdu_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', 0)

        outlet_table = self.snmp_handler.get_table('Sentry3-MIB', 'outletTable')
        for index, attribute in outlet_table.iteritems():
            name = attribute['outletID']
            relative_address = name
            unique_identifier = '%s.%s' % (pdu_name, name)

            rv.resources.append(self.makeres(name, 'Sentry3G2Pdu.PowerSocket', relative_address, unique_identifier))
            #TODO The outletName should be added as an attribute for the power sockets
            # rv.attributes.append(self.makeattr(relative_address, 'CS_PowerSocket.Model Name', attribute['outletName']))

        return rv

    def makeattr(self, relative_address, attribute_name, attribute_value):
        return AutoLoadAttribute(relative_address=relative_address,
                                 attribute_name=attribute_name,
                                 attribute_value=attribute_value)

    def makeres(self, name, model, relative_address, unique_identifier):
        return AutoLoadResource(name=name, model=model,
                                relative_address=relative_address,
                                unique_identifier=unique_identifier)
