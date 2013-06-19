#!/usr/bin/env python2.7

import unittest
import numpy
from ..src.scene import Scene
from ..src.SceneGraph  import trans_node
from ..src.SceneGraph  import light_node
from ..src.SceneGraph import smn_node
from ..src.SceneGraph import tree_node


class Scenegraph_Test(unittest.TestCase):

    def setUp(self):
        self.message_example1 = [[['FieldLength', 30], ['FieldWidth', 20], ['FieldHeight', 40], ['GoalWidth', 2.1], ['GoalDepth', 0.6], ['GoalHeight', 0.8], ['BorderSize', 0], ['FreeKickDistance', 2], ['WaitBeforeKickOff', 30], 
                                             ['AgentRadius', 0.4], ['BallRadius', 0.042], ['BallMass', 0.026], ['RuleGoalPauseTime', 3], ['RuleKickInPauseTime', 1], ['RuleHalfTime', 300], 
                                             ['play_modes', 'BeforeKickOff', 'KickOff_Left', 'KickOff_Right', 'PlayOn', 'KickIn_Left', 'KickIn_Right', 'corner_kick_left', 'corner_kick_right', 'goal_kick_left', 'goal_kick_right', 'offside_left', 'offside_right', 'GameOver', 'Goal_Left', 'Goal_Right', 'free_kick_left', 'free_kick_right'], 
                                             ['time', 0], ['half', 1], ['score_left', 0], ['score_right', 0], ['play_mode', 0]], 
                                ['RSG', 0, 1],
                                # trfNode1
                                [['nd', 'TRF', ['SLT', 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -10, 10, 10, 1], 
                                             # lightNode1
                                             ['nd', 'Light', ['setDiffuse', 1, 1, 1, 1], ['setAmbient', 0.8, 0.8, 0.8, 1], ['setSpecular', 0.1, 0.1, 0.1, 1]]], 
                                # trfNode2
                                ['nd', 'TRF', ['SLT', 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, -10, 10, 1], 
                                             #trfNode2_2
                                             ['nd', 'TRF', ['SLT', 1, 0, 0, 0, 0, 1, 0, 0, 0, 20, 1, 0, 10, -10, 10, 1],
                                                     # lightNode2
                                                     ['nd', 'Light', ['setDiffuse', 2, 2, 2, 2], ['setAmbient', 1, 5, 3, 1], ['setSpecular', 1, 0, 11, 21]],
                                                     # smnNode1 
                                                     ['nd', 'SMN', ['setVisible', 1], ['load', 'StdUnitBox'], ['sSc', 50.98, 1, 1], ['sMat', 'matGrey']]]],
                                # trfNode3
                                ['nd', 'TRF', ['SLT', -1, -8.74228e-08, -3.82137e-15, 0, 0, -4.37114e-08, 1, 0, -8.74228e-08, 1, 4.37114e-08, 0, 0, 0, 0, 1], 
                                             # staticMesh1
                                             ['nd', 'StaticMesh', ['setVisible', 1], ['load', 'models/naosoccerfield.obj'], ['sSc', 2.5, 1, 2.5], ['resetMaterials', 'None_rcs-naofield.png']],
                                             # staticMesh2
                                             ['nd', 'StaticMesh', ['setVisible', 1], ['load', 'models/rshank.obj'], ['sSc', 0.08, 0.08, 0.08], ['resetMaterials', 'matTeam', 'naoblack', 'naowhite']]]]]
       

        self.message_update1 = [[['time', 0]], 
                                ['RDS', 0, 1],
                                # trfNode1_update
                                [['nd',  'TRF', ['SLT', 1, 0, 0, 0, 0, 1, 0, 300, 0, 0, 1, 0, 100, -10, 10, 1],
                                             ['nd']], 
                                # trfNode2_update
                                ['nd', 'TRF', ['SLT', 1, 200, 0, 0, 0, 1, 0, 300, 0, 0, 1, 90, 100, -10, 10, 1],
                                             # trfNode2_1_update
                                             ['nd','TRF', ['SLT', 1, 0, 0, 400, 0, 1, 0, 300, 20, 0, 1, 0, 100, -10, 10, 1],
                                                     ['nd'],
                                                     ['nd', 'SMN']]],
                                # trfNode3_update
                                ['nd', 'TRF', ['SLT', 1000, 99, 0, 0, 0, 1, 0, 300, 0, 0, 1, 2, 100, -10, 10, 1],
                                             ['nd', 'StaticMesh'],
                                             ['nd', 'StaticMesh']]]]


        # trfNode1
        self.trfNode1_matrix = numpy.array( ((1,0,0,-10), (0,1,0,10), (0,0,1,10), (0,0,0,1)) )
        # lightNode1
        self.lightNode1_diffuse = numpy.array((1,1,1,1))
        self.lightNode1_ambient = numpy.array((0.8, 0.8, 0.8, 1))
        self.lightNode1_specular = numpy.array((0.1, 0.1, 0.1, 1))
        # trfNode2
        self.trfNode2_matrix = numpy.array(  ((1,0,0,10), (0,1,0,-10), (0,0,1,10), (0,0,0,1)) )
        # trfNode2_1
        self.trfNode2_1_matrix = numpy.array( ( (1,0,0,10), (0,1,20,-10), (0,0,1,10), (0,0,0,1)) )
        # lightNode2 
        self.lightNode2_diffuse = numpy.array((2, 2, 2, 2))
        self.lightNode2_ambient = numpy.array((1, 5, 3, 1))
        self.lightNode2_specular = numpy.array((1, 0, 11, 21))
        # smnNode1
        self.smnNode1_setVisible = 1
        self.smnNode1_load = ['StdUnitBox']
        self.smnNode1_sSc = [50.98, 1, 1]
        self.smnNode1_sMat = 'matGrey'
        # trfNode3
        self.trfNode3_matrix = (((-1,0,-8.74228e-08,0),(-8.74228e-08,-4.37114e-08,1,0),(-3.82137e-15,1,4.37114e-08,0),(0,0,0,1)))
        # staticMesh1
        self.staticMesh1_load = 'models/naosoccerfield.obj'
        self.staticMesh1_sSc = [2.5, 1, 2.5]
        self.staticMesh1_reset = ['None_rcs-naofield.png']
        self.staticMesh1_visible = 1
        # staticMesh2
        self.staticMesh2_load = 'models/rshank.obj'
        self.staticMesh2_sSc = [0.08, 0.08, 0.08]
        self.staticMesh2_reset = ['matTeam', 'naoblack', 'naowhite']
        self.staticMesh2_visible = 1


        # trfNode1_update
        self.trfNode1_update_matrix = numpy.array(  ((1,0,0,100), (0,1,0,-10), (0,0,1,10), (0,300,0,1)) )
        # trfNode2_update
        self.trfNode2_update_matrix = numpy.array(  ((1,0,0,100), (200,1,0,-10), (0,0,1,10), (0,300,90,1)) )
        # trfNode2_1_update
        self.trfNode2_1_update_matrix = numpy.array(  ((1,0,20,100), (0,1,0,-10), (0,0,1,10), (400,300,0,1)) )
        # trfNode3_update
        self.trfNode3_update_matrix = numpy.array(  ((1000,0,0,100), (99,1,0,-10), (0,0,1,10), (0,300,2,1)) )


    def testScene1(self):
        scene = Scene.Instance()
        scene.create_scene(self.message_example1)
        # trfNode1
        self.assertTrue(numpy.array_equal(self.trfNode1_matrix, scene.find_node(1).get_matrix()))
        # lightNode1
        self.assertTrue(numpy.array_equal(self.lightNode1_diffuse, scene.find_node(2).get_diffuse()))
        self.assertTrue(numpy.array_equal(self.lightNode1_ambient, scene.find_node(2).get_ambient()))
        self.assertTrue(numpy.array_equal(self.lightNode1_specular, scene.find_node(2).get_specular()))
        # trfNode2
        self.assertTrue(numpy.array_equal(self.trfNode2_matrix, scene.find_node(3).get_matrix()))
        # trfNode2_1
        self.assertTrue(numpy.array_equal(self.trfNode2_1_matrix, scene.find_node(4).get_matrix()))
        # lightNode2 
        self.assertTrue(numpy.array_equal(self.lightNode2_diffuse, scene.find_node(5).get_diffuse()))
        self.assertTrue(numpy.array_equal(self.lightNode2_ambient, scene.find_node(5).get_ambient()))
        self.assertTrue(numpy.array_equal(self.lightNode2_specular, scene.find_node(5).get_specular()))
        # smnNode1
        self.assertEqual(self.smnNode1_setVisible, scene.find_node(6).get_visible())
        self.assertEqual(self.smnNode1_load, scene.find_node(6).get_load())
        self.assertEqual(self.smnNode1_sSc, scene.find_node(6).get_sSc())
        self.assertEqual(self.smnNode1_sMat, scene.find_node(6).get_material())
        # trfNode3
        self.assertTrue(numpy.array_equal(self.trfNode3_matrix, scene.find_node(7).get_matrix()))
        # staticMesh1
        self.assertEqual(self.staticMesh1_visible, scene.find_node(8).get_visible())
        self.assertEqual(self.staticMesh1_load, scene.find_node(8).get_load())
        self.assertEqual(self.staticMesh1_sSc, scene.find_node(8).get_sSc())
        self.assertEqual(self.staticMesh1_reset, scene.find_node(8).get_reset())
        # staticMesh2
        self.assertEqual(self.staticMesh2_visible, scene.find_node(9).get_visible())
        self.assertEqual(self.staticMesh2_load, scene.find_node(9).get_load())
        self.assertEqual(self.staticMesh2_sSc, scene.find_node(9).get_sSc())
        self.assertEqual(self.staticMesh2_reset, scene.find_node(9).get_reset())


    def testScene_update1(self):
        scene = Scene.Instance()
        scene.create_scene(self.message_example1)
        scene.update_scene(self.message_update1)
        # trfNode1_update
        self.assertTrue(numpy.array_equal(self.trfNode1_update_matrix, scene.find_node(1).get_matrix()))
        # trfNode2_update
        self.assertTrue(numpy.array_equal(self.trfNode2_update_matrix, scene.find_node(3).get_matrix()))
        # trfNode2_1_update
        self.assertTrue(numpy.array_equal(self.trfNode2_1_update_matrix, scene.find_node(4).get_matrix()))
        # trfNode3_update
        self.assertTrue(numpy.array_equal(self.trfNode3_update_matrix, scene.find_node(7).get_matrix()))

if __name__ == '__main__':
  unittest.main()
        
