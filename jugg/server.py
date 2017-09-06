import asyncio
import pyarchy
import socket
import srp

from . import constants, utils
from .core import ClientBase, Datagram
from .security import KeyHandler


class ClientAI(ClientBase):

    def __init__(self,
                 stream_in, stream_out,
                 hmac_key : bytes, challenge_key : bytes):
        ClientBase.__init__(
            self,
            stream_in, stream_out,
            hmac_key, challenge_key)

        self._commands[constants.CMD_LOGIN] = self.handle_login
        
    def verify_credentials(self, data):
        return utils.validate_name(data)

    async def handle_login(self, dg : Datagram):
        # Initial login request
        if not self.verify_credentials(dg.data):
            await self.send_error(constants.ERR_CREDENTIALS)
            return

        if not isinstance(dg.data, str) or \
           not self.verify_HMAC(
               dg.hmac.encode(),
               dg.data.encode(),
               self._hmac_key):
            await self.send_error(constants.ERR_HMAC)
            return
        else:
            await self.send_response(True)

        # Challenge
        response = await self.recv()

        if response and response.data:
            svr = srp.Verifier(
                dg.data.encode(),
                *srp.create_salted_verification_key(
                    dg.data.encode(), self._challenge_key),
                bytes.fromhex(response.data))
        else:
            return

        s, B = svr.get_challenge()
        if (s is None) or (B is None):
            await self.send_error(constants.ERR_CHALLENGE)
            return
        else:
            await self.send_response([s.hex(), B.hex()])

        # Verification
        response = await self.recv()

        if response and response.data:
            HAMK = svr.verify_session(bytes.fromhex(response.data))
            if HAMK and svr.authenticated():
                self.name = dg.data
                self.id = pyarchy.core.Identity()
                await self.send_response(HAMK.hex())
            else:
                await self.send_error(constants.ERR_VERIFICATION)


class Server(object):

    client_handler = ClientAI

    def __init__(self,
                 host : str = None, port : int = None,
                 socket_ : socket.socket = None,
                 hmac_key : bytes = None, challenge_key : bytes = None):
        KeyHandler.__init__(self)

        if host and port:
            self._address = (host, port)
            self._socket = None
        elif socket_:
            self._address = socket_.getsockname()
            self._socket = socket_
        else:
            raise TypeError('must supply either address or socket')

        self._hmac_key = hmac_key or  b''
        self._challenge_key = challenge_key or b''

    async def new_connection(self, stream_in, stream_out):
        try:
            # Create the client on the server
            client = self.client_handler(
                stream_in, stream_out,
                self._hmac_key, self._challenge_key)
            self.clients.add(client)
            # Maintain the connection
            await client.start()
            # Connection broke; remove the client from the server
            self.clients.remove(client)
        except asyncio.CancelledError:
            return

    def start(self):
        if self._socket:
            pass
        elif self._address:
            # Make the socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind(self._address)
        else:
            raise AttributeError('no socket or address specified')

        # Establish the conncetion
        loop = asyncio.get_event_loop()
        server_coro = loop.create_server(
            # Stream factory
            lambda: asyncio.StreamReaderProtocol(
                asyncio.StreamReader(loop = loop),
                self.new_connection,
                loop),
            sock = self._socket)

        # Make the client pool
        self.clients = pyarchy.data.ItemPool()
        self.clients.object_type = ClientBase
        
        self.run(loop, server_coro)

    def run(self, event_loop, start_coro):
        # Maintain the connection
        utils.reactive_event_loop(
            event_loop,
            start_coro, self.stop(),
            run_forever = True)

    async def stop(self):
        # Cleanup
        pass


__all__ = [
    ClientAI,
    Server,
]
