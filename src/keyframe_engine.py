from Keyframes import stand_up_from_back


class Keyframe_Engine:
    
    def __init__(self, nao, socket):
        self.last_joint_speed = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.progressed_time = 0
        self.keyframe_line = 0
        self._default_time = 20
        self.nao = nao
        self.socket = socket
        self.fall = True
 
#    def get_joint_position(self, parsed):
#        joint_number = 0
#        for i in parsed:
#            if i[0] == 'HJ':
#                value = float(i[2].split(' ', 1 )[1])
#                self.joint_position[joint_number] = value
#                joint_number = joint_number +1

    def fall_on_front(self):
        while(self.fall):
		    self.socket.enqueue("(rle5 2.0)")
		    self.socket.flush()
		    self.fall = False
    
    def fall_on_back(self):
	    while(self.fall):
		    self.socket.enqueue("(rle5 -2.0)")
		    self.socket.flush()
		    self.fall = False
    
    
    def stand_up_from_back(self):
        keyframe = stand_up_from_back.keyframe
        name = stand_up_from_back.name
        self.get_new_joint_postion(keyframe[self.keyframe_line], name)
        if self.keyframe_line >= len(keyframe): # alt: 6
            self.keyframe_line = 0
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
                    self.last_joint_speed[joint_number] = (keyframe[joint_name]-(self.nao.hinge_joints[joint_number].value + self.last_joint_speed[joint_number] * self._default_time)) / (keyframe[0] - self.progressed_time) * self._default_time
                    joint_number = joint_number + 1
                    break
                joint_name = joint_name + 1
        self.progressed_time = self.progressed_time + 20
        if (keyframe[0] - self.progressed_time) < self._default_time:                
            self.progressed_time = 0
            self.keyframe_line = self.keyframe_line + 1
            
    def send(self, *params):
        self.socket.send(" ".join(map(str, ["("] + list(params) + [")"])))
   
   
        
