# from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
# from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
#     AutoLoadAttribute, AutoLoadDetails, CancellationContext
#from data_model import *  # run 'shellfoundry generate' to generate data model classes

from sentry.pm_pdu_handler import PmPduHandler
from cloudshell.power.pdu.power_resource_driver_interface import PowerResourceDriverInterface
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import AutoLoadDetails, InitCommandContext, ResourceCommandContext
from log_helper import LogHelper


class Sentry3G2PduDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
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
        handler = PmPduHandler(context)

        return handler.get_inventory()

    def PowerCycle(self, context, ports, delay):
        try:
            float(delay)
        except ValueError:
            raise Exception('Delay must be a numeric value')

        handler = PmPduHandler(context)
        return handler.power_cycle(ports, float(delay))

    def PowerOff(self, context, ports):
        handler = PmPduHandler(context)

        return handler.power_off(ports)

    def PowerOn(self, context, ports):
        handler = PmPduHandler(context)

        return handler.power_on(ports)



if __name__ == "__main__":
    import mock
    from cloudshell.shell.core.driver_context import CancellationContext
    shell_name = "Sentry3G2Pdu"

    cancellation_context = mock.create_autospec(CancellationContext)
    context = mock.create_autospec(ResourceCommandContext)
    context.resource = mock.MagicMock()
    context.reservation = mock.MagicMock()
    context.connectivity = mock.MagicMock()
#    context.reservation.reservation_id = "102996cc-2099-4c96-ac7d-44a27974c49a"
#    context.resource.address = "10.11.100.251" # Sentry 4
#    context.resource.address = "10.16.145.249"  # Sentry 3
    context.resource.name = "Debug_Sentry3"
    context.resource.attributes = dict()
    context.resource.attributes["{}.User".format(shell_name)] = "admn"
    context.resource.attributes["{}.Password".format(shell_name)] = "admn"
    context.resource.attributes["{}.SNMP Read Community".format(shell_name)] = "public"
    context.resource.attributes["{}.SNMP Write Community".format(shell_name)] = "private"

    driver = Sentry3G2PduDriver()
    # print driver.run_custom_command(context, custom_command="sh run", cancellation_context=cancellation_context)
    driver.initialize(context)
    result = driver.get_inventory(context)

    print "done"