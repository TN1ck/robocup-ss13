class Encoder(object):

    BASE = 90
    teamID = 0
    
    def __init__(self):
        pass

    def __del__(self):
        pass


    def encode(self):
        pass

    #i_c := int c (command)
    def encodeSCWoP(self, i_c):
        msg = chr(self.mapping(1)) # message type 1 - single command without parameters
        msg = msg + chr(self.mapping(i_c))
        msg = msg + self.checksum(msg,3)
        return msg

    def encodeSCTR(self, i_c, i_nao):
        msg = chr(self.mapping(2)) # messagte type 2
        msg = msg + chr(self.mapping(i_c))
        msg = msg + chr(self.mapping(i_nao))
        msg = msg + self.checksum(msg, 3)
        return msg

    #message type 3
    #single command with parameters
    def encodeSCWP(self, i_c, x, y):
        msg = chr(self.mapping(3)) 
        msg = msg + chr(self.mapping(i_c))
        msg = msg + self.encodeDouble(x,3)
        msg = msg + self.encodeDouble(y,3)
        msg = msg + self.checksum(msg, 3)
        return msg

    #message type 4
    #single command with parameters to nao(robot)
    def encodeSCWPTR(self, i_c, i_nao, x, y):
        msg = chr(self.mapping(4)) 
        msg = msg + chr(self.mapping(i_c))
        msg = msg + chr(self.mapping(i_nao))
        msg = msg + self.encodeDouble(x,3)
        msg = msg + self.encodeDouble(y,3)
        msg = msg + self.checksum(msg, 3)
        return msg

    #message type 5
    def encodeMT5(self, c, fNao, tNao, x, y):
        msg = chr(self.mapping(5))
        msg = msg + chr(self.mapping(c))
        msg = msg + chr(self.mapping(fNao))
        msg = msg + chr(self.mapping(tNao))
        msg = msg + self.encodeDouble(x, 3)
        msg = msg + self.encodeDouble(y, 3)
        msg = msg + self.checksum(msg, 3)
        return msg

    # calculate the checksum
    # s_msg the message
    # checksum length
    def checksum(self, s_msg, i_cl):
        i_l = len(s_msg)
        i_csum = 0

        i=0
        while( i < i_l):
            i_csum = (i_csum + ord(s_msg[i])*(i+1)) % (self.BASE**i_cl)
            i = i+1

        d_csum = (i_csum + self.teamID) / ((10.0)**i_cl)

        c_csum = self.encodeDouble(d_csum, i_cl)

        if(c_csum[2] == "\\"):
            c_csum = c_csum[0] + c_csum[1] + "B"

        return c_csum

    # d_x := double x 
    # i_c := int c (character length)
    def encodeDouble(self, d_x, i_cl):
        i_range = ((self.BASE**i_cl)/(10*i_cl)/2)
        if(d_x > -i_range and d_x < i_range):

            d_x = d_x * (10**i_cl)

            d_x = int(d_x)

            i_z = 0
            s_mz = ""

            b_isNegative = 0
            if(d_x < 0):
                d_x = d_x*(-1)
                b_isNegative = 1
            
            i=0
            while(i < i_cl):
                i_z = d_x % self.BASE
                if(i==i_cl-1 and b_isNegative):
                    i_z = i_z+self.BASE/2
                s_mz = s_mz + chr(self.mapping(i_z))
                d_x = int(d_x / self.BASE)
                i = i+1

            return s_mz[::-1]
        
        else:
            print "number is out of range"

    # z := 0-89
    def mapping(self, z):
        z = z+33
        if(z == 34):
            z = 123
        elif(z == 40):
            z = 124
        elif(z == 41):
            z = 125
        elif(z == 57):
            z = 126
        return z
            
                
                

            
        

    

