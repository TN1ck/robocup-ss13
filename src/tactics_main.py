# /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import world
from world import Vector
from random import shuffle
from logging import *
import math



class TacticsMain:

  def __init__(self, world, movement, nao):
    self.world = world
    self.mov = movement

    self.nao = nao

    self.my_position = None

    self.field_lines_idfs   = ["L1","L2","LL","LR","LM"]       #Field lines
    # self.right_penalty_idfs = ["LG1R","LG2R","LGR"]            #right penalty area
    # self.left_penalty_ifds  = ["LG1L","LG2L","LGL"]            #left penalty area
    self.right_goal_ifds    = ["G1R","G2R"]                    #right goal
    self.left_goal_idfs     = ["G1L","G2R"]                    #left goal
    self.player_t1_idfs     = ["P_1_0","P_1_1","P_1_2","P_1_3","P_1_4","P_1_5"]  #team 1
    self.player_t2_idfs     = ["P_1_0","P_1_1","P_1_2","P_1_3","P_1_4","P_1_5"]#team 2

    self.distance_team1 = {}
    self.distance_team2 = {}
    self.distance_goal_poles_right = {}
    self.distance_goal_poles_left = {}
    self.distance_lines = {}
    self.distance_ball = -1




  def set_own_position(self):
      self.my_position = self.nao.get_position()

  """Calculate distances too all objects on the field  except the Flags and save them in the corresponding list."""
  def get_distances(self):
      for i in range(len(self.player_t1_idfs)):
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t1_idfs[i]), self.my_position)
          self.distance_team1[self.player_t1_idfs[i]] = val
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t2_idfs[i]), self.my_position)
          self.distance_team2[self.player_t2_idfs[i]] = val

      calculate_goal_distances(self.my_position)
      self.distance_lines = self.calc_line_distance(self.my_position)
      self.distance_ball = self.calc_point_distance(self.world.get_entity_position('B'), self.my_position)

  def calculate_goal_distances(self, my_position):
      val = self.calc_point_distance(self.world.get_entity_position(self.left_goal_idfs[0]), my_position)
      val = (val + self.calc_point_distance(self.world.get_entity_position(self.left_goal_idfs[1]), my_position))/2
      self.distance_goal_left[self.left_goal_idfs] = val

      val = self.calc_point_distance(self.world.get_entity_position(self.right_goal_idfs[0]), self.my_position)
      val = (val + self.calc_point_distance(self.world.get_entity_position(self.right_goal_idfs[1]), my_position))/2
      self.distance_goal_left[self.right_goal_idfs] = val

  def clear_distances(self):
      self.distance_goal_left = {}
      self.distance_goal_right= {}
      self.distance_lines = {}
      self.distance_team1= {}
      self.distance_team2 ={}
      self.distance_ball = None

  """ Some field object position are specified by a point. This method calcs the distance to them """
  def calc_point_distance(self,x1,x2):
     return math.sqrt(math.pow((x1.x - x2.x),2) + math.pow((x1.y - x2.y),2))

  def calc_line_distance(self,x1):
      list = {}
      list[self.field_lines_idfs[0]] = (10 - x1.y)
      list[self.field_lines_idfs[1]] = ((-1) * (-10 - x1.y))
      list[self.field_lines_idfs[2]] = ((-1) * (-15 - x1.x))
      list[self.field_lines_idfs[3]] = (15 - x1.x)
      if x1.x < 0:
        list[self.field_lines_idfs[4]] = (-x1.x)
      else:
        list[self.field_lines_idfs[4]] = (x1.x)
      return list

  def find_maxima(self, l):
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
  def enemy_owns_ball(self):
    for i in self.world.players:
      if i.team != our_team:
        distance = calc_point_distance(self.world.get_entity_position(i.get_identifier), self.world.get_entity_position('B'))
        if distance <= 1:
          return True
    return False

  def we_own_ball(self):
    for i in self.world.players:
      if i.team == our_team:
        distance = calc_point_distance(self.world.get_entity_position(i.get_identifier), self.world.get_entity_position('B'))
        if distance <= 1:
          return True
    return False

  # def player_owns_ball(self, player):
  #   return False

  def i_own_ball(self):
    if calc_point_distance(my_position, self.world.get_entity_position('B')) <= 1:
      return True
    else:
      return False

  def base(self, x):
      if x == 0:
        return 0.9
      else:
        return min(0.9 / x, 1)

# Tactical functions

  def run_to_ball(self, x):
    return 0.8 * self.base(x)

  def run_to_own_goal(self, x):
    if enemy_owns_ball():
      return 0.8
    else:
     return 0.2 * self.base(x)

  def run_to_enemy_goal(self, x):
    if we_own_ball():
      return 1
    else:
      return 0.2 * self.base(x)

  def stay(self):
    return 0.1

  def run_away_from_friend(self, x):
    return base(x)

  def run_away_from_l1(self):
    return 0.5

  def run_away_from_r2(self):
    return 0.5


  def run_tactics(self):
    self.clear_distances()
    self.set_own_position()
    self.get_distances()

    ll = []
    ll.append(('run_to_ball', self.run_to_ball(self.distance_ball)))
    ll.append(('stay', self.stay()))
    # ll.append('run_to_enemy_goal', run_to_enemy_goal())
    # ll.append('run_to_own_goal', run_to_own_goal())

    maxima = self.find_maxima(ll)
    shuffle(maxima)
    maximum = maxima[0][0]

    if maximum == 'run_to_ball':
      ball_pos = self.world.get_entity_position('B').to_list()
      self.mov.run(ball_pos[0], ball_pos[1])
    elif maximum == 'stay':
      self.mov.stop()

    debug('TACTICS: Decided to do the following action: "' + maximum + '"')
