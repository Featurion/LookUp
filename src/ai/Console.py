import os
import signal
import sys
import threading

from src.base.Datagram import Datagram
from src.base import constants

class Console(threading.Thread):

    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server

        self.commands = {
            'list': {
                'callback': self.list,
                'help': 'list\t\tlist active connections'
            },
            'execute': {
                'callback': self.execute,
                'help': 'execute [code]\t\texecute arbitrary Python code (only if debug)'
            },
            'datagram': {
                'callback': self.datagram,
                'help': 'datagram [identifier], [command], [type], [data]\t\tsend a datagram (only if debug)'
            },
            'zombies': {
                'callback': self.zombies,
                'help': 'zombies\t\tlist zombie connections'
            },
            'kick': {
                'callback': self.kick,
                'help': 'kick [identifier] [reason]\tkick the given user from the server'
            },
            'ban': {
                'callback': self.ban,
                'help': 'ban [identifier] [reason]\tban the given user from the server'
            },
            'kill': {
                'callback': self.kill,
                'help': 'kill [ip] [reason]\tkill the zombie with the given IP'
            },
            'stop': {
                'callback': self.stop,
                'help': 'stop\t\tstop the server'
            },
            'help': {
                'callback': self.help,
                'help': 'help\t\tdisplay this message'
            },
        }

    def run(self):
        while True:
            try:
                command_input = sys.stdin.readline().split()
                if len(command_input) > 0:
                    cmd = self.commands[command_input[0]]['callback']
                    if len(command_input) == 2:
                        cmd(command_input[1])
                    elif len(command_input) > 2 and command_input[0] == 'execute':
                        cmd(command_input[1:])
                    elif len(command_input) > 1 and command_input[0] == 'kick':
                        cmd(command_input[1], command_input[2:])
                    elif len(command_input) > 1 and command_input[0] == 'ban':
                        cmd(command_input[1], command_input[2:])
                    elif len(command_input) > 1 and command_input[0] == 'kill':
                        cmd(command_input[1], command_input[2:])
                    elif len(command_input) == 5 and command_input[0] == 'datagram':
                        name = command_input[1]
                        command = command_input[2]
                        type_ = command_input[3]
                        data = command_input[4]
                        cmd(name, command, type_, data)
                    else:
                        cmd(None)
                else:
                    pass
            except EOFError:
                self.stop()
            except KeyError:
                print("Unrecognized command")
            except TypeError as e:
                print("Bad args")

    def execute(self, code):
        if not code:
            print("Execute command requires code")
        else:
            if __debug__:
                try:
                    exp = ''
                    if isinstance(code, list):
                        for length in code:
                            exp += length + ' '
                    else:
                        exp = code
                    exec(exp, globals(), globals()) # This allows you to execute anything as if it was a line of code in this class, as well as add it to globals()
                except Exception as e:
                    print(str(e))
            else:
                print("This command is too dangerous to use unless for debugging!")

    def datagram(self, identifier, command, type_, data):
        if not identifier or not command or not type_ or not data:
            print("Datagram command requires identifier, command, and data")
        else:
            if __debug__:
                try:
                    ai = self.server.cm.getClient(identifier)
                    if ai:
                        # TODO: List, tuple, and float support
                        if type_ == 'str':
                            data = str(data)
                        elif type_ == 'int':
                            data = int(data)
                        else:
                            print("Invalid data type.")
                            return
                        datagram = Datagram()
                        datagram.setCommand(int(command))
                        datagram.setData(data)
                        datagram.setSender(constants.SYSTEM)
                        datagram.setRecipient(ai.getId())

                        ai.sendDatagram(datagram)

                        print("Sent datagram", datagram.toJSON())
                    else:
                        print("Client {0} does not exist!".format(identifier))
                except Exception as e:
                    print(str(e))
            else:
                print("This command is too dangerous to use unless for debugging!")

    def list(self, arg):
        print("Registered users\n" + "=" * 16)
        for ai in self.server.cm.getClients():
            print(str(ai.getName()) + '-' + str(ai.getId()) + '-' + str(ai.getAddress()) + ':' + str(ai.getPort()))

    def zombies(self, arg):
        print("Zombie Connections\n" + "=" * 18)
        for ai in self.server.cm.getClients():
            if ai.getName() is None:
                print(str(ai.getAddress()))
            else:
                pass

    def kick(self, identifier, reason):
        if not identifier or not reason:
            print("Kick command requires identifier and reason")
        else:
            exp = ''
            if isinstance(reason, list):
                for length in reason:
                    exp += length + ' '
                exp = exp[:-1]
            kick = self.server.bm.kick(identifier, exp)
            if kick:
                print("{0} kicked from server".format(identifier))
            else:
                print("{0} is not a registered client".format(identifier))

    def ban(self, identifier, reason):
        if not identifier or not reason:
            print("Ban command requires an identifier and reason")
        else:
            exp = ''
            if isinstance(reason, list):
                for length in reason:
                    exp += length + ' '
                exp = exp[:-1]
            kick = self.server.bm.ban(identifier, exp)
            if kick:
                print("{0} banned from server".format(identifier))
            else:
                print("{0} is not a registered client".format(identifier))

    def kill(self, ip, reason):
        if not ip or not reason:
            print("Kill command requires an IP and reason")
        else:
            exp = ''
            if isinstance(reason, list):
                for length in reason:
                    exp += length + ' '
                exp = exp[:-1]
            try:
                kill = self.server.bm.kill(ip, exp)
                if kill:
                    print("{0} killed".format(ip))
                else:
                    print("{0} has no registered clients".format(ip))
            except KeyError:
                print("{0} is not a zombie".format(ip))

    def stop(self, arg=None):
        os.kill(os.getpid(), signal.SIGINT)

    def help(self, arg):
        help_messages = [cmd[1]['help'] for cmd in iter(self.commands.items())]
        print("Available commands:\n\t{0}".format('\n\t'.join(help_messages)))
