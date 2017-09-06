import asyncio
import json
import pyarchy
import socket
import struct

from concurrent.futures import TimeoutError

from . import constants, security


class Datagram(object):

    @classmethod
    def from_string(cls, str_ : str):
        return cls(**json.loads(str_))

    def __init__(self,
                 command : int = None,
                 sender : str = None, recipient : str = None,
                 data : str = None, hmac : str = None):
        object.__init__(self)

        self.__command = command
        self.__sender = sender
        self.__recipient = recipient
        self.__data = data
        self.__hmac = hmac

    def __str__(self):
        return json.dumps({
            'command': self.command,
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data,
            'hmac': self.hmac,
        })

    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self, command):
        self.__command = command

    @property
    def sender(self) -> str:
        return self.__sender

    @property
    def recipient(self) -> str:
        return self.__recipient

    @recipient.setter
    def recipient(self, recipient : str):
        self.__recipient = str(recipient)

    @property
    def route(self):
        return (self.sender, self.recipient)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        if isinstance(data, bytes):
            self.__data = data.decode()
        else:
            self.__data = data

    @property
    def hmac(self):
        return self.__hmac


class Node(security.KeyHandler):

    def __init__(self, stream_in, stream_out):
        security.KeyHandler.__init__(self)

        self.__in = stream_in
        self.__out = stream_out

        self._commands = {
            constants.CMD_ERR: self.handle_error,
        }

    async def recv(self, n_bytes : int = None):
        try:
            data = await asyncio.wait_for(
                # Read size if not provided
                self.__in.read(n_bytes if n_bytes else socket.ntohl(
                    struct.unpack(
                        'I',
                        # Size indicator
                        await asyncio.wait_for(
                            self.__in.read(4),
                            timeout = 4)
                        )[0]
                    )),
                timeout = 1)

            if data:
                return self.decrypt(data)
            else:
                return None
        except TimeoutError:
            return ''
        except struct.error:
            return None

    async def send(self, dg : Datagram):
        data = self.encrypt(dg)
        self.__out.write(struct.pack('I', socket.htonl(len(data))) + data)
        await self.__out.drain()

    async def close(self):
        self.__out.close()

    async def start(self):
        await self.do_handshake()
        if self.counter_key:
            await self.run()
        else:
            await self.stop()

    async def do_handshake(self):
        await self.send(str(self.key))
        self.counter_key = int(await self.recv() or '0')

    async def run(self):
        # Maintain the connection
        while True:
            dg = await self.recv()
            if dg is None:
                #  Connection broke
                break
            elif dg:
                await self.handle_datagram(dg)
            else:
                # Still connected; nothing to do
                continue

        # Cleanup
        await self.stop()

    async def stop(self):
        await self.close()

    async def send_error(self, errno : int):
        await self.send(
            Datagram(
                command = constants.CMD_ERR,
                sender = self.id,
                recipient = self.id,
                data = errno))

    # Add functionality in subclass
    async def do_error(self, errno):
        print('err({0}):'.format(errno), constants.ERROR_INFO_MAP.get(errno))

    async def handle_error(self, dg : Datagram):
        await self.do_error(dg.data)

    async def handle_datagram(self, dg: Datagram):
        func = self._commands.get(dg.command)
        if func:
            await func(dg)
        else:
            await self.stop()


class ClientBase(Node, pyarchy.common.ClassicObject):

    def __init__(self, stream_in, stream_out, hmac_key, challenge_key):
        Node.__init__(self, stream_in, stream_out)
        pyarchy.common.ClassicObject.__init__(self, '', rand_id = False)

        self._hmac_key = hmac_key or  b''
        self._challenge_key = challenge_key or b''

        self._name = None

    def __lt__(self, obj):
        if isinstance(obj, pyarchy.core.NamedObject):
            return self.name < obj.name
        else:
            return NotImplemented

    def __gt__(self):
        if isinstance(obj, pyarchy.core.NamedObject):
            return self.name > obj.name
        else:
            return NotImplemented

    @property
    def name(self) -> str:
        return str(self._name)

    @name.setter
    def name(self, name : str):
        if self._name is None:
            self._name = str(name)
        else:
            raise AttributeError('name can only be set once')

    async def send_response(self, data):
        await self.send(
            Datagram(
                command = constants.CMD_RESP,
                sender = self.id,
                recipient = self.id,
                data = data))


__all__ = [
    Datagram,
    Node,
    ClientBase,
]
