from src.base.Notifier import Notifier


class ZoneBase(Notifier):

    def __init__(self, id_, members):
        Notifier.__init__(self)
        self.__id = id_
        self.__members = members

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members
