from math import sin, cos, acos


class Movement:

    def __init__(self, world, socket):
        self.world = world
        self.socket = socket
        self.velocity = 10
        self.divergence = 10
        self.stopped = True
        self.destination = None
        self.angular_precision = 0.5;

    def get_world(self):
        return world

    def send(self, *params):
        self.socket.send(" ".join(map(str, ["("] + params + [")"])))

    def run(self, *destination):
        self.stopped = False
        player = self.world.get_own_player()
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

    def turn_head(self, horizontal, vertical, speed):
        self.turn_head_horizontal(horizontal, speed)
        self.turn_head_vertical(vertical, speed)

    def turn_head_horizontal(self, angle, speed):
        # if self.stopped:
        #     if (angle - hj) > self.angular_precision: # how do we get the hj1 value?
        #         self.send("he1", speed)
        #         turn_head_horizontal(self, angle, speed)
        #     if (hj - angle) > self.angular_precision:
        #         self.send("he1", 0 - speed)
        #         turn_head_horizontal(self, angle, speed)
        #     self.send("he1", 0)
            


    def turn_head_vertical(self, angle, speed):
        # analogous to turn_head_horizontal() with hj2 and he2

    def delete_destination(self):
        self.destination = None

    def update(self):
        if not self.stopped:
            self.run(self)
