# -*- coding: utf-8 -*-
import numpy
import world

class Interpol:

    def smooth_mobile_entity_positions(self):
        pass

    def __init__(self, player_nr, world, world_history, world_history_raw):
        self.player_nr = player_nr
        self.world = world
        self.world_history = world_history
        self.world_history_raw = world_history_raw
