from src.userbase.NodeAI import NodeAI


class ClientAI(NodeAI):

    def getName(self):
        """Getter for name"""
        return self.__name

    def setName(self, name):
        """Setter for name"""
        if self.__name is None:
            self.__name = name

    def getMode(self):
        """Getter for mode"""
        return self.__mode

    def setMode(self, mode):
        """Setter for mode"""
        if self.__mode is None:
            self.__mode = mode
