import json

from src.base.globals import CMD_LOGIN, CMD_REQ_ZONE
from src.base.Datagram import Datagram
from src.userbase.Node import Node
from src.zones.Zone import Zone
from src.zones.ZoneManager import ZoneManager

class Client(Node):

    def __init__(self, interface, address, port):
        Node.__init__(self, address, port, None)
        self.interface = interface
        self.zone_manager = ZoneManager()

    def start(self):
        Node.start(self)
        self.interface.connected_signal.emit()

    def connect(self, name, callback):
        datagram = Datagram()
        datagram.setCommand(CMD_LOGIN)
        datagram.setRecipient(self.getId())
        datagram.setData(name)

        self.notify.info('logging in as {0}-{1}'.format(name, self.getId()))
        self.sendDatagram(datagram)

        if self.getResp():
            self.setName(name)
            callback('')
        else:
            callback('placeholder rejection message') # replace

    def enteredZone(self, tab, zone_id, member_ids):
        zone = Zone(tab, zone_id, member_ids)
        self.zone_manager.addZone(zone)
        self.notify.debug('entered zone {0}'.format(zone_id))

        tab.setZone(zone)

    def requestNewZone(self, tab, member_names):
        datagram = Datagram()
        datagram.setCommand(CMD_REQ_ZONE)
        datagram.setRecipient(self.getId())
        datagram.setData(json.dumps([self.getName()] + member_names))

        self.notify.debug('requesting new zone')
        self.sendDatagram(datagram)

        self.enteredZone(tab, *json.loads(self.getResp()))
