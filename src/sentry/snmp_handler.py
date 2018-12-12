import os

from cloudshell.shell.core.context_utils import get_attribute_by_name
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters, SNMPV2ReadParameters
from pysnmp.smi.rfc1902 import ObjectType
from cloudshell.core.logger.qs_logger import get_qs_logger


class SnmpHandler:
    def __init__(self, context, resource, logger):
        self.context = context
        self.resource = resource
        self.logger = logger


        self.address = self.context.resource.address
        self.community_read = self.resource.snmp_read_community or 'public'

        logger.info('Community_read: {0}'.format(self.community_read))

        self.community_write = self.resource.snmp_write_community or 'private'

        logger.info('Community_write: {0}'.format(self.community_write))

        self.password = self.resource.snmp_v3_password or ''
        self.user =  self.resource.snmp_v3_user or ''
        self.version = self.resource.snmp_version or ''
        self.private_key = self.resource.snmp_v3_private_key

        logger.info('snmp_v3_user: {0}'.format(self.user))
        logger.info('snmp_v3_password: {0}'.format(self.password))
        logger.info('private_key: {0}'.format(self.private_key))

    def get(self, object_identity):
        handler = self._get_handler('get')

        return handler.get(ObjectType(object_identity))

    def set(self, object_identity, value):
        handler = self._get_handler('set')

        return handler._command(handler.cmd_gen.setCmd, ObjectType(object_identity, value))

    def get_raw_handler(self, action):
        return self._get_handler(action)

    def _get_handler(self, action):
        mib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mibs'))
        snmp_parameters = self._get_snmp_parameters(action)

        handler = QualiSnmp(snmp_parameters, self.logger)
        handler.update_mib_sources(mib_path)
        handler.load_mib(['Sentry3-MIB'])

        return handler

    def _get_snmp_parameters(self, action):
        if '3' in self.version:
            return SNMPV3Parameters(ip=self.address, snmp_user=self.user, snmp_password=self.password, snmp_private_key=self.private_key)
        else:
            if action.lower() == 'set':
                # community = self.community_write
                return SNMPV2WriteParameters(ip=self.address, snmp_write_community=self.community_write)
            else:
                # community = self.community_read
                return SNMPV2ReadParameters(ip=self.address, snmp_read_community=self.community_read)
            # return SNMPV2Parameters(ip=self.address, snmp_community=community)
