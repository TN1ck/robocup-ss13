import Keyframes as kf


class Keyframe_Engine:
    
    def __init__(self, nao, socket):
        self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.progressed_time = 0
        self.keyframe_line = 0
        self._default_time = 20
        self.nao = nao
        self.socket = socket
 
#    def get_joint_position(self, parsed):
#        joint_number = 0
#        for i in parsed:
#            if i[0] == 'HJ':
#                value = float(i[2].split(' ', 1 )[1])
#                self.joint_position[joint_number] = value
#                joint_number = joint_number +1
    
    
    def stand_up_from_back(self):
        keyframe = kf.stand_up_from_back.keyframe
        self.get_new_joint_postion(keyframe[self.keyframe_line])
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
        self.send()
    
    def get_new_joint_postion(self, keyframe):   
        for joint_number in self.last_joint_speed:
            self.last_joint_speed[joint_number] = (keyframe[joint_number+1]-(self.nao.hinge_joints[joint_number].value + self.last_joint_speed[joint_number] * self._default_time)) / (keyframe[0] - self.progressed_time) * self._default_time
        self.progressed_time = self.progressed_time + 20
        if (keyframe[0] - self.progressed_time) < self._default_time:                
            self.progressed_time = 0
            self.keyframe_line = self.keyframe_line + 1
            
    def send(self):
        print 'h'
            
        