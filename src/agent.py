#!/usr/bin/python
# -*- coding: utf-8 -*-

import sock
import parser
import world
import perception
import logging
import tactics_main
import movement
import nao
import keyframe_engine
import communication
import signal
import sys
from sys import argv
import drawing
import __builtin__
import copy
import collections
import math
import scene
import statistics
import numpy
import interpol
from multiprocessing import Process, Manager, Value

# Hacky way to make global variables in Python
__builtin__.our_team = "DAI-Labor"
__builtin__.our_team_number = 1
__builtin__.number_of_players_per_team = 6



class Agent:

    def __init__(self,p_nr):
        self.player_nr = p_nr
        self.agentSocket = sock.Sock("localhost", 3100, our_team, self.player_nr)
        self.monitorSocket = sock.Sock("localhost", 3200, None, None)

        self.drawer = drawing.Drawing(0, 0)

        self.world = world.World(11, 30, 20)
        self.world_history = collections.deque()        # smoothed world (double ended queue)
        self.world_history_raw = collections.deque()    # raw world, as perceived
        self.nao = nao.Nao(self.world, self.player_nr)
        self.perception = perception.Perception(self.player_nr, our_team, self.drawer)
        self.interpol = interpol.Interpol(self.player_nr, self.world, self.world_history, self.world_history_raw)
        self.movement = movement.Movement(self.world, self.monitorSocket,self.player_nr)
       	self.keyFrameEngine = keyframe_engine.Keyframe_Engine(self.nao,self.agentSocket)
        self.communication = communication.Communication(self.agentSocket)
        self.tactics = tactics_main.TacticsMain(self.world,self.movement,self.nao)
        self.hearObj = None
        self.statistic = statistics.Statistics()
        self.old_ball_pos = None #one tick before
        self.t = None #variable for the keeper
        self.scene = scene.Scene()
        self.scene_updated = False #variable for handling the scenegraph
        self.position = None #variable that holds the agent's own position (read from the scenegraph)

    def start(self):
            self.monitorSocket.start()
            self.agentSocket.start()

            offset_for_player = -9 + (3 * self.player_nr)
            self.agentSocket.enqueue(" ( beam -10 " + str(offset_for_player) + " 0 ) ")
            #self.agentSocket.enqueue(" ( beam -0.5 0 0 ) ")
            self.agentSocket.flush()
            
             #stuff to handle the second thread that receives via monitor protocol: 
            manager = Manager()
            shared_list = manager.list()
            shared_value = Value('b', 0)
            # start second thread:
            # Process(target=receive_monitor_data, args=(shared_list, shared_value)).start()


            while True:
                msg = self.agentSocket.receive()
                
                if(shared_value.value == 1):
                    shared_value.value = 0
                    self.scene.run_cycle(shared_list)
                    self.scene_updated = True
                    del shared_list[:]
                  
                parsed_msg = parser.parse_sexp(msg)
                while len(parsed_msg) != 0:
                    current_preceptor = parsed_msg.pop()
                    if current_preceptor[0] == 'HJ':
                        self.perception.process_joint_positions(current_preceptor, self.nao)
                    elif current_preceptor[0] == 'See':
                        self.perception.process_vision(current_preceptor, self.world)
                        # drawing some position as stored in world model:
                        player_id = 'P_1_' + str(self.player_nr)
                        player = self.world.entity_from_identifier[player_id]
                        self.drawer.drawCircle(player.get_position(), 0.2, 3, [200, 155, 100], "all." + player_id + ".ownpos")
                        self.drawer.drawArrow(player.get_position(), player.get_position() + world.Vector(player._see_vector[0] * 2, player._see_vector[1] * 2), 3, [255, 150, 0], "all." + player_id + ".see")
                        self.drawer.drawCircle(self.world.get_entity_position('B'), 0.2, 3, [200, 200, 200], "all." + player_id + ".ballpos")
                        self.drawer.showDrawingsNamed("all." + player_id)
                        # ok, vision is parsed and processed, we've got our final world model for this cycle.
                        # save it:
                        self.world_history.append(copy.deepcopy(self.world))
                        if len(self.world_history) > 100:
                            self.world_history.popleft()

                        #perception statistics
                        #scene graph auslesen
                        #self.scene.run_cycle()
                        #ps = self.scene.get_position_xy( 'left', self.player_nr)
                        #pw = self.nao.get_position()
                        #if ps != None :
                        #    self.statistic.abweichung.append(numpy.array([pw.x - ps[0] ,pw.y - ps[1]]))

                    elif current_preceptor[0] == 'GYR':
                        self.perception.process_gyros(current_preceptor, self.nao)
                    elif current_preceptor[0] == 'ACC':
                        # when ĺying on back, it's like ['ACC', ['n', 'torso'], ['a', 0, 9.62, -1.82]]
                        # when ĺying on front, it's like ['ACC', ['n', 'torso'], ['a', 0, -9.76, -0.96]]
                        self.perception.process_accelerometer(current_preceptor, self.nao)
                    elif current_preceptor[0] == 'hear':
                        self.hearObj = self.communication.hear(current_preceptor)
                    elif current_preceptor[0] == 'GS':
                        for i in current_preceptor:
                            if i[0] == 'pm':
                                self.gs = i[1]
                            if i[0] == 'team':
                                if i[1] == 'left':
                                    self.on_left = True
                                else:
                                    self.on_left = False
                if self.on_left:
                  self.us   = "Left"
                  self.them = "Right"
                else:
                  self.us   = "Right"
                  self.them = "Left"

                if(self.gs == 'BeforeKickOff' or self.gs == 'Goal_Left' or self.gs == 'Goal_Right'):
                    goto_startposition(self)
                    self.keyFrameEngine.stand()
                    self.keyFrameEngine.work()
                elif(self.gs == 'KickIn_'+self.them or self.gs == 'corner_kick_'+self.them.lower() or self.gs == 'goal_kick_'+self.them.lower() or self.gs =='free_kick_'+self.them.lower()):
                    goto_waitposition(self)
                    self.keyFrameEngine.stand()
                    self.keyFrameEngine.work()
                elif(self.gs == 'KickOff_'+self.us or self.gs == 'PlayOn'):
                    if not self.keyFrameEngine.working and self.player_nr > 1:
                        actions = self.tactics.run_tactics(self.hearObj)
                        if actions != None:
                            for item in actions:
                                if item[0] == 'stand_up':
                                    if item[1] == 'front':
                                        self.keyFrameEngine.stand_up_from_front()
                                        break
                                    if item[1] == 'back':
                                        self.keyFrameEngine.stand_up_from_back()
                                        break
                                if item[0] == 'kick':
                                    if item[1] == 1:
                                        self.keyFrameEngine.kick1()
                                    elif item[1] == 2:
                                        self.keyFrameEngine.strong_kick()
                                if item[0] == 'run':
                                    if item[1] is False:
                                        self.movement.stop()
                                    elif item[1] == 'shoot':
                                        self.movement.run_to_shoot_position(item[2],item[3])
                                    else:
                                        self.movement.run(item[1],item[2])
                                if item[0] == 'say':
                                    pass
                                if item[0] == 'head':
                                    if item[1] is True:
                                        self.keyFrameEngine.head_lookAround()
                                    elif item[1] != False:
                                        self.keyFrameEngine.head_move(item[1])
                    else:

                        if(self.old_ball_pos != None):
                            # print (self.world.ball.get_position())
                            self.direction = self.world.ball.get_position() - self.old_ball_pos
                            self.betrag = math.sqrt(self.direction.x*self.direction.x + self.direction.y*self.direction.y)
                            # What do you do when you have self.direction.x == 0? :o -- Max
                            self.increase = (self.direction.y / self.direction.x)
                            self.y_intercept = self.old_ball_pos.y - self.increase*self.old_ball_pos.x
                            self.goal_intercept = (-15)*self.increase + self.y_intercept
                            self.g_point =  world.Vector(-15,self.goal_intercept)

                            if (self.betrag > 1):
                                #print ('old_pos.x: '+str(self.old_ball_pos.x) +' old_pos.y: '+str(self.old_ball_pos.y))
                                #print ('pos.x: '+str(self.world.ball.get_position().x) +' pos.y: '+str(self.world.ball.get_position().y))
                                #print ('dir.x: '+str(self.direction.x)+' dir.y: '+str(self.direction.y))
                                #print ('steigung: '+str(self.increase))
                                self.t_vec = (self.g_point - self.world.ball.get_position())/self.betrag
                                self.t = math.sqrt(self.t_vec.x**2 + self.t_vec.y**2)
                                print ('estimated t cycles until the ball is in the goal: '+str(self.t))
                                #print self.goal_intercept
                        if(self.t > 1):
                            self.movement.move_keeper()
                        else:
                            pass #use keyeginge
                        self.old_ball_pos = self.world.ball.get_position()

                #a = raw_input('press enter:')
                elif(self.gs == 'KickOff_Right'):
                    pass
                elif(self.gs == 'PlayOn'):
                    print "PLAYON!!"
                    pass
                elif(self.gs == 'KickIn_Left'):
                    pass
                elif(self.gs == 'corner_kick_left'):
                    pass
                elif(self.gs == 'goal_kick_left'):
                    pass
                #elif(self.gs == 'offside_left'):
                #    pass
                #elif(self.gs == 'offside_right'):
                #    pass
                elif(self.gs == 'GameOver'):
                    raise SystemExit(0)
                elif(self.gs == 'free_kick_left'):
                    pass
                self.keyFrameEngine.work()
                self.agentSocket.flush()
                self.monitorSocket.flush()
                
