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
from math import *
import math

# Hacky way to make global variables in Python
__builtin__.our_team = "DAI-Labor"
__builtin__.our_team_number = 1
__builtin__.number_of_players_per_team = 11

#some change

class Agent:

    def __init__(self,p_nr):
        self.player_nr = p_nr
        self.agentSocket = sock.Sock("localhost", 3100, our_team, self.player_nr)
        self.monitorSocket = sock.Sock("localhost", 3200, None, None)

        self.drawer = drawing.Drawing(0, 0)

        self.world = world.World()
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
        self.scene = scene.Scene()
        self.scene_updated = False #variable for handling the scenegraph
        self.position = None #variable that holds the agent's own position (read from the scenegraph)
        self.used_keyframes = False
        self.ticks = 0
        self.estimated_point = None

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
                '''
                if(shared_value.value == 1):
                    shared_value.value = 0
                    self.scene.run_cycle(shared_list)
                    self.scene_updated = True
                    del shared_list[:]
                    '''
                  
                parsed_msg = parser.parse_sexp(msg)
                while len(parsed_msg) != 0:
                    current_preceptor = parsed_msg.pop()
                    if current_preceptor[0] == 'HJ':
                        self.perception.process_joint_positions(current_preceptor, self.nao)
                    elif current_preceptor[0] == 'See':
                        self.perception.process_vision(current_preceptor, self.world)
                        # ok, vision is parsed and processed. save the raw world model for further use:
                        self.world_history_raw.append(copy.deepcopy(self.world))
                        if len(self.world_history_raw) > 100:
                            self.world_history_raw.popleft()
                        # smoothing:
                        self.interpol.smooth_mobile_entity_positions()
                        # world is smooth now. final version. add to smooth world queue:
                        self.world_history.append(copy.deepcopy(self.world))
                        if len(self.world_history) > 100:
                            self.world_history.popleft()
                        # drawing some position as stored in world model:
                        self.debug_draws()

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
                                    self.us = "Left"
                                    self.them = "Right"
                                else:
                                    self.on_left = False
                                    self.us = "Right"
                                    self.them = "Left"

                if(self.gs == 'BeforeKickOff' or self.gs == 'Goal_Left' or self.gs == 'Goal_Right'):
                    goto_startposition(self)
                    self.keyFrameEngine.stand()
                    #self.keyFrameEngine.work()
                elif(self.gs == 'KickIn_'+self.them or self.gs == 'corner_kick_'+self.them.lower() or self.gs == 'goal_kick_'+self.them.lower() or self.gs =='free_kick_'+self.them.lower()):
                    self.ball_posx = self.world.ball.get_position().x
                    self.ball_posy = self.world.ball.get_position().y
                    self.closest_to_ball = self.tactics.get_distances_ball()
                    if self.ball_posx < 0:
                        self.ball_posx = -self.ball_posx
                    if self.gs == 'KickIn_'+self.them:
                        for i in range(len(self.closest_to_ball)):
                            if self.closest_to_ball[i][0] == 'P_1_'+str(self.nao.player_nr) and i < 2:
                                if self.ball_posy < 0: 
                                    self.movement.run(relx(self, self.ball_posx+i),self.ball_posy+1)
                                else: 
                                    self.movement.run(relx(self, self.ball_posx+i),self.ball_posy-1)
                    elif self.gs == 'corner_kick_'+self.them.lower() and len(self.closest_to_ball) > 0:
                        if self.closest_to_ball[0][0] == 'P_1_'+str(self.nao.player_nr):
                            if self.ball_posy < 0: 
                                self.movement.run(relx(self, self.ball_posx-0.75),self.ball_posy+1)
                            else: 
                                self.movement.run(relx(self, self.ball_posx-0.75),self.ball_posy-1)
                    elif self.gs =='free_kick_'+self.them.lower():
                        for i in range(len(self.closest_to_ball)):
                            if self.closest_to_ball[i][0] == 'P_1_'+str(self.nao.player_nr) and i < 3:
                                if self.ball_posy < 0: 
                                    self.movement.run(relx(self, self.ball_posx+1.5),self.ball_posy+(i*0.5))
                                else: 
                                    self.movement.run(relx(self, self.ball_posx+1.5),self.ball_posy-(i*0.5))
                    else:
                        goto_waitposition(self)
                    self.keyFrameEngine.stand()
                    self.keyFrameEngine.work()
                elif(self.gs == 'KickOff_'+self.us or self.gs == 'PlayOn'):
                    if self.player_nr > 1:
                        if not self.keyFrameEngine.working:
                            actions = self.tactics.run_tactics(self.hearObj)
                            #print actions
                            self.hearObj = None
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
                                            self.keyFrameEngine.kick_right()
                                            break
                                        elif item[1] == 2:
                                            self.keyFrameEngine.kick_strong_right()#self.keyFrameEngine.kick_strong_right()
                                            break
                                    if item[0] == 'run':
                                        if item[1] is False:
                                            self.movement.stop()
                                        elif item[1] == 'shoot':
                                            self.movement.run_to_shoot_position(item[2],item[3])
                                        elif item[1] == 'turn':
                                            self.movement.turn(item[2])
                                        else:
                                            self.movement.run(item[1],item[2])
                                    if item[0] == 'say':
                                        if item[1] is not False:
                                            self.communication.sayMessageType5(item[1],item[2], item[3],item[4],item[5])
                                    if item[0] == 'head':
                                        if item[1] is True:
                                            self.keyFrameEngine.head_lookAround()
                                        elif item[1] == 'stop':
                                            self.keyFrameEngine.stop_head()
                                        elif item[1] != False:
                                            print 'Down'
                                            self.keyFrameEngine.head_down()
                                        elif item[1] =='reset':
                                            self.keyFrameEngine.head_reset()
                    else:
                        '''
                        Keepers Part:
                        '''
                        if not self.keyFrameEngine.working:
                            #print 'keyframe is NOT working'
                            #if the keyframesengine was used before jo have to rest beampos
                            if self.used_keyframes:
                                #self.movement.reset_pos()
                                #self.movement.move_keeper()
                                self.used_keyframes = False

                            if self.nao.lies_on_front():
                                self.used_keyframes = True
                                self.keyFrameEngine.stand_up_from_front()

                            elif self.nao.lies_on_back():
                                self.used_keyframes = True
                                self.keyFrameEngine.stand_up_from_back()

                            #he didn't see the ball in the last 10 see-perceptions
                            elif self.perception.see_the_ball == False:
                                if self.movement.degrees < -90:
                                    self.movement.turn_about(+2)
                                else:
                                    self.movement.turn_about(-2)

                            #If the ball is in the penalty area then walk to the ball an kick it away
                            elif(self.world.ball.get_position().x < -13 and -3 < self.world.ball.get_position().y < 3):
                                #print 'ball in penalty-area'
                                if not self.movement.reached_position:
                                    self.movement.run_to_shoot_position(15,0)
                                else:
                                    self.used_keyframes = True
                                    self.keyFrameEngine.kick_right()
                                    self.movement.reached_position = False

                            elif(self.old_ball_pos != None):
                                self.movement.move_keeper()
                                
                                #calculate current direction and amount of the ball
                                self.direction = self.world.ball.get_position() - self.old_ball_pos
                                self.velocity = math.sqrt(self.direction.x*self.direction.x + self.direction.y*self.direction.y)

                                #stretch the line
                                if self.direction.x != 0:
                                    self.increase = (self.direction.y / self.direction.x)
                                else:
                                    self.increase = self.direction.y
                                self.y_intercept = self.old_ball_pos.y - self.increase*self.old_ball_pos.x
                                #and calculate where the ball will hit the goalline
                                self.goal_intercept = (-15)*self.increase + self.y_intercept

                                #just in case that:
                                #   - the balls direction in x is < 0
                                #   - the ball moves fast enough
                                #   - the ball will cross the goalline between the goalpoals
                                #calculate the estimated point where the ball will stop
                                if (self.direction.x < 0 and self.velocity > 0.05 and -1 < self.goal_intercept < 1): 
                                    #Begin of calculation where the ball will stop
                                    self.estimated_point = self.world.ball.get_position()
                                    # I assume that the balls velocity after 60ms will decrease with the factor 0.7
                                    # and add it n times to the estimated point until the velocity is nearly zero
                                    self.direction.x = self.direction.x*10
                                    self.direction.y = self.direction.y*10
                                    while(self.velocity > 0.1):
                                        self.velocity = self.velocity*0.9
                                        self.direction.x = self.direction.x*self.velocity
                                        self.direction.y = self.direction.y*self.velocity
                                        self.estimated_point.x = self.estimated_point.x+self.direction.x
                                        self.estimated_point.y = self.estimated_point.y+self.direction.y               
                                     
                                    if(self.estimated_point.x < -15):
                                        self.used_keyframes = True
                                        if (-0.6 < self.goal_intercept < 0.6):
                                            self.keyFrameEngine.parry_straight()
                                        elif(-0.6 >= self.goal_intercept >= 1.0):
                                            self.keyFrameEngine.parry_right()
                                        elif(0.6 <= self.goal_intercept <= 1.0):
                                            self.keyFrameEngine.parry_left() 

                            self.old_ball_pos =  self.world.ball.get_position()
                            if self.estimated_point != None:
                                self.drawer.drawCircle(self.estimated_point, 0.2, 3, [255,0,51], "est_p")
                                self.drawer.showDrawingsNamed("est_p")

                elif(self.gs == 'KickOff_'+self.us or self.gs == 'KickIn_'+self.us or self.gs == 'corner_kick_left' or self.gs == 'goal_kick_'+self.us or self.gs == 'free_kick_'+self.us):
                    self.ball_posx = self.world.ball.get_position().x
                    self.ball_posy = self.world.ball.get_position().y
                    self.closest_to_ball = self.tactics.get_distances_ball()
                    if len(self.closest_to_ball) > 0:
                       if self.closest_to_ball[0][0] == 'P_1_'+str(self.nao.player_nr):
                            self.movement.run(self.ball_posx,self.ball_posy)

                elif(self.gs == 'GameOver'):
                    raise SystemExit(0)
                self.keyFrameEngine.work()
                self.agentSocket.flush()
                self.monitorSocket.flush()
                
    def debug_draws(self):
        # some helperz:
        player_id = 'P_1_' + str(self.player_nr)
        player = self.world.entity_from_identifier[player_id]
        player_pos = player.get_position()
        # draw player pos & see vector:
        self.drawer.drawCircle(player_pos, 0.2, 3, [200, 155, 100], "all." + player_id + ".ownpos")
        self.drawer.drawArrow(player_pos, player_pos + world.Vector(player._see_vector[0] * 2, player._see_vector[1] * 2), 3, [255, 150, 0], "all." + player_id + ".see")
        # draw mobilez:
        for me in self.world.mobile_entities():
            if isinstance(me, world.Ball):
                color = [200, 200, 200]
            else:   # is instace of player
                color = [255, 0, 0] if me.get_identifier()[2:3] == '2' else [0, 255, 0]
            self.drawer.drawLine(player_pos, me.get_position(), 1, color, "all." + player_id + ".mobile_entity_line")
            self.drawer.drawCircle(me.get_position(), 0.2, 3, color, "all." + player_id + ".mobile_entity_circle")
        self.drawer.showDrawingsNamed("all." + player_id)

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
        self.movement.run(relx(self, 10), (6-((self.player_nr-2)*4)))
    elif (self.player_nr > 5) and (self.player_nr < 10):
        #self.agentSocket.enqueue(" ( beam 5 "+str((6-(((self.player_nr-2)-4)*4)))+" 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 5 "+str((6-(((self.player_nr-2)-4)*4)))+" 0.38 0 )")
        self.movement.run(relx(self, 5), (6-(((self.player_nr-2)-4)*4)))
    elif self.player_nr == 10:
        #self.agentSocket.enqueue(" ( beam 10 2 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 10 2 0.38 0 )")
        self.movement.run(relx(self, 3), 2)
    elif self.player_nr == 11:
        #self.agentSocket.enqueue(" ( beam 11 -2 0 ) ")
        #self.agentSocket.enqueue("agent (unum" + str(self.player_nr) + ") (team Left) (move 11 -2 0.38 0 )")
        self.movement.run(relx(self, 2), -2)


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
