# /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import world
from world import Vector
from random import shuffle
from logging import *
import math
import copy



class TacticsMain:

  def __init__(self, world, movement, nao):
    self.MIN_DISTANCE = 2
    self.world = world
    self.mov = movement
    self.index  = -1
    self.nao = nao

    self.my_position = None

    self.field_lines_idfs   = ["L1","L2","LL","LR","LM"]       #Field lines
    # self.right_penalty_idfs = ["LG1R","LG2R","LGR"]            #right penalty area
    # self.left_penalty_ifds  = ["LG1L","LG2L","LGL"]            #left penalty area
    self.right_goal_idfs    = ["G1R","G2R"]                    #right goal
    self.left_goal_idfs     = ["G1L","G2R"]                    #left goal
    self.player_t1_idfs     = ["P_1_1","P_1_2","P_1_3","P_1_4","P_1_5","P_1_6","P_1_7","P_1_8","P_1_9","P_1_10","P_1_11"]  #team 1
    self.player_t2_idfs     = ["P_2_1","P_2_2","P_2_3","P_2_4","P_2_5","P_2_6"]#team 2

    self.distance_team1 = []
    self.distance_team2 = []
    self.distance_lines = {}
    self.distances_ball = []
    self.distance_goal_left = None
    self.distance_goal_right= None

    self.headAngle = 0
    self.run_straight =False
    self.dest = None



  def set_own_position(self):
    if self.world.entity_from_identifier['P_1_' + str(self.nao.player_nr)].confidence >=0.5:
      self.my_position = self.nao.get_position()
    else:
      self.my_position = None

  """Calculate distances too all objects on the field  except the Flags and save them in the corresponding list."""
  def get_distances(self):
      for i in range(len(self.player_t1_idfs)):
        if self.world.entity_from_identifier[self.player_t1_idfs[i]].confidence > 0.5:
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t1_idfs[i]), self.my_position)
          self.distance_team1.append((self.player_t1_idfs[i], val))

      self.calculate_goal_distances(self.my_position)
      self.distance_lines = self.calc_line_distance(self.my_position)
      if True or not self.world.entity_from_identifier['B'].confidence < 0.5:
        for i in range(len(self.player_t1_idfs)):
          if self.world.entity_from_identifier[self.player_t1_idfs[i]].confidence > 0.5:
            dist =  self.calc_point_distance(self.world.get_entity_position('B'), self.world.get_entity_position(self.player_t1_idfs[i]))
            self.distances_ball.append((self.player_t1_idfs[i],dist))
        self.distances_ball = sorted(self.distances_ball, key = lambda dist : dist[1] )

  def calculate_goal_distances(self, my_position):
      val = self.calc_point_distance(self.world.get_entity_position(self.left_goal_idfs[0]), my_position)
      val = (val + self.calc_point_distance(self.world.get_entity_position(self.left_goal_idfs[1]), my_position))/2
      self.distance_goal_left = val

      val = self.calc_point_distance(self.world.get_entity_position(self.right_goal_idfs[0]), self.my_position)
      val = (val + self.calc_point_distance(self.world.get_entity_position(self.right_goal_idfs[1]), my_position))/2
      self.distance_goal_right = val

  def clear_distances(self):
      self.distance_goal_left = None
      self.distance_goal_right= None
      self.distance_lines = {}
      self.distance_team1= []
      self.distance_team2 =[]
      self.distances_ball = []

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



  def i_own_ball(self):
    if len(self.distances_ball) == 0:
      return False
    return self.distances_ball[0][0] == 'P_1_' +str(self.nao.player_nr)

  def offence_Player(self):
    for i in range( len(self.distances_ball)):
      if self.distances_ball[i][0] == 'P_1_' + str(self.nao.player_nr):
        return True
      if i == 3:
        return False

  def flocking_behavior(self):
    too_near = []
    for player in self.distance_team1:
      if player[1] <= self.MIN_DISTANCE and player[0] != 'P_1_'+str(self.nao.player_nr):
        too_near.append(player)
    if len(too_near) == 0:
      return False
    too_near = sorted(too_near, key = lambda dist: dist[1])
    self.run_straight = True

    new_tuples = []
    for i in too_near:
      pos = self.world.get_entity_position(i[0])
      x_dist = self.my_position.x - pos.x
      y_dist = self.my_position.y - pos.y

      new_tuples.append((self.my_position.x + (self.MIN_DISTANCE - x_dist),
                   self.my_position.y + (self.MIN_DISTANCE - y_dist)))

    average_tuple = (0, 0)
    for i in new_tuples:
      average_tuple[0] += i[0]
      average_tuple[1] += i[1]

    return (average_tuple[0]/len(too_near), average_tuple[1]/len(too_near))

  def run_tactics(self,hearObj):
    #if self.nao.lies_on_front():
     # return (('run', False),('stand_up','front'),('kick',False),('say',False), ('head',True))
    #if self.nao.lies_on_back():
      #return (('run', False),('stand_up','back'),('kick',False),('say',False), ('head',True))

    self.clear_distances()
    self.set_own_position()
    if self.my_position == None:
      return (('run', False),('stand_up',False),('kick',False),('say',False), ('head',True))
    self.get_distances()

    for line in self.field_lines_idfs:
      if line == 'M':
        continue
      if self.distance_lines[line] <= 0.2:
        if line == "L1":
          self.run_straight =True
          self.dest = Vector(self.my_position.x, self.my_position.y - 0.3)
        if line == "L2":
          self.run_straight =True
          self.dest = Vector(self.my_position.x, self.my_position.y + 0.3)
        if line == "LL":
          self.run_straight =True
          self.dest = Vector(self.my_position.x + 0.3, self.my_position.y)
        if line == "LR":
          self.run_straight =True
          self.dest = Vector(self.my_position.x - 0.3, self.my_position.y)




    if self.run_straight:
      if self.my_position ==None  or self.dest == None:
        print "MyPosition = " +  str(self.my_position) + " dist " +str(self.dest)
      vec = Vector(0,0)
      vec.x = self.my_position.x / self.dest.x
      vec.y = self.my_position.y / self.dest.y
      if vec.x <= 1.1 and vec.x >= 0.9 and vec.y <= 1.1 and vec.y >= 0.9:
        self.dest = None
        self.run_straight = False
      else:
        return (('run', self.dest.x,self.dest.y),('stand_up',False),('kick',False),('say',False), ('head',False))





    ball = self.i_own_ball()
    offence = self.offence_Player()
    defence = not ball and not offence

    result_list = [ball,offence,defence]
    run_tuple = ('run',False)
    kick_tuple = ('kick',False)
    if result_list[0]:
      if self.distances_ball[0][1] <= 0.2:
        kick_tuple = ('kick',1)
      else:
        tup = self.world.entity_from_identifier['B'].get_position()
        run_tuple = ('run',tup.x,tup.y)
    elif result_list[1]:
        tup = self.flocking_behavior()
        if tup is False :
          tup = (self.world.get_entity_position(self.distances_ball[0][0]).x-1.3,self.world.get_entity_position(self.distances_ball[0][0]).y-1.3)
        else:
          self.dest = Vector(tup[0],tup[1])
        run_tuple = ('run',tup[0],tup[1])
    elif result_list[2]:
        pass
    return (run_tuple, ('stand_up',False), kick_tuple, ('say',False), ('head',False))


