from math import *

class Movement:
    def __init__(self, world, socket, player_nr):
        self.world = world
        self.socket = socket
        self.player_nr = player_nr
        #self.team = team
        self.velocity = 0.02
        self.divergence = 0.27
        self.stopped = True
        self.destination = None
        self.angular_precision = 0.1;
        self.rotation = 0
        self.position = self.world.entity_from_identifier['P_1_' + str(self.player_nr)].get_position()
        self.beampos = self.position
        self.shoot_distance = hypot(-0.2, 0.05)
        self.shoot_angle_offset = atan2(-0.2, 0.05)
        self.fresh = True
        self.reached_position = False

    def get_world(self):
        return self.world

    def send(self, *params):
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))

    def run(self, *destination):
       # print destination[0]
        #print destination[1]
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False
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

        #if(abs(self.beampos.x - self.position.x) < self.divergence):
        self.beampos.x = self.beampos.x + dx
        #else:
        #    self.beampos.x = self.position.x + dx

        #if(abs(self.beampos.y - self.position.y) < self.divergence):
        self.beampos.y = self.beampos.y + dy
        #else:
        #    self.beampos.y = self.position.y + dy

        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384",(-1 * degrees(self.rotation) ), ")")
        #self.socket.flush()
        #self.socket.receive()
        #self.send("beam", self.beampos.x, self.beampos.y, (-1 * degrees(self.rotation) )+90)

    def turn(self, angle):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False
        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384", angle, ")")
        
    def run_to_shoot_position(self, *destination):
        print "lol2"
        self.position = self.world.get_entity_position('P_1_' + str(self.player_nr))
        ballposition = self.world.ball.get_position()
        a = atan2(destination[0] - ballposition.x, destination[1] - ballposition.y)
        if (hypot(ballposition.x - self.position.x, ballposition.y - self.position.y) > self.divergence):
            self.reached_position = False
            self.run(ballposition.x + (sin(a + self.shoot_angle_offset) * self.shoot_distance), ballposition.y + (cos(a + self.shoot_angle_offset) * self.shoot_distance))
        else:
            self.reached_position = True
            self.turn(degrees(a) - 80)
        return

    def stop(self):
        self.stopped = True

    def move_keeper(self):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False
        ballposition = self.world.ball.get_position()
        self.target = ballposition.y/10
        self.rotation = atan2(ballposition.x-self.beampos.x, ballposition.y-self.beampos.y)
        if(abs(self.target - self.beampos.y) > 0.1):
            if(self.target > self.beampos.y):
               self.beampos.y = self.beampos.y + 0.01
            else:
               self.beampos.y = self.beampos.y - 0.01
        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384",(-1 * degrees(self.rotation) ), ")")

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
