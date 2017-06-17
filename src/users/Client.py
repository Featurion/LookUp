import json
import os
import socket
import srp

from src.base.constants import CMD_LOGIN, CMD_REQ_ZONE, CMD_RESP, CMD_RESP_OK, CMD_REQ_CHALLENGE, CMD_RESP_CHALLENGE, CMD_VERIFY_CHALLENGE
from src.base.constants import CMD_RESP_NO, CMD_HELO, CMD_ZONE_MSG
from src.base.constants import HMAC_KEY
from src.base.Datagram import Datagram
from src.base.Node import Node
from src.users.ClientBase import ClientBase
from src.zones.Zone import Zone
from src.zones.ZoneManager import ZoneManager


class Client(ClientBase):

    def __init__(self, interface, address, port):
        ClientBase.__init__(self, address, port)
        self.interface = interface
        self.__pending_tabs = []
        self.setupSocket(socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM), True)
        self.getSocket().connect((self.getAddress(), self.getPort()))
        self.__challenge_complete = False

    def startManagers(self):
        """Start client managers"""
        self.zm = ZoneManager()

    def start(self):
        """Handle startup of the client"""
        ClientBase.start(self)
        self.doHandshake()
        self.interface.connected_signal.emit()

    def stop(self):
        """Handle stopping of the client"""
        if ClientBase.stop(self): # clean exit
            self.notify.debug('stopped client')
        else:
            self.terminate()

    def terminate(self):
        """Forcefully exit the client"""
        self.notify.info('failed to quit, force quitting')
        os.kill(os.getpid(), 9)

    def connect(self, name, callback):
        # HMAC verification
        hmac = self.generateHmac(name.encode(), HMAC_KEY, True)

        # Challenge verification
        self.user = srp.User(name.encode(), HMAC_KEY)
        uname, A = self.user.start_authentication()

        datagram = Datagram()
        datagram.setCommand(CMD_LOGIN)
        datagram.setRecipient(self.getId())
        datagram.setData(json.dumps([name, 'temp'])) # TODO: implement modes properly
        datagram.setHMAC(hmac)

        self.notify.info('logging in as {0}'.format(name))
        self.sendDatagram(datagram)

        if self.getResp() is True:
            self.setName(name)

            # Request a challenge
            datagram.setCommand(CMD_REQ_CHALLENGE)
            datagram.setData((uname.decode('latin-1'), A.decode('latin-1')))
            self.sendDatagram(datagram)

            while self.__challenge_complete is False:
                if self.__challenge_complete is True:
                    break
                else:
                    continue

            callback('')
        else:
            callback('placeholder rejection message') # TODO: replace message

    def doHandshake(self):
        """Respond to an initiated handshake"""
        self.receiveKey()
        self.sendKey()

    def _recv(self, data):
        datagram = Datagram.fromJSON(data)

        if datagram.getCommand() == CMD_RESP:
            self.setResp(datagram.getData())
        elif datagram.getCommand() == CMD_RESP_OK:
            self.setResp(True)
        elif datagram.getCommand() == CMD_RESP_NO:
            self.setResp(False)
        elif datagram.getCommand() == CMD_HELO:
            zone_id, key, member_ids, member_names = json.loads(datagram.getData())
            zone = self.zm.getZoneById(zone_id)
            if not zone:
                if member_names[0] != self.getName():
                    window = self.interface.getWindow()
                    window.new_client_signal.emit(zone_id, key, member_ids, member_names)
                else:
                    flag = False
                    for names, tab in self.__pending_tabs:
                        if names == member_names:
                            zone = Zone(tab, zone_id, key, member_ids)
                            self.enter(tab, zone)
                            zone.sendRedy()
                            flag = True

                    if not flag:
                        self.notify.error('ZoneError', 'could not find tab')
        elif datagram.getCommand() == CMD_ZONE_MSG:
            zone = self.zm.getZoneById(datagram.getSender())
            if zone:
                zone.recvDatagram(datagram)
            else:
                self.notify.warning('received suspicious zone datagram')
        elif datagram.getCommand() == CMD_RESP_CHALLENGE:
            s, B = datagram.getData()
            M = self.user.process_challenge(s.encode('latin-1'), B.encode('latin-1'))

            if M is None:
                self.notify.error('AuthenticationError', 'suspicious challenge failure')

            datagram.setCommand(CMD_RESP_CHALLENGE)
            datagram.setData(M.decode('latin-1'))
            self.sendDatagram(datagram)
        elif datagram.getCommand() == CMD_VERIFY_CHALLENGE:
            HAMK = datagram.getData()
            HAMK = HAMK.encode('latin-1')

            # Finish the authentication process
            self.user.verify_session(HAMK)

            if self.user.authenticated():
                self.__challenge_complete = True
            else:
                self.notify.critical('suspiciously failed to complete challenge')
        else:
            self.notify.warning('received suspicious datagram')

        return data

    def enter(self, tab, zone):
        tab.setZone(zone)
        self.zm.addZone(zone)
        self.notify.debug('entered zone {0}'.format(zone.getId()))

    def requestNewZone(self, tab, member_names):
        datagram = Datagram()
        datagram.setCommand(CMD_REQ_ZONE)
        datagram.setRecipient(self.getId())
        datagram.setData(json.dumps([self.getName()] + member_names))

        self.notify.debug('requesting new zone')
        self.sendDatagram(datagram)

        self.__pending_tabs.append((tuple(member_names), tab))
