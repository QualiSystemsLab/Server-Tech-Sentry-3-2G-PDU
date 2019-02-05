from sentry.autoload.pm_pdu_autoloader import PmPduAutoloader
from sentry.snmp_handler import SnmpHandler
from pysnmp.proto.rfc1902 import Integer
from pysnmp.smi.rfc1902 import ObjectIdentity
from time import sleep


class PmPduHandler:
    class Port:
        def __init__(self, port):
            self.address, port_details = port.split('/')
            # ToDo Verify port_number is the correct name for the first value
            # ToDo value checking on port_details. Should be SNMP index value
            self.port_number, self.pdu_number, self.outlet_number = port_details.split('.')

    def __init__(self, address, resource, logger):
        """

        :param address: The address of the resource to connect to
        :type  address: str
        :param resource: The resource object to connect to
        :param logger:
        :type  logger: logging.Logger
        """
        self.address = address
        self.resource = resource
        self.logger = logger

        self.snmp_handler = SnmpHandler(self.address, self.resource, self.logger)

    def get_inventory(self):
        """ Reads & returns the resource structure from the PDU via SNMP """
        return PmPduAutoloader(self.snmp_handler, self.logger).autoload()
#        return PmPduAutoloader(self.address, self.resource, self.logger).autoload()


    def power_cycle(self, port_list, delay):
        """
        Powers off, sleeps, powers on a list of 1 or more ports

        :param port_list: List of ports' relative addresses to power cycle
        :type port_list: list of str
        :param delay: number of seconds to delay between power off and power on
        :type delay: float
        :return: None
        """
        self.logger.info("Power cycle starting for ports %s" % port_list)

        self.power_off(port_list)

        self.logger.info("Sleeping %f second(s)" % delay)
        sleep(delay)

        self.power_on(port_list)

        self.logger.info("Power cycle complete for ports %s" % port_list)
        return "Power Cycle: Success"

    def power_off(self, port_list):
        self.logger.info("Power off called for ports %s" % port_list)
        for raw_port in port_list:
            self.logger.info("Powering off port %s" % raw_port)
            port = self.Port(raw_port)
            # TODO Change the Integer(2) harcoding to use the named value "off"
            self.snmp_handler.set(ObjectIdentity('Sentry3-MIB',
                                                 'outletControlAction',
                                                 port.port_number,
                                                 port.pdu_number,
                                                 port.outlet_number),
                                  Integer(2))
            status = self.snmp_handler.get(('Sentry3-MIB',
                                            'outletStatus',
                                            port.port_number,
                                            port.pdu_number,
                                            port.outlet_number))['outletStatus']
            self.logger.info("Port {} is now: ".format(raw_port) + status)
        return "Power Off: Success"

    def power_on(self, port_list):
        self.logger.info("Power on called for ports %s" % port_list)
        for raw_port in port_list:
            self.logger.info("Powering on port %s" % raw_port)
            port = self.Port(raw_port)
            # TODO Change the Integer(1) hardcoding to use the named value "on"
            self.snmp_handler.set(ObjectIdentity('Sentry3-MIB',
                                                 'outletControlAction',
                                                 port.port_number,
                                                 port.pdu_number,
                                                 port.outlet_number),
                                  Integer(1))
            status = self.snmp_handler.get(('Sentry3-MIB',
                                            'outletStatus',
                                            port.port_number,
                                            port.pdu_number,
                                            port.outlet_number))['outletStatus']
            self.logger.info("Port {} is now: ".format(raw_port) + status)

        return "Power On: Success"
