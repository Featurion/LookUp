class ZoneBase(object):

    def __init__(self, id_, member_ids):
        self.__id = id_
        self.__members = list(member_ids)

    def getId(self):
        return self.__id

    def getMembers(self):
        return self.__members

    def add(self, id_):
        if id_ not in self.getMembers():
            self.__members.append(id_)

    def remove(self, id_):
        if id_ in self.getMembers():
            self.__members.remove(id_)