# updates the agent's position
def get_position(self):
    if (self.scene_updated):
        if(self.on_left):
            self.position = self.scene.get_position_xy("left", self.player_nr)
        else:
            self.position = self.scene.get_position_xy("right", self.player_nr)
    self.scene_updated = False
    return self.position

def relx(self, x):
    return -x if self.on_left else x

def goto_startposition(self):
    if self.player_nr == 1:
        self.agentSocket.enqueue(" ( beam "+str(relx(self, 14))+" 0 0 ) ")
    elif (self.player_nr > 1) and (self.player_nr < 6):
        self.agentSocket.enqueue(" ( beam "+str(relx(self, 10))+" "+str((6-((self.player_nr-2)*4)))+" 0 ) ")
    elif (self.player_nr > 5) and (self.player_nr < 10):
        self.agentSocket.enqueue(" ( beam "+str(relx(self, 5))+" "+str((6-(((self.player_nr-2)-4)*4)))+" 0 ) ")
    elif self.player_nr == 10:
        self.agentSocket.enqueue(" ( beam "+str(relx(self, 3))+" 2 0 ) ")
    elif self.player_nr == 11:
        self.agentSocket.enqueue(" ( beam "+str(relx(self, 2))+" -2 0 ) ")

def goto_waitposition(self):
    if self.player_nr == 1:
        #self.agentSocket.enqueue(" ( beam -14 0 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move -14 0 0.384 0 )")
        self.movement.run(relx(self, 14), 0)
    elif (self.player_nr > 1) and (self.player_nr < 6):
        #self.agentSocket.enqueue(" ( beam -5 "+str((6-((self.player_nr-2)*4)))+" 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move -5 "+str((6-((self.player_nr-2)*4)))+" 0.38 0 )")
        self.movement.run(relx(self, 5), (6-((self.player_nr-2)*4)))
    elif (self.player_nr > 5) and (self.player_nr < 10):
        #self.agentSocket.enqueue(" ( beam 5 "+str((6-(((self.player_nr-2)-4)*4)))+" 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 5 "+str((6-(((self.player_nr-2)-4)*4)))+" 0.38 0 )")
        self.movement.run(relx(self, -5), (6-(((self.player_nr-2)-4)*4)))
    elif self.player_nr == 10:
        #self.agentSocket.enqueue(" ( beam 10 2 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 10 2 0.38 0 )")
        self.movement.run(relx(self, -10), 2)
    elif self.player_nr == 11:
        #self.agentSocket.enqueue(" ( beam 11 -2 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 11 -2 0.38 0 )")
        self.movement.run(relx(self, -11), -2)


# method that receives via monitor protocol
def receive_monitor_data(list, val):
        socket = sock.Sock("localhost", 3200, None, None)
        socket.start()
        while True:
            msg = socket.receive()
            data = parser.parse_sexp(msg)
            if not list:
                list.extend(data)
                val.value = 1

def signal_handler(signal, frame):
    #print("Here some statistics:")
    #a.statistic.print_results()
    print("Received SIGINT")
    print("Closing sockets and terminating...")
    a.agentSocket.close()
    a.monitorSocket.close()
    sys.exit(0)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        agent_id = int(argv[1])
    except:
        print("You need to call \"./agent.py <player_id>\".")
        exit(1)

    global a
    a = Agent(agent_id)

    signal.signal(signal.SIGINT, signal_handler)

    a.start()
