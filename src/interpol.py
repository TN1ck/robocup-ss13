# -*- coding: utf-8 -*-
import numpy
import world
import logging

WEIGHTING_FACTOR = 0.7
HISTORIES_TO_USE = 15

class Interpol:

    def smooth_mobile_entity_positions(self):
        '''Smoothment takes HISTORIES_TO_USE past world_history_raw instances and weights them
        WEIGHTING_FACTOR^i, so the most current ones are weighted heavier then the older ones.
        After that, the smooth position tends to lag behind the real position (because older
        positions used for smoothing.)
        Therefor a movement prediction is calculated as a linear fit from the two most current
        smooth positions and added to the final position.'''

        # me  -> mobile entity
        # mes -> mobile entities
        # meh -> mobile entity history instance
        processed = []
        mes = self.world.mobile_entities()          # fetch mobile entities from current world
        for me in mes:                              # iterate through mobile entities
            processed.append(me.get_identifier())
            #logging.debug('[' + me.get_identifier() + '] pos raw:    ' + str(me.get_position()))
            pos = world.Vector(0.0, 0.0)
            for i in xrange(1, HISTORIES_TO_USE):   # iterate backwards through world history
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
                        break                       # world history instance exists, but w/o the mobile entity
                else:
                    break                           # no more world history yet (agent just started)
            # end iterating through world history
            weight_sum = sum(self.weights[:i])
            pos.x /= weight_sum
            pos.y /= weight_sum
            # POSITION PREDICTION
            if self.prev_me_pos.has_key(me.get_identifier()):
                # there is a smoothed position w/o pos prediction from the previous cycle
                prev_me_pos = self.prev_me_pos[me.get_identifier()]
                self.prev_me_pos[me.get_identifier()] = world.Vector(pos.x, pos.y)
                direction = pos - prev_me_pos
                # here the movement / position prediction is added
                # COMMENT THIS LINE OUT TO DEACTIVATE MOVEMENT PREDICTION:
                #pos += direction * weight_sum
            else:
                # there is no value from the previous cycle
                # just store the current one:
                self.prev_me_pos[me.get_identifier()] = world.Vector(pos.x, pos.y)
            #logging.debug('[' + me.get_identifier() + '] smoothed over ' + str(i - 1) + ' history instances.')
            me.set_position(pos.x, pos.y)
            #logging.debug('[' + me.get_identifier() + '] pos smooth: ' + str(me.get_position()))
        # end iterating through mobile entities

        # finally, remove all prev smooth me pos values, which were not processed this time:
        # (so they won't be used next time accidentally, could have strange effects...)
        for identifier, position in self.prev_me_pos.items():
            if not identifier in processed:
                del prev_me_pos[identifier]

    def __init__(self, player_nr, world, world_history, world_history_raw):
        self.player_nr = player_nr
        self.world = world
        self.world_history = world_history
        self.world_history_raw = world_history_raw
        # init weights:
        self.weights = []
        for i in xrange(0, HISTORIES_TO_USE):
            self.weights.append(WEIGHTING_FACTOR ** i)
        # dictionary storing previous smooth me positions w/o pos prediction:
        self.prev_me_pos = {}
