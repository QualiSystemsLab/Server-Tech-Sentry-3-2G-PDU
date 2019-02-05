import os

from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters, SNMPV2ReadParameters
from pysnmp.smi.rfc1902 import ObjectType

class SnmpHandler:
    """ Generic SNMP Handler for any resource """
    def __init__(self, address, resource, logger):
        """
        Initializes the SnmpHandler to connect to the resource

        :param address: The address of the resource to connect to
        :type address: str
        :param resource: The resource object to connect to
        :param logger:
        :type logger: logging.Logger
        """
        self.logger = logger

        self.address = address
        self.snmp_version = resource.snmp_version or 'v2c'

        self.snmp_read_community = resource.snmp_read_community or 'public'
        self.snmp_write_community = resource.snmp_write_community or 'private'

        self.snmp_v3_user = resource.snmp_v3_user or None
        self.snmp_v3_password = resource.snmp_v3_password or None
        self.snmp_v3_private_key = resource.snmp_v3_private_key or None

        # logger.info('SNMP Handler Created\n    ' + '\n    '.join("%s: %s" % item for item in sorted(vars(self).items())))

    def get(self, object_identity):
        """ Returns the value at object_identity """
        return self._handler('get').get(object_identity)

    # TODO function untested
    def set(self, object_identity, value):
        """ Sets the value at object_identity"""
        # TODO This should not use the internal _command function
        handler = self._handler('set')
        return handler._command(handler.cmd_gen.setCmd, ObjectType(object_identity, value))

    def get_raw_handler(self, action):
        """"
        Creates & returns an SNMP handler for the desired action-set or get

        :param action: The desired action. 'get' or 'set'
        :return:
        :rtype: QualiSnmp
        """
        return self._handler(action)

    def _handler(self, action):
        """
        Sets up an SNMP handler with the current SNMPHandler state

        :rtype: QualiSnmp
        """
        mib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mibs'))
        snmp_parameters = self._snmp_parameters(action)

        try:
            handler = QualiSnmp(snmp_parameters, self.logger)
        except Exception as e:
            if action.lower() == 'get':
                error = '''Unable to communicate via SNMP read to resource
                Please verify the SNMP read community and that the device is accessible'''
            elif action.lower() == 'set':
                error = '''Unable to communicate via SNMP write to resource
                Please verify the SNMP write community and that the device is accessible'''
            else:
                error = '''Unable to communicate via SNMP to resource
                Please verify the SNMP communities and that the device is accessible'''
            raise Exception(error + '\nDownstream error: ' + str(e))
        handler.update_mib_sources(mib_path)
        handler.load_mib(['Sentry3-MIB'])

        return handler

    def _snmp_parameters(self, action):
        """ Returns the SNMPHandler state variables for the specific action"""
        if self.snmp_version == 'v3':
            return SNMPV3Parameters(ip=self.address,
                                    snmp_user=self.snmp_v3_user,
                                    snmp_password=self.snmp_v3_password,
                                    snmp_private_key=self.snmp_v3_private_key)
        if self.snmp_version.startswith('v2'):
            if action.lower() == 'set':
                return SNMPV2WriteParameters(ip=self.address,
                                             snmp_write_community=self.snmp_write_community)
            if action.lower() == 'get':
                return SNMPV2ReadParameters(ip=self.address,
                                            snmp_read_community=self.snmp_read_community)
            else:
                ValueError("Function argument 'action' should be either 'get' or 'set'")
        else:
            ValueError("Unknown SNMP version set on resource")

