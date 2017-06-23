import os
import socket
import srp
import ssl
import uuid

from src.base import constants
from src.base.Datagram import Datagram
from src.base.Node import Node
from src.users.ClientBase import ClientBase
from src.zones.Zone import Zone
from src.zones.ZoneManager import ZoneManager


class Client(ClientBase):

    def __init__(self, interface, address, port):
        ClientBase.__init__(self, address, port)
        self.interface = interface
        self.zm = None
        self.__pending_tabs = []

        self.COMMAND_MAP.update({
            constants.CMD_ERR: self.doError,
            constants.CMD_HELO: self.doHelo,
            constants.CMD_ZONE_MSG: self.forwardZoneDatagram,
        })

    def start(self):
        """Handle startup of the client"""
        ClientBase.start(self)
        self.initiateHandshake()
        self.interface.connected_signal.emit()

    def startManagers(self):
        """Start client managers"""
        self.zm = ZoneManager()

    def stop(self):
        """Handle stopping of the client"""
        self.notify.info('disconnecting from the server...')
        ClientBase.stop(self)

        if self.isSending:
            self.notify.error('ExitError', 'an error occurred while halting datagram sending')

        if self.isReceiving:
            self.notify.error('ExitError', 'an error occurred while halting datagram receiving')

        if not self.isAlive:
            self.notify.debug('stopped client')
        else:
            self.terminate()

    def cleanup(self):
        ClientBase.cleanup(self)
        if self.interface:
            self.interface.cleanup()
            del self.interface
            self.interface = None
        if self.zm:
            self.zm.cleanup()
            del self.zm
            self.zm = None
        if self.__pending_tabs:
            for _t in self.__pending_tabs:
                del _t
            del self.__pending_tabs[:]
            del self.__pending_tabs
            self.__pending_tabs = None

    def connect(self, address, port):
        try:
            self.getSocket().connect((address, port))
        except ssl.SSLError as e:
            self.notify.critical('error establishing ssl')
        except Exception as e:
            self.notify.critical(str(e))

        response = self.waitForApproval()
        if response == True:
            pass
        else:
            self.interface.error_signal.emit(constants.TITLE_BANNED, constants.CLIENT_BANNED)

        del address
        del port

    def waitForApproval(self):
        while True:
            recv = self.getSocket().recv(1024)
            if recv == constants.ACCEPTED:
                return True
            elif recv == constants.BANNED:
                return False
            else:
                continue

    def terminate(self):
        """Forcefully exit the client"""
        self.notify.info('failed to quit, force quitting')
        os.kill(os.getpid(), 9)

    def setupSocket(self):
        self.setSocket(self.__buildSocket())

        try:
            self.connect(self.getAddress(), self.getPort())
            self.notify.info('connected to server')
        except ConnectionRefusedError:
            self.notify.error('ConnectionError', 'could not connect to server')
        except Exception as e:
            self.notify.error('ConnectionError', str(e))
            self.stop()

        ClientBase.setupSocket(self)

    def __buildSocket(self):
        try:
            if constants.TLS_ENABLED:
                self.notify.info('connecting with SSL')
                return ssl.wrap_socket(socket.socket(socket.AF_INET,
                                                     socket.SOCK_STREAM),
                                       ca_certs="certs/pem.crt",
                                       cert_reqs=ssl.CERT_REQUIRED,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2,
                                       ciphers='ECDHE-RSA-AES256-GCM-SHA384')
            else:
                self.notify.info('connecting without SSL')
                return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except ssl.SSLError as e:
            self.notify.error('SSLError', str(e))

    def sendDatagram(self, datagram):
        datagram.setSender(self.getId())
        ClientBase.sendDatagram(self, datagram)

        del datagram

    def enter(self, tab, zone):
        tab.setZone(zone)
        self.zm.addZone(zone)
        self.notify.debug('entered zone {0}'.format(zone.getId()))

        del tab
        del zone

    def doError(self, datagram):
        title, err = datagram.getData()
        self.interface.error_signal.emit(str(title), str(err))

        del title
        del err
        del datagram

    def initiateHandshake(self):
        """Initiate handshake"""
        datagram = Datagram()
        datagram.setCommand(constants.CMD_REQ_CONNECTION)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(self.getKey())
        self.sendDatagram(datagram)
        self.notify.debug('sent public key')

        self.generateSecret(self.getResp().getData())
        self.notify.debug('received public key')

        self.notify.info('secured socket connection')
        self.setSecure(True)

    def initiateLogin(self, name, callback):
        hmac = self.generateHmac(name.encode(), constants.HMAC_KEY, True)

        # login
        datagram = Datagram()
        datagram.setCommand(constants.CMD_REQ_LOGIN)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData([name, 'temp'])
        datagram.setHMAC(hmac)
        self.sendDatagram(datagram)

        # credentials
        resp = self.getResp()
        if resp.getData() is True: # login success
            self.setName(name)
            self.notify.debug('credentials validated')
        else:
            callback('failed to login; bad credentials')
            return

        # challenge
        M = self.initiateChallenge(name) # needed for verification
        if M is False:
            self.notify.warning('AuthenticationError',
                                'suspicious challenge failure')
            callback('challenge failed')
            return
        else:
            self.notify.debug('challenge success')

        # verification
        if self.initiateChallengeVerification(M):
            self.notify.info('logged in as {0}'.format(name, self.getId()))
            callback('') # start chatting

    def initiateChallenge(self, name):
        self.user = srp.User(name.encode(), constants.HMAC_KEY)
        uname, A = self.user.start_authentication()

        datagram = Datagram()
        datagram.setCommand(constants.CMD_REQ_CHALLENGE)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(A.hex())

        self.notify.debug('challenging')
        self.sendDatagram(datagram)

        resp = self.getResp().getData()
        if resp is False:
            return False
        else:
            s, B = map(bytes.fromhex, resp)
            M = self.user.process_challenge(s, B)
            if M is None:
                self.sendNo()
                return False
            else:
                return M

    def initiateChallengeVerification(self, M):
        datagram = Datagram()
        datagram.setCommand(constants.CMD_REQ_CHALLENGE_VERIFY)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(M.hex())

        self.notify.debug('verifying')
        self.sendDatagram(datagram)

        resp = self.getResp()
        HAMK = bytes.fromhex(resp.getData())
        self.user.verify_session(HAMK)

        del M
        del HAMK

        if self.user.authenticated():
            self.setId(uuid.UUID(resp.getRecipient()))
            self.notify.debug('challenge verified')
            return True
        else:
            self.notify.critical('suspiciously challenge failure')
            return False

    def initiateHelo(self, tab, member_names):
        member_names = [self.getName()] + member_names

        datagram = Datagram()
        datagram.setCommand(constants.CMD_HELO)
        datagram.setSender(self.getId())
        datagram.setRecipient(self.getId())
        datagram.setData(member_names)

        self.notify.debug('requesting new zone')
        self.sendDatagram(datagram)

        self.zm.addTab(tab, tuple(member_names))

        del tab
        del member_names
        del datagram

    def doHelo(self, datagram):
        zone_id, key, member_ids, member_names = datagram.getData()
        if not self.zm.getZoneById(zone_id, search=True):
            if member_names[0] != self.getName():
                window = self.interface.getWindow()
                window.new_client_signal.emit(str(zone_id),
                                              str(key),
                                              member_ids,
                                              member_names)
            else:
                tab = self.zm.getTabByMembers(tuple(member_names))
                if tab:
                    zone = Zone(tab, zone_id, key, member_ids)
                    self.enter(tab, zone)
                    zone.sendRedy()
                else:
                    self.notify.error('ZoneError', 'could not find tab')

                del tab
                del zone

        del zone_id
        del key
        del member_ids
        del member_names
        del datagram

    def forwardZoneDatagram(self, datagram):
        if datagram.getSender() in self.zm.getZoneIds():
            zone = self.zm.getZoneById(datagram.getSender())
            zone.receiveDatagram(datagram)
            del zone
        else:
            self.notify.warning('received suspicious zone datagram')

        del datagram
