#!/usr/bin/env python2.7

import unittest
from ..src import parser3

# We subclass TestCase to create our own TestClass
class ParserTest(unittest.TestCase):

  # We set-up everything we need for the test, setUp() and tearDown() are called between every test
  def setUp(self):
    self.easy_se = """(see (pol 3.4 8.3 3.9))"""
    self.medium_se = """(will paste later)"""
    self.hard_se = """((FieldLength 18)(FieldWidth 12)(FieldHeight 40)
                            (GoalWidth 2.1)(GoalDepth 0.6)(GoalHeight 0.8)
                            (FreeKickDistance 1.3)(WaitBeforeKickOff 2)
                            (AgentRadius 0.4)(BallRadius 0.042)(BallMass 0.026)
                            (RuleGoalPauseTime 3)(RuleKickInPauseTime 1)(RuleHalfTime 300)
                            (play_modes BeforeKickOff KickOff_Left KickOff_Right PlayOn
                                        KickIn_Left KickIn_Right corner_kick_left corner_kick_right
                                        goal_kick_left goal_kick_right offside_left offside_right
                                        GameOver Goal_Left Goal_Right free_kick_left free_kick_right))"""
    self.sub_case_1 = """(((((number 4.456)))))"""
    # This is NOT a s-expression, but the server will send it
    self.sub_case_2 = """(one)(two)(three)"""
    self.sub_case_3 = """((())((one)))"""

    self.easy_se_exp = ['see', ['pol', 3.4, 8.3, 3.9]]
    self.medium_se_exp = ['will', 'paste', 'later']
    self.hard_se_exp = [['FieldLength', 18], ['FieldWidth', 12], ['FieldHeight', 40],
                   ['GoalWidth', 2.1], ['GoalDepth', 0.6], ['GoalHeight', 0.8],
                   ['FreeKickDistance', 1.3], ['WaitBeforeKickOff', 2], ['AgentRadius', 0.4],
                   ['BallRadius', 0.042], ['BallMass', 0.026], ['RuleGoalPauseTime', 3],
                   ['RuleKickInPauseTime', 1], ['RuleHalfTime', 300],
                   ['play_modes', 'BeforeKickOff', 'KickOff_Left',
                    'KickOff_Right', 'PlayOn', 'KickIn_Left', 'KickIn_Right',
                    'corner_kick_left', 'corner_kick_right', 'goal_kick_left',
                    'goal_kick_right', 'offside_left', 'offside_right',
                    'GameOver', 'Goal_Left', 'Goal_Right', 'free_kick_left', 'free_kick_right']]
    self.sub_case_1_exp = [[[[['number', 4.456]]]]]
    self.sub_case_2_exp = [['one'], ['two'],['three']]
    self.sub_case_3_exp = [[[]], [['one']]]

  def test_easy(self):
    print("\nIn test easy, testing the expression: \n" + parser3.print_sexp(self.easy_se))
    self.assertEqual(self.easy_se_exp, parser3.parse_sexp(self.easy_se))

  def test_medium(self):
    print("\nIn test medium, testing the expression: \n" + parser3.print_sexp(self.medium_se))
    self.assertEqual(self.medium_se_exp, parser3.parse_sexp(self.medium_se))

  def test_hard(self):
    print("\nIn test hard, testing the expression: \n" + parser3.print_sexp(self.hard_se).replace(" ",""))
    self.assertEqual(self.hard_se_exp, parser3.parse_sexp(self.hard_se))


if __name__ == '__main__':
  unittest.main()