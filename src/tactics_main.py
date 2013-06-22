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
    self.index  = -1
    self.nao = nao

    self.my_position = None

    self.field_lines_idfs   = ["L1","L2","LL","LR","LM"]       #Field lines
    # self.right_penalty_idfs = ["LG1R","LG2R","LGR"]            #right penalty area
    # self.left_penalty_ifds  = ["LG1L","LG2L","LGL"]            #left penalty area
    self.right_goal_idfs    = ["G1R","G2R"]                    #right goal
    self.left_goal_idfs     = ["G1L","G2R"]                    #left goal
    self.player_t1_idfs     = ["P_1_1","P_1_2","P_1_3","P_1_4","P_1_5","P_1_6"]  #team 1
    self.player_t2_idfs     = ["P_2_1","P_2_2","P_2_3","P_2_4","P_2_5","P_2_6"]#team 2

    self.distance_team1 = []
    self.distance_team2 = {}
    #self.distance_goal_poles_right = {}
    #self.distance_goal_poles_left = {}
    self.distance_lines = {}
    self.distance_ball = []
    self.distance_goal_left = None
    self.distance_goal_right= None
    self.wasToNear = False

    self.headAngle = 0
    self.enemy_players_ball_distance = [float('inf')] * number_of_players_per_team
    self.our_players_ball_distance = [float('inf')] * number_of_players_per_team
    self.last_to_near = [(0,0)]



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
            self.distance_ball.append((self.player_t1_idfs[i],dist))
            self.distance_ball = sorted(self.distance_ball, key = lambda dist : dist[1] )

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
      self.distance_team2 ={}
      self.distance_ball = [] 

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



# Utility functions
  def enemy_owns_ball(self):
    if len(self.distance_ball) == 0:
      return False
    for i in range(len(self.world.players)):
      if self.world.players[i].team != our_team_number:
        distance = self.calc_point_distance(self.world.get_entity_position(self.world.players[i].get_identifier()), self.world.get_entity_position('B'))
        self.enemy_players_ball_distance[i] = distance
        if distance <= 0.15:
          return True
    return False

  def we_own_ball(self):
    for i in range(len(self.world.players)):
      if self.world.players[i].team == our_team_number:
        player = self.world.entity_from_identifier[self.world.players[i].get_identifier()]
        if player.confidence > 0.5:
          distance = self.calc_point_distance(player.get_position(), self.world.get_entity_position('B'))
          self.enemy_players_ball_distance[i] = distance
          if distance <= 0.15:
            return True
    return False

  # def player_owns_ball(self, player):
  #   return False

  def i_own_ball(self):
      if len(self.distance_ball) == 0:
        return False
      return self.distance_ball[0][0] == 'P_1_' +str(self.nao.player_nr)


  def offence_Player(self):
    for i in range( len(self.distance_ball)):
      if self.distance_ball[i][0] == 'P_1_' + str(self.nao.player_nr):
        self.index = i
        return True
      if i == 3:
        return False

  def flocking_behavior(self):
    to_near = []
    for player in self.distance_team1:
      if player[1] <= 2 and player[0] != 'P_1_'+str(self.nao.player_nr):
        to_near.append(player)
    if len(to_near) == 0:
      return False
    if len(to_near) == 1:
        if self.last_to_near[0][0] == to_near[0][0] and self.last_to_near[0][1] >= to_near [0][1]:
          return (False,False)
        self.last_to_near = to_near
        pos = self.world.get_entity_position(to_near[0][0])
        x_dist = pos.x - self.my_position.x
        y_dist = pos.y - self.my_position.y
        if x_dist < 0:
          x_dist = -x_dist
        if x_dist < 1.3:
          if pos.x < self.my_position.x:
            return (self.my_position.x +0.5,self.my_position.y)
          else:
            return (self.my_position.x -0.5,self.my_position.y)
        else:
          if pos.y < self.my_position.y:
            return (self.my_position.x ,self.my_position.y+0.5)
          else:
            return (self.my_position.x ,self.my_position.y -0.5)
    else:
      return (False,False)
        

  def run_tactics(self,hearObj):
    if self.nao.lies_on_front():
      return (('run', False),('stand_up','front'),('kick',False),('say',False), ('head',True))
    if self.nao.lies_on_back():
      return (('run', False),('stand_up','back'),('kick',False),('say',False), ('head',True))

    self.clear_distances()
    self.set_own_position()
    if self.my_position == None:
      return (('run', False),('stand_up',False),('kick',False),('say',False), ('head',True))
    self.get_distances()



    ball = self.i_own_ball()
    offence = self.offence_Player()
    defence = not ball and not offence

    result_list = [ball,offence,defence]
    run_tuple = ('run',False)
    kick_tuple = ('kick',False)
    if result_list[0]:
      if self.distance_ball[0][1] <= 0.15:
        kick_tuple = ('kick',1)
      else:
        tup = self.world.entity_from_identifier['B'].get_position()
        run_tuple = ('run',tup.x,tup.y)
    elif result_list[1]:
        tup = self.flocking_behavior()
        if tup is False :
          tup = (self.world.get_entity_position(self.distance_ball[0][0]).x,self.world.get_entity_position(self.distance_ball[0][0]).y)
        run_tuple = ('run',tup[0],tup[1])
        print run_tuple
    elif result_list[2]:
      pass
     #print result_list'''
    return (run_tuple, ('stand_up',False), kick_tuple, ('say',False), ('head',False))


    

