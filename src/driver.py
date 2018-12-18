from sentry.pm_pdu_handler import PmPduHandler
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext
from log_helper import LogHelper
from data_model import *
from cloudshell.api.cloudshell_api import CloudShellAPISession


class SentryPduDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize is empty since we're storing no state
        Initialize the driver session, this function is called every time a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.

        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def get_inventory(self, context):
        resource = self._decrypt_resource_passwords(context,
            SentryPdu.create_from_context(context))
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.get_inventory()

    def PowerCycle(self, context, ports, delay):
        """

        :param context:
        :param ports:
        :type  ports: list of str
        :param delay:
        :type  delay: float
        :return:
        """
        try:
            float(delay)
        except ValueError:
            raise Exception('Delay must be a numeric value')

        resource = self._decrypt_resource_passwords(context,
            SentryPdu.create_from_context(context))
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.power_cycle(ports, float(delay))

    def PowerOff(self, context, ports):
        """

        :param context:
        :param ports:
        :type  ports: list of str
        :return:
        """

        resource = self._decrypt_resource_passwords(context,
            SentryPdu.create_from_context(context))
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.power_off(ports)

    def PowerOn(self, context, ports):
        """

        :param context:
        :param ports: list of port addresses to power cycle
        :type  ports: list of str
        :return:
        """
        resource = self._decrypt_resource_passwords(context,
            SentryPdu.create_from_context(context))
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.power_on(ports)

    def _decrypt_resource_passwords(self, context, resource):
        """

        :param context:
        :param resource: SentryPdu resource object with encrypted passwords
        :type  resource: SentryPdu
        :return: the resource object with the passwords decrypted
        :rtype : SentryPdu
        """
        logger = LogHelper.get_logger(context)

        try:
            domain = context.reservation.domain
        except:
            domain = 'Global'

        logger.info("Creating API Session")
        api = CloudShellAPISession(context.connectivity.server_address,
                                   token_id=context.connectivity.admin_auth_token,
                                   port=context.connectivity.cloudshell_api_port,
                                   domain=domain)

        attributes_to_decrypt = ('snmp_write_community', 'snmp_read_community',
                                 'snmp_v3_password', 'snmp_v3_private_key',
                                 'password')
        for pass_attribute in attributes_to_decrypt:
            logger.info("Attempting decryption of password value at {}".format(pass_attribute))
            value = getattr(resource, pass_attribute)
            if value is None:
                # logger.info("    Skipping Decryption of {}: Value is None".format(pass_attribute))
                continue
            elif value.endswith('=='):
                # logger.info("    Decrypting {}: Detected encrypted value {}".format(pass_attribute, value))
                setattr(resource, pass_attribute, api.DecryptPassword(value).Value)
                # logger.info("        Got: {}".format(getattr(resource, pass_attribute)))
                continue
            else:
                # logger.info("    Skipping Decryption of {}: Unable to determine type for: {}".format(pass_attribute, value))
                pass

        return resource

if __name__ == "__main__":
    import mock
    from cloudshell.shell.core.driver_context import CancellationContext
    import cloudshell.api.cloudshell_api as cs_api
    shell_name = "SentryPdu"

    cancellation_context = mock.create_autospec(CancellationContext)
    context = mock.create_autospec(ResourceCommandContext)
    context.resource = mock.MagicMock()
    context.reservation = mock.MagicMock()
    context.connectivity = mock.MagicMock()
    context.reservation.reservation_id = "<Reservation ID>"
    context.resource.address = "10.16.145.249"  # Sentry 3
    context.resource.name = "Debug_Sentry3"
    context.resource.attributes = dict()
    context.resource.attributes["{}.User".format(shell_name)] = "admn"
    context.resource.attributes["{}.Password".format(shell_name)] = "admn"
    context.resource.attributes["{}.SNMP Read Community".format(shell_name)] = "public"
    context.resource.attributes["{}.SNMP Write Community".format(shell_name)] = "private"
    cs_session = cs_api.CloudShellAPISession("localhost",
                                             "admin",
                                             "admin",
                                             domain="Global",
                                             port=8029)
    context.connectivity.cloudshell_api_port = cs_session.port
    context.connectivity.server_address = cs_session.host
    context.connectivity.admin_auth_token = cs_session.token_id

    driver = SentryPduDriver()
    # print driver.run_custom_command(context, custom_command="sh run", cancellation_context=cancellation_context)
    driver.initialize(context)
    result = driver.get_inventory(context)

    print "done"
