import argparse
import datetime
import os
import sys
import builtins

from src.base import constants

class Launcher(object):

    def __init__(self):
        info = self.getLaunchInfo()
        if info.server:
            self.type = 'ai'
        else:
            self.type = 'client'

        self.__startLogging()

        if __debug__ and constants.WANT_INJECTOR:
            self.__launchInjector()

        if info.server:
            self.__launchAIServer(info.address, info.port)
        else:
            self.__launchClient(info.address, info.port)

    def getLogFilePath(self):
        if not os.path.exists(constants.LOG_PATH):
            os.mkdir(constants.LOG_PATH)

        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = '{0}/{1} {2}.{3}.log'.format(constants.LOG_PATH, constants.APP_TITLE, now, self.type)
        return path

    def getLaunchInfo(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--server',
                            dest='server',
                            action='store_true',
                            default=False,
                            help='launch server')
        parser.add_argument('-a', '--address',
                            dest='address',
                            type=str,
                            nargs='?',
                            default=constants.DEFAULT_ADDRESS,
                            help='server address')
        parser.add_argument('-p', '--port',
                            dest='port',
                            type=int,
                            nargs='?',
                            default=constants.DEFAULT_PORT,
                            help='server port')
        args = parser.parse_args()
        return args

    def __startLogging(self):
        if __debug__:
            self.setConfig(level=constants.DEBUG)
        else:
            self.setConfig(filename=self.getLogFilePath())

    def __launchAIServer(self, address, port):
        from src.ai.Server import Server
        from src.ai.Console import Console

        server = Server(address, port)
        console = Console(server.cm, server.bm)

        builtins.ai = server # Make the Server a builtin class

        console.start()
        server.start()

    def __launchClient(self, address, port):
        from src.gui.ClientUI import ClientUI

        client = ClientUI(address, port)

        builtins.client = client # Make the Client a builtin class

        client.start()

    def setConfig(self, stream=None, filename=None, level=constants.INFO):
        constants.LOG_CONFIG = (stream, filename, level)

    if __debug__:
        def __launchInjector(self):
            import threading

            def runInjectorCode():
                global text
                exec(text.get(1.0, 'end'), globals(), globals())

            def openInjector():
                import tkinter

                tk = tkinter.Tk()
                tk.geometry('600x400')
                tk.title('Python Injector')
                tk.resizable(False, False)

                frame = tkinter.Frame(tk)

                global text
                text = tkinter.Text(frame, width=70, height=20)
                text.pack(side='left')

                tkinter.Button(tk, text='Inject', command=runInjectorCode).pack()

                scrollbar = tkinter.Scrollbar(frame)
                scrollbar.pack(fill='y', side='right')
                scrollbar.config(command=text.yview)

                text.config(yscrollcommand=scrollbar.set)

                frame.pack(fill='y')

                tk.mainloop()

            threading.Thread(target=openInjector).start()

if __name__ == '__main__':
    Launcher()