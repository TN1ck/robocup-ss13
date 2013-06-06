import socket
import struct

'''  For more information on these commands see
     https://sites.google.com/site/umroboviz/drawing-api/draw-commands '''


class DrawingAdvanced:

        udpIp = "127.0.0.1"
        udpPort = 32769
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

        ''' If you wish to use this locally you can just call this
            as drawing_basics.DrawingBasics(0,0) otherwise udpIp should be a string'''
        def __init__(self, udpIp, udpPort):
                if (udpIp != 0):
                    self.udpIp = udpIp
                if (udpPort != 0):
                    self.udpPort = udpPort

        def _sendCommand(self, message):
                self.sock.sendto(message, (self.udpIp, self.udpPort))

        ''' Formats floats into Strings of length 6 as explained
            in the Command documentation linked above'''
        def _formatFloat(self, number):
            number = str(number)[:6]
            if len(number) < 6:
                    if("." in number):
                            number = (number+"00000")[:6]
                    else:
                            number = (number+".0000")[:6]
            return number

        ''' You have to call this function after drawing your stuff
            (if you want to actually see the drawings)'''
        def swapBuffers(self, setName):
                self._sendCommand(bytearray([0,0]+list(setName)+[0]))

        def drawCircle(self, posX, posY, radius, thickness, red, green, blue, setName):
                posX = self._formatFloat(posX)
                posY = self._formatFloat(posY)
                radius = self._formatFloat(radius)
                thickness = self._formatFloat(thickness)
                self._sendCommand(bytearray([1,0]+list(posX)+list(posY)+list(radius)+list(thickness)+[red,green,blue]+list(setName)+[0]))

        def drawLine(self, startX, startY, startZ, endX, endY, endZ, thickness, red, green, blue, setName):
                startX = self._formatFloat(startX)
                startY = self._formatFloat(startY)
                startZ = self._formatFloat(startZ)
                endX = self._formatFloat(endX)
                endY = self._formatFloat(endY)
                endZ = self._formatFloat(endZ)
                thickness = self._formatFloat(thickness)
                self._sendCommand(bytearray([1,1]+list(startX)+list(startY)+list(startZ)+list(endX)+list(endY)+list(endZ)+list(thickness)+[red,green,blue]+list(setName)+[0]))

        def drawPoint(self, posX, posY, posZ, size, red, green, blue, setName):  # recommended Values for size are within [1,10]
                posX = self._formatFloat(posX)
                posY = self._formatFloat(posY)
                posZ = self._formatFloat(posZ)
                size = self._formatFloat(size)
                self._sendCommand(bytearray([1,2]+list(posX)+list(posY)+list(posZ)+list(size)+[red,green,blue]+list(setName)+[0]))

        def drawSphere(self, posX, posY, posZ, radius, red, green, blue, setName):
                posX = self._formatFloat(posX)
                posY = self._formatFloat(posY)
                posZ = self._formatFloat(posZ)
                radius = self._formatFloat(radius)
                self._sendCommand(bytearray([1,3]+list(posX)+list(posY)+list(posZ)+list(radius)+[red,green,blue]+list(setName)+[0]))

        ''' To draw a Polygon you need to pass a List of vertices to the '''
        def drawPolygon(self, vertices, red, green, blue, alpha, setName):
                vertexString = ""
                for i in vertices:
                    vertexString += self._formatFloat(i)
                self._sendCommand(bytearray([1,4,len(vertices)/3,red,green,blue,alpha]+list(vertexString)+list(setName)+[0]))

        '''drawStandardAnnotation writes the specified text to the specified x,y,z position'''
        def drawStandardAnnotation(self, posX, posY, posZ, red, green, blue, text, setName):
                posX = self._formatFloat(posX)
                posY = self._formatFloat(posY)
                posZ = self._formatFloat(posZ)
                msg = bytearray([2,0]+list(posX)+list(posY)+list(posZ)+[red,green,blue]+list(text)+[0]+list(setName)+[0])
                self._sendCommand(msg)

        ''' drawAgentAnnotation writes the specified text above the Head of the robot specified by agentTeam
            agentTeam should be one Number containing information about the agent who gets the annotation and the team he's playing for.
            #
            You can calculate the Team/Agent byte as follows (leftTeam is a boolean; agentNum is an integer):
                if(leftTeam):
                    agentTeam = agentNum - 1
                else:
                    agentTeam = agentNum + 127
            #
            agentNum should NOT be greater than 128'''
        def drawAgentAnnotation(self, agentTeam, red, green, blue, text):
                self._sendCommand(bytearray([2,1,agentTeam,red,green,blue]+list(text)+[0]))

        def removeAgentAnnotation(self, agentTeam):
                self._sendCommand(bytearray([2,2,agentTeam]))
