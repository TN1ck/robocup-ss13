from math import sin, cos, acos


class Movement:

    def __init__(self, world, socket):
        self.world = world
        self.socket = socket
        self.velocity = 10
        self.divergence = 10
        self.stopped = True
        self.destination = None

    def send(self, *params):
        self.socket.send(" ".join(map(str, ["("] + params + [")"])))

    def run(self, *destination):
        self.stopped = False
        player = self.world.get_player
        # Destination parameters are present in parameters
        if destination:
            player.rot = acos(abs(player.pos.x - self.destination[0]) / abs(player.pos.y - self.destination[1]))
            self.destination = destination
                # Did we reach our destination?
        if ((self.destination and
            abs(self.destination[0] - player.pos.x) < self.divergence) and
           (abs(self.destination[1] - player.pos.y) < self.divergence)):
            self.stopped = True
            return
        dy = sin(player.rot) * self.velocity
        dx = cos(player.rot) * self.velocity
        self.send("beam", player.pos.x + dx, player.pos.y + dy, player.rot)
        self.world.player.pos.x = player.pos.x + dx
        self.world.player.pos.y = player.pos.y + dy

    def stop(self):
        self.stopped = True

    def delete_destination(self):
        self.destination = None

    def update(self):
        if not self.stopped:
            self.run(self)
