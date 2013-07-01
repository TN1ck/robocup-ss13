import Keyframes as kf
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
        self.fall = False       # Variable that determines if a fall function has been called, NOT the true position
        self.angle = 0.0
        self.working = False    # For tactics, if TRUE start keep_going
        self.last = 0
        self.last_frame = None  # Last keyframe
        self.head_working = False
        self.head_frame = None
        self.head_line = 0
        self.head_time = 0
        self.head_last = 0
        self.head_stop = False


    def work(self):
        '''
        Runs the actual keyframes, has to be called at end of tactics!
        '''
        if self.working:
            keyframe = self.last_frame.keyframe
            name = self.last_frame.name
            self.next_step(keyframe, name)

        if self.head_working:
            keyframe = self.head_frame
            name = kf.lookAround.name
            self.next_head_step(keyframe, name)

    def parry_right(self):
        self.last_frame = kf.parry_right_1
        self.working = True

    def parry_left(self):
        self.last_frame = kf.parry_left_1
        self.working = True

    def kick_strong(self):
        self.last_frame = kf.kick_strong
        self.working = True

    def fall_on_front(self):
        '''
        Testfunction to let the Nao fall on its front
        '''
        self.last_frame = kf.fall_front
        self.fall = True
        self.working = True

    def fall_on_back(self):
        '''
        Testfunction to let the Nao fall on its back
        '''
        self.last_frame = kf.fall_back
        self.fall = True
        self.working = True

    def stand(self):
        '''
        Stand position of the NAO
        '''
        self.last_frame = kf.stand
        self.working = True

    def stand_up_from_back(self):
        '''
        Stand_up-function from back
        '''
        self.last_frame = kf.stand_up_from_back
        self.working = True
        self.fall = False

    def stand_up_from_front(self):
        '''
        Stand_up-function from front
        '''
        self.last_frame = kf.stand_up_from_front
        self.working = True
        self.fall = False

    def head_lookAround(self):
        '''
        funktion for look around
        '''
        self.head_frame = kf.lookAround.keyframe
        self.head_working = True

    def kick1(self):
        '''
        first kick-function
        the ball has to lay in front of the nao
        '''
        self.last_frame = kf.kick1
        self.working = True

    def test_frame(self):
        '''
        Testfunction that moves all  joints
        '''
        self.last_frame = kf.testframe
        self.working = True

    def head_move(self, angle):
        '''
        Function to move the head horizontal to the given angle.
        '''
        self.head_frame = [[math.fabs(angle)*10, 0.0, angle]]
        if angle == 0:
            self.head_frame = [[400, 0.0, angle]]
        self.head_working = True

    def stop_head(self):
        '''
        Stops the head movement at the actual position. Not yet finished.
        '''
        self.head_stop = True


    def head_reset(self):
        '''
        Resets the head to 0-Position. Not yet finished.
        '''
        self.head_frame = [[500, 0, 0]]
        self.head_working = True

    def next_step(self, keyframe, name):
        '''
        calculates the next joints speed and sends them to the socket

        self.last == 1, if the keyframe is finished
        self.last == 0, if the keyframe is not finished
        '''
        if self.last == 1:
            #the keyframe is finished and does not repeat
            #perhaps important for the communication with the tactics group
            i = 0
            if self.head_working:
                i = 2
            while i < len(self.last_joint_speed):
                self.last_joint_speed[i] = 0.0
                self.last_joint_angle[i] = 0.0
                i = i + 1
            self.last_frame = None
            self.working = False
            self.last = 2

        if self.last == 0:
            self.get_new_joint_postion(keyframe[self.keyframe_line], name)
            if self.keyframe_line >= len(keyframe):
                self.keyframe_line = 0
                self.last = 1
        i = 0
        if self.head_working:
            i = 2
        while i < len(self.nao.hinge_joints):
            self.send(self.nao.hinge_joints[i].effector, self.last_joint_speed[i])
            i = i + 1
        if self.last == 2:
            self.last = 0

    def next_head_step(self, keyframe, name):
        '''
        calculates the next head joints speed and sends them to the socket
        '''
        if self.head_last == 1 or self.head_stop:
            self.last_joint_speed[0] = 0.0
            self.last_joint_speed[1] = 0.0
            self.last_joint_angle[0] = 0.0
            self.last_joint_angle[1] = 0.0
            self.head_frame = None
            self.head_working = False
            self.head_stop = False
            self.head_last = 2

        if self.head_last == 0:
            self.get_new_head_position(keyframe[self.head_line], name)
            if self.head_line >= len(keyframe):
                self.head_line = 0
                self.head_last = 1
        self.send(self.nao.hinge_joints[0].effector, self.last_joint_speed[0])
        self.send(self.nao.hinge_joints[1].effector, self.last_joint_speed[1])
        if self.head_last == 2:
            self.head_last = 0

    def get_new_head_position(self, keyframe, name):
        '''
        Calculate the new head speed in rad/sec
        '''
        joint_number = 0
        while joint_number < 2:
            joint_name = 1
            while joint_name < len(name):
                if name[joint_name] == self.nao.hinge_joints[joint_number].description:
                    self.angle = keyframe[joint_name] - (self.nao.hinge_joints[joint_number].value + self.last_joint_angle[joint_number])
                    if(self.nao.hinge_joints[joint_number].min > keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].min
                    if(self.nao.hinge_joints[joint_number].max < keyframe[joint_name]):
                        self.angle = self.nao.hinge_joints[joint_number].max
                    self.angle = self._default_time * self.angle / (keyframe[0]-self.head_time)
                    self.last_joint_angle[joint_number] = self.angle
                    self.last_joint_speed[joint_number] = (math.radians(self.angle)/(self._default_time*0.001))
                    joint_number = joint_number + 1
                    break
                joint_name = joint_name + 1
        self.head_time = self.head_time + 20
        if (keyframe[0] - self.head_time) < self._default_time:
            self.head_time = 0
            self.head_line = self.head_line + 1

    def get_new_joint_postion(self, keyframe, name):
        '''
        Function to calculate the new speed in rad/sec
        '''
        joint_number = 0
        if self.head_working:
            joint_number = 2
        while joint_number < len(self.last_joint_speed):
            joint_name = 1
            while joint_name < len(name):
                if name[joint_name] == self.nao.hinge_joints[joint_number].description:
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

    def send(self, *params):
        '''
        Enqueue the new joint speeds
        '''
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))



