# /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import world
from world import Vector
from random import shuffle
import math



class TacticsMain:

  def __init__(self, world, movement, player_id):
    self.world = world
    self.mov = movement
    
    self.player_id = player_id
    
    self.my_position = None
    
    self.field_lines_idfs   = ["L1","L2","LL","LR","LM"]       #Field lines
    self.right_penalty_idfs = ["LG1R","LG2R","LGR"]            #right penalty area 
    self.left_penalty_ifds  = ["LG1L","LG2L","LGL"]            #left penalty area
    self.right_goal_ifds    = ["G1R","G2R"]                    #right goal
    self.left_goal_idfs     = ["G1L","G2R"]                    #left goal  
    self.player_t1_idfs     = ["P0","P1","P2","P3","P4","P5"]  #team 1
    self.player_t2_idfs     = ["P6","P7","P8","P9","P10","P11"]#team 2
    
    self.distance_team1 = {}
    self.distance_team2 = {}
    self.distance_goal_poles_right = {}
    self.distance_goal_poles_left = {}
    self.distance_lines = {}
    self.distance_ball = -1
    

    
    
  def set_own_position (self): 
      self.my_position = self.world.get_entity_position('P' + str(self.player_id))

  """Calculate distances too all objects on the field  except the Flags and save them in the corresponding list."""    
  def get_distances(self):
      for i in range(len(self.player_t1_idfs)):
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t1_idfs[i]), self.my_position) 
          self.distance_team1[self.player_t1_idfs[i]] = val
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t2_idfs[i]), self.my_position)
          self.distance_team2[self.player_t2_idfs[i]] = val
          if i < 2:
            val = self.calc_point_distance(self.world.get_entity_position(self.left_goal_idfs[i]), self.my_position)
            self.distance_goal_poles_left[self.left_goal_idfs[i]] = val
            val = self.calc_point_distance(self.world.get_entity_position(self.right_goal_ifds[i]), self.my_position)
            self.distance_goal_poles_right[self.right_goal_ifds[i]] = val
      self.distance_lines = self.calc_line_distance(self.my_position)
      self.distance_ball = self.calc_point_distance(self.world.get_entity_position('B'), self.my_position)
 
  def clear_distances(self):
      self.distance_goal_poles_left = {}
      self.distance_goal_poles_right= {}
      self.distance_lines = {}
      self.distance_team1= {}
      self.distance_team2 ={}
      self.distance_ball = -1

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
    return False

  def player_owns_ball(self, player):
    return False

  def base(self, x):
      return 1 / x

# Tactical functions

  def run_to_ball(self, x):
    return 0.5 * self.base(x)

  def run_to_own_goal(self, x):
    return 0.5 * self.base(x)

  def run_to_enemy_goal(self, x):
    return 0.5 * self.base(x)

  def stay(self):
    return 0.1

  def run_to_friend(self, x):
    return 0
  # return 0.5 * base(x)

  def run_away_from_friend(self, x):
    return 0
  # return 0.5 * base(x)

  def run_away_from_l1(self):
    return 0.5

  def run_away_from_r2(self):
    return 0.  
  
  
  def run_tactics(self):
    self.clear_distances()
    self.set_own_position()
    self.get_distances()
    print "Begin"
    print self.my_position
    print self.distance_ball
    print self.distance_lines
    print self.distance_team1
    print self.distance_team2
    print self.distance_goal_poles_left
    print self.distance_goal_poles_right
    print "end"
  
    """    
    all_arguments = [
      5,  # run_to_ball,
      5,  # run_to_own_goal,
      5,  # run_to_enemy_goal,
      None,  # stay,
      0,  # run_to_friend,
      0,  # run_away_from_friend
      None,  # run_away_from_l1,
      None,  # run_away_from_r2,
    ]
    all_functions = [
      self.run_to_ball,
      self.run_to_own_goal,
      self.run_to_enemy_goal,
      self.stay,
      self.run_to_friend,
      self.run_away_from_friend,
      self.run_away_from_l1,
      self.run_away_from_r2,
    ]

    all_results = []

    for i in range(len(all_functions)):
      if all_arguments[i]:
        all_results.append((all_functions[i].__name__, all_functions[i](all_arguments[i])))
      else:
        all_results.append((all_functions[i].__name__, all_functions[i]))

    maxima = self.find_maxima(all_results)

    shuffle(maxima)

    actual_tuple = maxima[0]"""




