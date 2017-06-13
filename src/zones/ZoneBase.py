from src.base.Notifier import Notifier


class ZoneBase(Notifier):

    def __init__(self, id_, member_ids):
        Notifier.__init__(self)
        self.__id = id_
        self.__members = set(member_ids)

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members

    def remove(self, id_):
        if id_ in self.getMembers():
            self.__members.remove(id_)
