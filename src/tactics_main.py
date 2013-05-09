#/usr/bin/env python2.7

from world import Vector

class TacticsMain:

  def __init__(self, world, movement):
    self.world = world
    self.mov = movement

  def update(self):

    pos = Vector(5,5)

    self.mov.run(pos)
