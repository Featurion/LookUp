from src.zones.ZoneBase import ZoneBase


class ZoneAI(ZoneBase):

    def __init__(self, zone_manager, id_, member_ids):
        ZoneBase.__init__(self, id_, member_ids)
        self.zone_manager = zone_manager
