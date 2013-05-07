from math import sin, cos


class Movement:

    def __init__(self, world, socket):
        self.world = world
        self.socket = socket
        self.velocity = 0
        self.stepsize = 0.1

    def run(self, velocity):
        self.velocity = velocity
        player = self.world.get_player
        dy = sin(player.rot) * self.stepsize * self.velocity
        dx = cos(player.rot) * self.stepsize * self.velocity
        self.socket.send(" ".join(map(str, ["(beam",
                                            player.pos.x + dx,
                                            player.pos.y + dy, player.rot, ")"]
                                      )))
        self.world.player.pos.x = player.pos.x + dx
        self.world.player.pos.y = player.pos.y + dy

    def update(self):
        self.run(self, self.velocity)
