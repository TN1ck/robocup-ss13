from math import *
import math

class Movement:
    def __init__(self, world, socket, player_nr):
        self.world = world
        self.socket = socket
        self.player_nr = player_nr
        #self.team = team
        self.velocity = 0.02
        self.divergence = 0.05
        self.stopped = True
        self.destination = None
        self.angular_precision = 0.1;
        self.rotation = 0
        self.degrees = 0
        self.position = self.world.entity_from_identifier['P_1_' + str(self.player_nr)].get_position()
        self.beampos = self.position
        self.shoot_distance = hypot(-0.2, 0.05)
        self.shoot_angle_offset = atan2(0.05, -0.2)
        self.fresh = True
        self.reached_position = False

    def reset_pos(self):
        self.fresh = True

    def get_world(self):
        return self.world

    def send(self, *params):
        self.socket.enqueue(" ".join(map(str, ["("] + list(params) + [")"])))

    def run(self, *destination):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False

        self.position = self.beampos
        self.stopped = False
        if destination: self.destination = destination

        self.rotation = atan2(self.destination[0] - self.position.x, self.destination[1] - self.position.y)
        self.degrees = (-1 * degrees(self.rotation) )

        dy = cos(self.rotation) * self.velocity
        dx = sin(self.rotation) * self.velocity

        self.beampos.x = self.beampos.x + dx
        self.beampos.y = self.beampos.y + dy
        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384",self.degrees, ")")

    def turn(self, angle):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False

        if angle < (-1 * degrees(self.rotation)) and abs(angle - (-1 * degrees(self.rotation))) > 1:
            self.degrees = self.degrees - 2
        else:
            self.degrees = self.degrees + 2
        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384",self.degrees, ")")

    def turn_about(self, angle):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False
        print str(self.degrees + angle)
        self.degrees = self.degrees + angle
        self.send("agent (unum", self.player_nr, ") (team Left) (move", self.beampos.x, self.beampos.y, "0.384",self.degrees, ")")

        
        
    def run_to_shoot_position(self, *destination):
        self.position = self.world.get_entity_position('P_1_' + str(self.player_nr))
        ballposition = self.world.ball.get_position()
        #ballposition.x = 0
        #ballposition.y = 0
        a = atan2(destination[1] - ballposition.y, destination[0] - ballposition.x)
        self.destx = ballposition.x + (cos(a + self.shoot_angle_offset) * self.shoot_distance)
        self.desty = ballposition.y + (sin(a + self.shoot_angle_offset) * self.shoot_distance)
        if (hypot(self.destx - self.position.x, self.desty - self.position.y) > self.divergence):
            self.run(self.destx, self.desty)
            self.reached_position = False
        else:
            self.turn(degrees(a) - 80)
            self.reached_position = True
        return

    def stop(self):
        self.stopped = True

    def move_keeper(self):
        if self.fresh:
            self.beampos = self.world.get_entity_position('P_1_' + str(self.player_nr))
            self.fresh = False
        ballposition = self.world.ball.get_position()
        self.dir_to_ball = ballposition - self.beampos
        self.betrag = math.sqrt(self.dir_to_ball.x*self.dir_to_ball.x + self.dir_to_ball.y*self.dir_to_ball.y)
        self.norm = self.dir_to_ball*(1/self.betrag)
        self.dir_to_ball.x = -15
        self.dir_to_ball.y = 0
        self.distance =  math.sqrt( (ballposition - self.dir_to_ball).x*(ballposition - self.dir_to_ball).x + 
                                    (ballposition - self.dir_to_ball).y*(ballposition - self.dir_to_ball).y)
        self.target = self.dir_to_ball + self.norm
        self.target.x = self.dir_to_ball.x + self.norm.x*(self.distance/15)
        self.target.y = self.dir_to_ball.y + self.norm.y*(self.distance/15)
        self.rotation = atan2(ballposition.x-self.beampos.x, ballposition.y-self.beampos.y)
        self.degrees = (-1 * degrees(self.rotation) )
        if(abs(self.target.y - self.beampos.y) > 0.01):
            if(self.target.y > self.beampos.y):
               self.beampos.y = self.beampos.y + 0.01
            else:
               self.beampos.y = self.beampos.y - 0.01
        if(abs(self.target.x - self.beampos.x) > 0.01):
            if(self.target.x > self.beampos.x):
               self.beampos.x = self.beampos.x + 0.01
            else:
               self.beampos.x = self.beampos.x - 0.01
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
