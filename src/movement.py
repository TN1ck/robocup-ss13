from math import sin, cos, acos, atan2, degrees, pi, pow, sqrt, tan

class Movement:
    def __init__(self, world, socket, player_nr):
        self.world = world
        self.socket = socket
        self.player_nr = player_nr
        #self.team = team
        self.velocity = 0.1
        self.divergence = 0.1
        self.stopped = True
        self.destination = None
        self.angular_precision = 0.5;
        self.rotation = 0
        self.position = self.world.entity_from_identifier['P_1_' + str(self.player_nr)].get_position()
        self.beampos = self.position

    def get_world(self):
        return self.world

    def send(self, *params):
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))

    def run(self, *destination):
        #print destination[0]
        #print destination[1]
        self.position = self.beampos
        #print self.position.x
	#print self.position.y
        self.stopped = False
        if destination: self.destination = destination
        # Destination parameters are present in parameters
        #if destination:
        #    self.destination = destination
        #if ((self.destination and
        #    abs(self.destination[0] - self.position.x) < self.divergence) and
        #   (abs(self.destination[1] - self.position.y) < self.divergence)):
        #    self.stopped = True
        #    return

        self.rotation = atan2(self.destination[0] - self.beampos.x, self.destination[1] - self.beampos.y)
        #print self.rotation
        #print degrees(self.rotation)
        #print sin(self.rotation)
        #print cos(self.rotation)
        dy = cos(self.rotation) * self.velocity
        dx = sin(self.rotation) * self.velocity

        if(abs(self.beampos.x - self.position.x) < self.divergence):
            self.beampos.x = self.beampos.x + dx
        else:
            self.beampos.x = self.position.x + dx

        if(abs(self.beampos.y - self.position.y) < self.divergence):
            self.beampos.y = self.beampos.y + dy
        else:
            self.beampos.y = self.position.y + dy

        #self.send("agent (unum", self.player_nr, ") (team", self.team, ") (move", self.beampos.x, self.beampos.y, "100",(-1 * degrees(self.rotation) )+90, ")")
        #self.socket.flush()
        #self.socket.receive()
        self.send("beam", self.beampos.x, self.beampos.y, (-1 * degrees(self.rotation) )+90)


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

    #def update(self):
    #    if not self.stopped:
    #        self.run()
