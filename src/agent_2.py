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
from sys import argv

global our_team
our_team = "DAI-Labor"

class Agent:

    def __init__(self,p_nr):
        self.player_nr = p_nr
        self.agentSocket = sock.Sock("localhost", 3100, our_team, self.player_nr)
        self.monitorSocket = sock.Sock("localhost", 3200, None, None)

        self.world = world.World(6, 30, 20) 
        self.nao = nao.Nao(self.world, self.player_nr)
        self.perception = perception.Perception(self.player_nr, our_team)
        self.movement = movement.Movement(self.world, self.agentSocket,self.player_nr)
       	self.keyFrameEngine = keyframe_engine.Keyframe_Engine(self.nao,self.agentSocket)
        self.communication = communication.Communication(self.agentSocket)
        self.tactics = tactics_main.TacticsMain(self.world,self.movement,self.nao)
        self.start()

    def start(self):
            self.agentSocket.start()
            self.monitorSocket.start()

            offset_for_player = -9 + (3*self.player_nr)
            self.agentSocket.enqueue(" ( beam -10 "+ str(offset_for_player) +" 0 ) ")
            self.agentSocket.flush()

            self.keyFrameEngine.fall_on_front()

            self.keyFrameEngine.work()
            self.agentSocket.flush()
            self.keyFrameEngine.stand_up_from_front()
            self.keyFrameEngine.work()
            self.agentSocket.flush()

            while True:
                msg = self.agentSocket.receive()
                parsed_msg = parser.parse_sexp(msg)
                while len(parsed_msg) != 0:
                    current_preceptor = parsed_msg.pop()
                    if current_preceptor[0] == 'HJ':
                        self.perception.process_joint_positions([current_preceptor], self.nao)
                    elif current_preceptor[0] == 'See':
                        self.perception.process_vision([current_preceptor],self.world)
                    elif current_preceptor [0] == 'GYR':
                        self.perception.process_gyros([current_preceptor], self.nao)
                    elif current_preceptor[0] == 'hear':
                        pass
                    #actions = self.tactics.run_tactics()
                    actions = (('run', False),('stand_up','front'),('kick',False),('say',False), ('head',False))
                    if not self.keyFrameEngine.working:
                        for item in actions:
                            if item[0] == 'standup':
                                if item[1] == 'front':
                                    self.keyFrameEngine.stand_up_from_front()
                                    break
                                if item[1] == 'back':
                                    self.keyFrameEngine.stand_up_from_back()
                                    break
                            if item[0] == 'kick':
                                if item[1] == 1:
                                    self.keyFrameEngine.kick1()
                                else:
                                    pass
                            if item[0] == 'run':
                                if not item[1]:
                                    self.movement.stop()
                                else:
                                    self.movement.run(item[1],item[2])
                            if item[0] == 'say':
                                pass
                            if item[0] == 'head':
                                if item[1] == True:
                                    self.keyFrameEngine.head_lookAround()
                                elif item[1] != False:
                                    self.keyFrameEngine.head_move(item1[1])
                    self.keyFrameEngine.work()
                    self.agentSocket.flush()
                    self.monitorSocket.flush()    
                                


                        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        agent_id = int(argv[1])
    except:
        print("You need to call \"./agent.py <player_id>\".")
        exit(1)

    Agent(agent_id)