import Keyframes as kf


class Keyframe_Engine:
    
    def __init__(self):
        self.joint_position = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.progressed_time = 0
        self.keyframe_line = 0
        self._default_time = 20
 
    def get_joint_position(self, parsed):
        joint_number = 0
        for i in parsed:
            if i[0] == 'HJ':
                value = float(i[2].split(' ', 1 )[1])
                self.joint_position[joint_number] = value
                joint_number = joint_number +1
    
    
    def stand_up_from_back(self, parsed):
        keyframe = kf.stand_up_from_back.keyframe
        self.get_joint_position(parsed)
        self.get_new_joint_postion(keyframe[self.keyframe_line])
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
    
    def get_new_joint_postion(self, keyframe):   
        for joint_number in self.joint_position:
            self.joint_position[joint_number] = (keyframe[joint_number+1]-self.joint_positions[joint_number]) / (keyframe[0] - self.progressed_time) * self._default_time
        self.progressed_time = self.progressed_time + 20
        if (keyframe[0] - self.progressed_time) < self._default_time:                
            self.progressed_time = 0
            self.keyframe_line = self.keyframe_line + 1
            
            
        