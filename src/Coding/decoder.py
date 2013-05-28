import encoder

class Decoder(object):

    BASE = 90
    def __init__(self):
        pass

    def __del__(self):
        pass

    def decode(self):
        pass

    # 0 - false, 1 - true
    # s_msg = message (string)
    # i_cl = int cl (checksum length)
    def isValidChecksum(self, s_msg, i_cl):
        e = encoder.Encoder()

        s_omsg = ""
        s_csum = ""

        i=0
        while(i< len(s_msg)):
            if(i<(len(s_msg)-i_cl)):
               s_omsg = s_omsg+s_msg[i]
            else:
               s_csum = s_csum + s_msg[i]

            i = i+1

        s_cmsg = e.checksum(s_omsg, i_cl)
        
        if( s_csum == s_cmsg):
            return 1
        else:
            return 0
        
        
    
    def decodeDouble(self, s_str):
        i_l = len(s_str)
        if(i_l > 0):
            i_mz = 0
            d_x = 0.0

            b_isNegative = 0
            i = 0
            while(i < i_l):
                i_mz = ord(s_str[i])
                i_mz = self.reMapping(i_mz)
                if(i==0 and i_mz>=self.BASE/2):
                    i_mz = (i_mz-self.BASE/2)
                    b_isNegative = 1
                d_x = d_x + i_mz * (self.BASE**(i_l-i-1))
                i = i+1

        if(b_isNegative):
            return (-1)*(d_x/(10**i_l))
        else:
            return d_x/(10**i_l)
 

    def reMapping(self, mz):
        if(mz==126):
            return 57
        elif(mz==125):
            return 41
        elif(mz==124):
            return 40
        elif(mz==123):
            return 34
        else:
            return mz-33

        
