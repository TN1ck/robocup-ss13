# -*- coding: utf-8 -*-
import numpy
import world
import logging

WEIGHTING_FACTOR = 0.6
HISTORIES_TO_USE = 5

class Interpol:

    def smooth_mobile_entity_positions(self):
        mes = self.world.mobile_entities()          # fetch mobile entities from current world
        for me in mes:                              # iterate through mobile entities
            #logging.debug('[' + me.get_identifier() + '] pos raw:    ' + str(me.get_position()))
            pos = world.Vector(0.0, 0.0)
            for i in xrange(1, HISTORIES_TO_USE):   # iterate through world history
                if len(self.world_history_raw) >= i:
                    # get mobile entity's history instance:
                    if self.world_history_raw[-i].entity_from_identifier.has_key(me.get_identifier()):
                        meh = self.world_history_raw[-i].entity_from_identifier[me.get_identifier()]
                        #logging.debug('meh pos: ' + str(meh.get_position()))
                        pos.x += (meh.get_position().x * self.weights[i - 1])
                        pos.y += (meh.get_position().y * self.weights[i - 1])
                        #logging.debug(str(self.weights[i - 1]))
                        #logging.debug(str(pos))
                    else:
                        break                   # world history instance exists, but w/o the mobile entity
                else:
                    break                       # no more world history yet (agent just started)
            if i > 1:                           # if there are values to sum up
                pos.x /= sum(self.weights[:i])
                pos.y /= sum(self.weights[:i])
                #logging.debug('[' + me.get_identifier() + '] smoothed over ' + str(i - 1) + ' history instances.')
            else:
                #logging.debug('couldn\'t smooth')
                pass
            me.set_position(pos.x, pos.y)
            #logging.debug('[' + me.get_identifier() + '] pos smooth: ' + str(me.get_position()))

    def __init__(self, player_nr, world, world_history, world_history_raw):
        self.player_nr = player_nr
        self.world = world
        self.world_history = world_history
        self.world_history_raw = world_history_raw
        # init weights:
        self.weights = []
        for i in xrange(0, HISTORIES_TO_USE):
            self.weights.append(WEIGHTING_FACTOR ** i)
