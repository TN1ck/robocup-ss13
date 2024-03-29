import world
import logging
import numpy
import copy

class HingeJoint:
    
    def __init__(self, description, perceptor, effector, min, max):
        self.description = description
        self.perceptor = perceptor
        self.effector = effector
        self.min = min
        self.max = max
        self.value = 0.0

class Nao:
    
    def __init__(self, world, player_nr):
        self.world = world
        self.player_nr = player_nr
        self.hinge_joints = []
        self.hinge_joints += [
            HingeJoint('Neck Yaw', 'hj1', 'he1', -120, 120), 
            HingeJoint('Neck Pitch', 'hj2', 'he2', -45, 120), 
            HingeJoint('Left Shoulder Pitch', 'laj1', 'lae1', -120, 120), 
            HingeJoint('Left Shoulder Yaw', 'laj2', 'lae2', -1, 95), 
            HingeJoint('Left Arm Roll', 'laj3', 'lae3', -120, 120), 
            HingeJoint('Left Arm Yaw', 'laj4', 'lae4', -90, 1), 
            HingeJoint('Left Hip YawPitch', 'llj1', 'lle1', -90, 1), 
            HingeJoint('Left Hip Roll', 'llj2', 'lle2', -25, 45), 
            HingeJoint('Left Hip Pitch', 'llj3', 'lle3', -25, 100), 
            HingeJoint('Left Knee Pitch', 'llj4', 'lle4', -130, 1), 
            HingeJoint('Left Foot Pitch', 'llj5', 'lle5', -45, 75), 
            HingeJoint('Left Foot Roll', 'llj6', 'lle6', -45, 25), 
            HingeJoint('Right Hip YawPitch', 'rlj1', 'rle1', -90, 1), 
            HingeJoint('Right Hip Roll', 'rlj2', 'rle2', -45, 25), 
            HingeJoint('Right Hip Pitch', 'rlj3', 'rle3', -25, 100), 
            HingeJoint('Right Knee Pitch', 'rlj4', 'rle4', -130, 1), 
            HingeJoint('Right Foot Pitch', 'rlj5', 'rle5', -45, 75), 
            HingeJoint('Right Foot Roll', 'rlj6', 'rle6', -25, 45), 
            HingeJoint('Right Shoulder Pitch', 'raj1', 'rae1', -120, 120), 
            HingeJoint('Right Shoulder Yaw', 'raj2', 'rae2', -95, 1), 
            HingeJoint('Right Arm Roll', 'raj3', 'rae3', -120, 120), 
            HingeJoint('Right Arm Yaw', 'raj4', 'rae4', -1, 90), 
        ]
        
        # some dictionaries:
        self.from_description = {}
        self.from_perceptor = {}
        self.from_effector = {}
        for joint in self.hinge_joints:
            self.from_description[joint.description] = joint
            self.from_perceptor[joint.perceptor] = joint
            self.from_effector[joint.effector] = joint

        # gyro:
        self._gyro_rate = numpy.array([0.0, 0.0, 0.0])
        self._gyro_state = numpy.array([0.0, 0.0, 0.0])

        self._accelerometer = numpy.array([0.0, 0.0, 0.0])
    
    def get_position(self):
        return self.world.get_entity_position('P_1_' + str(self.player_nr))

    def get_see_vector(self):
        return self.world.entity_from_identifier['P_1_' + str(self.player_nr)].get_see_vector()

    def set_gyro_rate(self, rate):
        """Sets the current gyro rate and adjusts the absolute gyro state with the new value."""
        self._gyro_rate = numpy.array(rate)
        self._gyro_state += (self._gyro_rate / 1000 * 20) # rate is in degrees/second. we want degrees/cycle.

    def get_gyro_rate(self):
        """Returns the gyro change rate as obtained from parser."""
        return copy.deepcopy(self._gyro_rate)

    def get_gyro_state(self):
        """Returns the absolute gyro orientation."""
        return copy.deepcopy(self._gyro_state)

    def get_accelerometer(self):
        """Returns the accelerometer as a 3-component numpy array."""
        return copy.deepcopy(self._accelerometer)

    def lies_on_front(self):
        if self._accelerometer[1] < -9:
            return 1
        else:
            return 0

    def lies_on_back(self):
        if self._accelerometer[1] > 9:
            return 1
        else:
            return 0
    """
    def update_joint_positions(self, parsed):
        '''Updates all currently perceived joints of the nao.'''
        joint_number = 0
        for i in parsed:
            if i[0] == 'HJ':
                for j in self.hinge_joints:
                    if i[1][1] == j.perceptor:
                        j.value = i[2][1]
                        joint_number = joint_number +1
                        break
    """
