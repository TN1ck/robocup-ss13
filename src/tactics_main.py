#/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from world import Vector
from random import shuffle
from perception import Perception

def base(x):
  return 1/x

def find_maxima(l):
  maximum = -float("inf")
  maxima = []
  for tup in l:
    if tup[1] >= maximum:
      maximum = tup[1]
  for tup in l:
    if tup[1] >= maximum:
      maxima.append(tup)
  return maxima



# Utility functions

def enemy_owns_ball():
  return False

def player_owns_ball(player):
  return False



# Tactical functions

def run_to_ball(x):
  return 0.5 * base(x)

def run_to_own_goal(x):
  return 0.5 * base(x)

def run_to_enemy_goal(x):
  return 0.5 * base(x)

def stay():
  return 0.1

def run_to_friend(x):
  return 0
  # return 0.5 * base(x)

def run_away_from_friend(x):
  return 0
  # return 0.5 * base(x)

def run_away_from_l1():
  return 0.5

def run_away_from_r2():
  return 0.5

class TacticsMain:

  def __init__(self, world, movement):
    self.world = world
    self.mov = movement

  def run_tactics(self):

    ____ = self.world.lines
    _P__ = self.world.flags
    _TT_ = self.world.goal_poles
    _R__ = self.world.players
    _o__ = self.world.ball

    me = _R__[0]



    all_arguments = [
      5,    # run_to_ball,
      5,    # run_to_own_goal,
      5,    # run_to_enemy_goal,
      None, # stay,
      0,    # run_to_friend,
      0,    # run_away_from_friend
      None, # run_away_from_l1,
      None, # run_away_from_r2,
    ]
    all_functions = [
      run_to_ball,
      run_to_own_goal,
      run_to_enemy_goal,
      stay,
      run_to_friend,
      run_away_from_friend,
      run_away_from_l1,
      run_away_from_r2,
    ]

    all_results = []

    for i in range(len(all_functions)):
      if all_arguments[i]:
        all_results.append((all_functions[i].__name__, all_functions[i](all_arguments[i])))
      else:
        all_results.append((all_functions[i].__name__, all_functions[i]))

    maxima = find_maxima(all_results)

    shuffle(maxima)

    actual_tuple = maxima[0]




