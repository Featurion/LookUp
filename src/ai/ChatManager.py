class ChatManagerAI(IDManager):
    """Manage chat messages"""

    def allocateId(self, scope_name, node_name):
        pass

    def emitMessage(self, message):
        """Send message to all clients"""
        return NotImplemented

    def emitMessageInsideZone(self, message, zone):
        """Send message to all clients with interest in zone"""
        return NotImplemented

    def emitMessageOutsideZone(self, message, zone):
        """Send message to all clients without interest in zone"""
        return NotImplemented
