from Keyframes import stand_up_from_back, testframe, fall_back, fall_front, stand_up_from_front
import math

class Keyframe_Engine:
    
    def __init__(self, nao, socket):
        self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.last_joint_angle = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.progressed_time = 0
        self.keyframe_line = 0
        self._default_time = 20.0
        self.nao = nao
        self.socket = socket
        self.fall = True
        self.angle = 0.0
        self.done = 0
        self.last = 0
        self.last2 = 0
        
    
    
    def fall_on_front(self):
        '''
        Testfunction to let the Nao fall on its front
        '''
        keyframe = fall_front.keyframe
        name = stand_up_from_back.name
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 1
            self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            self.last_joint_angle = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
    
    def fall_on_back(self):
        '''
        Testfunction to let the Nao fall on its back
        '''
        keyframe = fall_back.keyframe
        name = stand_up_from_back.name
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 1
            self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            self.last_joint_angle = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
    
    def stand_up_from_back(self):
        '''
        Stand_up-function from back
        '''
        keyframe = stand_up_from_back.keyframe
        name = stand_up_from_back.name
        self.next_step(keyframe, name)
               
    def stand_up_from_front(self):
        '''
        Stand_up-function from front
        '''
        keyframe = stand_up_from_front.keyframe
        name = stand_up_from_front.name
        self.next_step(keyframe, name)
    
    def test_frame(self):
        '''
        Testfunction that moves all  joints
        '''
        keyframe = testframe.keyframe
        name = testframe.name
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
            self.done = 1
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
            
    def next_step(self, keyframe, name):
        '''
        calculates the next joints speed and sends them to the socket
        
        self.last == 1, if the keyframe is finished
        self.last == 0, if the keyframe is not finished
        '''
        if self.last == 1:
            self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            self.last_joint_angle = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            #the keyframe is finished and does not repeat
            #perhaps important for the communication with the tactics group
            self.done = 2
            self.last2 = 1

        if self.last == 0:
            self.get_new_joint_postion(keyframe[self.keyframe_line], name)
            if self.keyframe_line >= len(keyframe): # alt: 6
                self.keyframe_line = 0
                self.last = 1
        i = 0
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
        if self.last2 == 1:
            self.last = 0        
    
    def get_new_joint_postion(self, keyframe, name):
        '''    
        Function to calculate the new speed in rad/sec
        '''
        joint_number = 0
        while joint_number < len(self.last_joint_speed):
            joint_name = 1
            while joint_name < len(name):
                if name[joint_name] == self.nao.hinge_joints[joint_number].description:
                    #self.last_joint_speed[joint_number] = (keyframe[joint_name]-(self.nao.hinge_joints[joint_number].value)) / (keyframe[0] - self.progressed_time) * (self._default_time)
                    self.angle = keyframe[joint_name] - (self.nao.hinge_joints[joint_number].value + self.last_joint_angle[joint_number])
                    if(self.nao.hinge_joints[joint_number].min > keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].min
                    if(self.nao.hinge_joints[joint_number].max < keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].max
                    self.angle = self._default_time * self.angle / (keyframe[0]-self.progressed_time)
                    self.last_joint_angle[joint_number] = self.angle
                    self.last_joint_speed[joint_number] = (math.radians(self.angle)/(self._default_time*0.001))
                    joint_number = joint_number + 1
                    break
                joint_name = joint_name + 1
        self.progressed_time = self.progressed_time + 20
        if (keyframe[0] - self.progressed_time) < self._default_time:                
            self.progressed_time = 0
            self.keyframe_line = self.keyframe_line + 1
            #self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
   
            
    def send(self, *params):
        '''
        Enqueue the new joint speeds
        '''
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))
   
   
        
