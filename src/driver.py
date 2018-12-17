from sentry.pm_pdu_handler import PmPduHandler
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import InitCommandContext
from log_helper import LogHelper
from data_model import *


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
        resource = SentryPdu.create_from_context(context)
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

        resource = SentryPdu.create_from_context(context)
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
        resource = SentryPdu.create_from_context(context)
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.power_off(ports)

    def PowerOn(self, context, ports):
        """

        :param context:
        :param ports:
        :type  ports: list of str
        :return:
        """
        resource = SentryPdu.create_from_context(context)
        logger = LogHelper.get_logger(context)

        handler = PmPduHandler(context.resource.address, resource, logger)

        return handler.power_on(ports)

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
