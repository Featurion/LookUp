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
        self.scope_map = {scope: {} for scope in self.SCOPES.values()}

    def allocateId(self, mode, name, id_=None, owner=None):
        """Register a new ID"""
        if id_ in self.id2owner:
            return self.generateId(mode, name)
        else:
            self.id2owner[id_] = owner
            self.scope_map[mode][id_] = owner

    def deallocateId(self, id_, mode):
        if id_ in self.id2owner:
            del self.id2owner[id_]
            del self.scope_map[mode][id_]
        else:
            # log: '{id} not in use'
            pass

    def generateId(self, scope=None, seed=None):
        """Return a random or seeded 128-bit integer"""
        if scope is None and seed is None:
            # log: 'generating random id'
            scope = self.SCOPES['default']
            seed = base64.b64encode(os.urandom(32)).decode('utf-8')
            id_ = int(uuid.uuid5(scope, seed))
            return (scope, seed, id_)
        elif scope is None and seed is not None:
            # err: ValueError('scope and seed are mutually exclusive args')
            pass
        elif scope is not None and seed is None:
            # err: ValueError('scope and seed are mutually exclusive args')
            pass
        elif not isinstance(scope, uuid.UUID):
            # err: ValueError('scope argument expects a UUID object')
            pass
        elif scope not in self.SCOPES.values():
            # err: ValueError('received invalid scope')
            pass
        elif not isinstance(seed, str):
            # err: ValueError('seed argument expects a string')
            pass
        else:
            # log: 'generating seeded id'
            id_ = int(uuid.uuid5(scope, seed))
            return (scope, seed, id_)

        # log: 'suspicious id generation attempt'
        return None
