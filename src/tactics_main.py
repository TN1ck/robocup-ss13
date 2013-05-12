#/usr/bin/env python2.7

from world import Vector

class TacticsMain:

  def __init__(self, world, movement):
    self.world = world
    self.mov = movement

  def run_tactics(self):
    pass

    # The tactics module calculates our tactics
    # and calls other modules like movement, and these modules
    # then send commands via network to the server.

    # pos = Vector(5,5)

    # # The run method doesn't work yet...
    # self.mov.run(pos)
