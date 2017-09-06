import asyncio
import base64
import pyarchy
import socket
import srp

from . import constants, utils
from .constants import ERROR_INFO_MAP
from .core import ClientBase, Datagram


class Client(ClientBase):

    def __init__(self,
                 host : str = None, port : int = None,
                 socket_ : socket.socket = None,
                 hmac_key : bytes = None, challenge_key : bytes = None):
        if host and port:
            self._address = (host, port)
            self._socket = None
        elif socket_:
            self._address = socket_.getsockname()
            self._socket = socket_
        else:
            raise TypeError('must supply either address or socket')

        loop = asyncio.get_event_loop()
        streams = loop.run_until_complete(self.make_streams(loop))
        ClientBase.__init__(self, *streams, hmac_key, challenge_key)

    async def make_streams(self, loop):
        if self._socket:
            pass
        elif self._address:
            # Make the socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect(self._address)
        else:
            raise AttributeError('no socket or address specified')

        return await asyncio.open_connection(
            loop = loop,
            sock = self._socket)

    async def send_login(self, name):
        # Intital login request
        hmac = self.generate_HMAC(name.encode(), self._hmac_key)
        await self.send(
            Datagram(
                command = constants.CMD_LOGIN,
                sender = self.id,
                recipient = self.id,
                data = name,
                hmac = base64.b85encode(hmac).decode()))
        response = await self.recv()

        if not response or response.data is not True:
            await self.do_error(constants.ERR_CREDENTIALS)
            return

        # Challenge
        user = srp.User(name.encode(), self._challenge_key)
        username, auth = user.start_authentication()

        await self.send_response(auth.hex())
        response = await self.recv()

        if response and response.data:
            s, B = map(bytes.fromhex, response.data)
            M = user.process_challenge(s, B)

            if M is None:
                await self.do_error(constants.ERR_CHALLENGE)
                return
            else:
                await self.send_response(M.hex())

        # Verification
        response = await self.recv()

        if response and response.data:
            HAMK = bytes.fromhex(response.data)
            user.verify_session(HAMK)

            # Generate new hash based off of the session key
            self.counter_cipher = user.get_session_key()

            if user.authenticated():
                self.name = name
                self.id = pyarchy.core.Identity(response.recipient)
        else:
            await self.do_error(constants.ERR_VERIFICATION)


__all__ = [
    Client,
]
