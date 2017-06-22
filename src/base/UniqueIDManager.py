import base64
import os
import uuid
from src.base.Notifier import Notifier

class UniqueIDManager(Notifier):
    """Base class for managers using unique identifiers"""

    SCOPES = {
        'default': uuid.UUID('a8c52ed81a0e4d8bbda2801a55553d12'),
    } # update in subclass

    def __init__(self):
        Notifier.__init__(self)
        self.id2owner = {}
        self.scope_map = {scope: {} for scope in self.SCOPES.keys()}

    def allocateId(self, mode, name, id_=None, owner=None):
        """Register a new ID"""
        if self.id2owner.get(id_):
            return self.generateId(mode, name)
        elif mode in self.scope_map:
            self.id2owner.setdefault(id_, owner)
            self.scope_map.get(mode).setdefault(id_, owner)
        else:
            self.notify.error('IDError', 'id not allocated')

    def deallocateId(self, id_, mode):
        if self.id2owner.get(id_) and self.scope_map.get(mode):
            self.id2owner.pop(id_)
            self.scope_map.get(mode).pop(id_)
        else:
            self.notify.debug('ID {0} is not in use!'.format(id_))

    def generateId(self, mode=None, seed=None):
        """Return a random or seeded 128-bit integer"""
        scope = self.SCOPES.get(mode)

        if scope is None and seed is None:
            self.notify.debug('generating random ID...')
            scope = self.SCOPES['default']
            seed = base64.b64encode(os.urandom(32)).decode('utf-8')
            id_ = uuid.uuid5(scope, seed)
            return id_
        elif scope is None and seed is not None:
            self.notify.error('ValueError', 'scope and seed are mutually exclusive args')
        elif scope is not None and seed is None:
            self.notify.error('ValueError', 'scope and seed are mutually exclusive args')
        elif not isinstance(scope, uuid.UUID):
            self.notify.error('ValueError', 'scope argument expects a UUID object')
        elif scope not in self.SCOPES.values():
            self.notify.error('ValueError', 'received invalid scope')
        elif not isinstance(seed, str):
            self.notify.error('ValueError', 'seed argument expects a string')
        else:
            self.notify.debug('generating seeded id')
            id_ = uuid.uuid5(scope, seed)
            return id_

        self.notify.critical('suspicious ID generation attempt')
        return None