"""  ----------------------------Old version--------------------------------------------------------------------------
  def __init__(self, world, movement, nao):
    self.world = world
    self.mov = movement

    self.nao = nao

    self.my_position = None

    self.field_lines_idfs   = ["L1","L2","LL","LR","LM"]       #Field lines
    # self.right_penalty_idfs = ["LG1R","LG2R","LGR"]            #right penalty area
    # self.left_penalty_ifds  = ["LG1L","LG2L","LGL"]            #left penalty area
    self.right_goal_idfs    = ["G1R","G2R"]                    #right goal
    self.left_goal_idfs     = ["G1L","G2R"]                    #left goal
    self.player_t1_idfs     = ["P_1_1","P_1_2","P_1_3","P_1_4","P_1_5","P_1_6"]  #team 1
    self.player_t2_idfs     = ["P_2_1","P_2_2","P_2_3","P_2_4","P_2_5","P_2_6"]#team 2

    self.distance_team1 = {}
    self.distance_team2 = {}
    #self.distance_goal_poles_right = {}
    #self.distance_goal_poles_left = {}
    self.distance_lines = {}
    self.distance_ball = None
    self.distance_goal_left = None
    self.distance_goal_right= None

    self.headAngle = 0

    self.enemy_players_ball_distance = [float('inf')] * number_of_players_per_team
    self.our_players_ball_distance = [float('inf')] * number_of_players_per_team



  def set_own_position(self):
    if self.world.entity_from_identifier['P_1_' + str(self.nao.player_nr)].confidence >=0.5:
      self.my_position = self.nao.get_position()
    else:
      self.my_position = None

  
  def get_distances(self):
      for i in range(len(self.player_t1_idfs)):
        if self.world.entity_from_identifier[self.player_t1_idfs[i]].confidence > 0.5:
          val = self.calc_point_distance(self.world.get_entity_position(self.player_t1_idfs[i]), self.my_position)
          self.distance_team1[self.player_t1_idfs[i]] = val
         #val = self.calc_point_distance(self.world.get_entity_position(self.player_t2_idfs[i]), self.my_position)
         # self.distance_team2[self.player_t2_idfs[i]] = val 

      self.calculate_goal_distances(self.my_position)
      self.distance_lines = self.calc_line_distance(self.my_position)
      self.distance_ball = self.calc_point_distance(self.world.get_entity_position('B'), self.my_position)

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
      self.distance_team1= {}
      self.distance_team2 ={}
      self.distance_ball = None

  
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
    for i in range(len(self.world.players)):
      if self.world.players[i].team != our_team_number:
        distance = self.calc_point_distance(self.world.get_entity_position(self.world.players[i].get_identifier()), self.world.get_entity_position('B'))
        self.enemy_players_ball_distance[i] = distance
        if distance <= 0.15:
          return True
    return False

  def we_own_ball(self):
    for i in range(len(self.world.players)):
      if self.world.players[i].team == our_team_number:
        player = self.world.entity_from_identifier[self.world.players[i].get_identifier()]
        if player.confidence > 0.5:
          distance = self.calc_point_distance(player.get_position(), self.world.get_entity_position('B'))
          self.enemy_players_ball_distance[i] = distance
          if distance <= 0.15:
            return True
    return False

  # def player_owns_ball(self, player):
  #   return False

  def i_own_ball(self):
    if self.calc_point_distance(self.my_position, self.world.get_entity_position('B')) <= 0.15:
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
    return 0.9 * self.base(x)

  def run_to_own_goal(self, x):
    if self.enemy_owns_ball():
      return 0.8 * self.base(x)
    else:
      return 0.05

  def run_to_enemy_goal(self, x):
    if self.we_own_ball():
      return 0.95
    else:
      return 0.05

  def stay(self):
    return 0.01


  def run_away_from_friend(self):
    list = []
    for n in self.distance_team1:
      if n == 'P_1_' + str(self.nao.player_nr):
        continue
      dist =  self.distance_team1[n]
      if dist <=  2.0:
        list.append(n)
    return list

  def run_away_from_l1(self,x):
    return self.base(x)/10

  def run_away_from_r2(self,x):
    return self.base(x)/10


  def run_tactics(self,hearObj):


    self.clear_distances()
    self.set_own_position()
    if self.my_position == None:
      return (('run', False),('stand_up',False),('kick',False),('say',False), ('head',True))

    self.get_distances()

    toClose = self.run_away_from_friend()
    ll = []
    ll.append(('run_to_ball', self.run_to_ball(self.distance_ball)))
    ll.append(('stay', self.stay()))
    ll.append(('run_to_enemy_goal', self.run_to_enemy_goal(self.distance_goal_right)))
    #ll.append(('run_to_own_goal', self.run_to_own_goal(self.distance_goal_left)))
    ll.append(('run_away_from_l1',self.run_away_from_l1(self.distance_lines['L1'])))
    ll.append(('run_away_from_r2',self.run_away_from_r2(self.distance_lines['L2'])))
    ll.append(('run_away_from_friend',len(toClose)))
    # ll.append('run_to_enemy_goal', run_to_enemy_goal())
    # ll.append('run_to_own_goal', run_to_own_goal())

    maxima = self.find_maxima(ll)
    shuffle(maxima)
    maximum = maxima[0][0]

    run_tuple = ('run', False)
    kick_tuple = ('kick', False)
    if maximum == 'run_to_ball':
      ball_pos = self.world.get_entity_position('B').to_list()
      run_tuple = ('run', ball_pos[0], ball_pos[1])
    elif maximum == 'stay':
      run_tuple = ('run', False)
    elif maximum == 'run_to_enemy_goal':
      if self.i_own_ball():
        run_tuple = ('run', False)
        kick_tuple = ('kick', True)
      else:
        x = (self.world.get_entity_position(self.right_goal_idfs[0]).x + self.world.get_entity_position(self.right_goal_idfs[1]).x)/2
        y = (self.world.get_entity_position(self.right_goal_idfs[0]).y + self.world.get_entity_position(self.right_goal_idfs[1]).y)/2
        run_tuple = ('run', x, y)
        kick_tuple = ('kick', False)
    elif maximum == 'run_to_own_goal':
        x = (self.world.get_entity_position(self.left_goal_idfs[0]).x + self.world.get_entity_position(self.left_goal_idfs[1]).x)/2
        y = (self.world.get_entity_position(self.left_goal_idfs[0]).y + self.world.get_entity_position(self.left_goal_idfs[1]).y)/2
        run_tuple = ('run', x, y)
    elif maximum == 'run_away_from_r2':
      run_tuple = ('run', self.my_position.x, self.my_position.y + 0.1)
    elif maximum == 'run_away_from_l1':
      run_tuple = ('run',self.my_position.x, self.my_position.y - 0.1)
    elif maximum == 'run_away_from_friend':
      run_tuple = ('run',False)




    # debug(""+str(ll))
    # debug('TACTICS: Decided to do the following action: "' + maximum + '"')
    return (run_tuple, ('stand_up',False), kick_tuple, ('say',False), ('head',False))"""
