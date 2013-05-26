from Keyframes import stand_up_from_back, testframe, fall_back
import math
import time

class Keyframe_Engine:
    
    def __init__(self, nao, socket):
        self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.last_angle = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.progressed_time = 0
        self.keyframe_line = 0
        self._default_time = 20.0
        self.nao = nao
        self.socket = socket
        self.fall = True
        self.angle = 0.0
        self.done = 0

    def fall_on_front(self):
        while(self.fall):
            self.socket.enqueue("(rle5 2.0)")
            self.socket.flush()
            self.fall = False
    
    def fall_on_back(self):
        keyframe = fall_back.keyframe
        name = stand_up_from_back.name
        self.get_joint_values(name)
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 1
            self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
    
    def stand_up_from_back(self):
        keyframe = stand_up_from_back.keyframe
        name = stand_up_from_back.name
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 2
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
        if self.done == 2:
            i = 0
            self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            while i < len(self.nao.hinge_joints):
                self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
                i = i + 1
    
    def test_frame(self):
        keyframe = testframe.keyframe
        name = testframe.name
        if self.progressed_time == 0 and self.keyframe_line == 0:
            self.get_joint_values(name)
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 1
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
        
    
    def get_new_joint_postion(self, keyframe, name):
        joint_number = 0
        while joint_number < len(self.last_joint_speed):
            joint_name = 1
            while joint_name < len(name):
                if name[joint_name] == self.nao.hinge_joints[joint_number].description:
                    #self.last_joint_speed[joint_number] = (keyframe[joint_name]-(self.nao.hinge_joints[joint_number].value)) / (keyframe[0] - self.progressed_time) * (self._default_time)
                    self.angle = keyframe[joint_name] - self.last_angle[joint_number]
                    if(self.nao.hinge_joints[joint_number].min > keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].min
                    if(self.nao.hinge_joints[joint_number].max < keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].max
                    self.angle = self._default_time * self.angle / (keyframe[0]-self.progressed_time)
                    self.last_angle[joint_number] = self.angle + self.last_angle[joint_number]
                    self.last_joint_speed[joint_number] = (math.radians(self.angle)/(self._default_time*0.001))
                    joint_number = joint_number + 1
                    break
                joint_name = joint_name + 1
        self.progressed_time = self.progressed_time + 20
        if (keyframe[0] - self.progressed_time) < self._default_time:                
            self.progressed_time = 0
            self.keyframe_line = self.keyframe_line + 1
            #self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
   
    def get_joint_values(self, name):
        joint_number = 0
        while joint_number < len(self.last_angle):
            joint_name = 1
            while joint_name < len(name):
                if name[joint_name] == self.nao.hinge_joints[joint_number].description:
                    self.last_angle[joint_number] = self.nao.hinge_joints[joint_number].value
                    joint_number = joint_number + 1
                    break
                joint_name = joint_name + 1
            
    def send(self, *params):
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))
   
   
        
