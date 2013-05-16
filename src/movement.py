from math import sin, cos, acos, atan, degrees, pi, pow, sqrt
import time

class Movement:

    def __init__(self, world, socket, player_nr):
        self.world = world
        self.socket = socket
        self.player_nr = player_nr
        self.velocity = 0.1
        self.divergence = 1
        self.stopped = True
        self.destination = None
        self.angular_precision = 0.5;
        self.rotation = 0

    def get_world(self):
        return self.world

    def send(self, *params):
        self.socket.send(" ".join(map(str, ["("] + params + [")"])))

    def run(self, *destination):
        self.stopped = False
        position = self.world.entity_from_identifier['P' + str(self.player_nr)].get_position()
        # Destination parameters are present in parameters
        if destination:
            self.destination = destination
            self.rotation = acos((self.destination[0] - position.x) / sqrt(pow((self.destination[0] - position.x), 2) + pow((self.destination[1] - position.y), 2))) + pi
        if ((self.destination and
            abs(self.destination[0] - position.x) < self.divergence) and
           (abs(self.destination[1] - position.y) < self.divergence)):
            self.stopped = True
            return
        dy = sin(self.rotation) * self.velocity
        dx = cos(self.rotation) * self.velocity
        #trigonometry crash workaround: change 'self.rotation' to '0' in the following function
	self.socket.send("(beam "+ str(position.x + dx) + " " + str(position.y + dy) + " " + str(degrees(self.rotation)) + ")")
        #self.send("beam", position.x + dx, position.y + dy, self.rotation)
        #self.world.player.pos.x = player.pos.x + dx
        #self.world.player.pos.y = player.pos.y + dy

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
        self.send("he1", 0)
            
    def turn_head_vertical(self, angle, speed):
        # analogous to turn_head_horizontal() with hj2 and he2
        self.send("he2", 0)

    def delete_destination(self):
        self.destination = None

    def update(self):
        if not self.stopped:
            self.run()
