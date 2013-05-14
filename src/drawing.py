import socket
import struct

class Drawing:
        udpIp = "127.0.1.1"
        udpPort = 32769
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

        def __init__(self,udpIp,udpPort):
                if (udpIp!=0):
                    self.udpIp = udpIp
                if (udpPort != 0 ):         
                    self.udpPort = udpPort
                
        def sendCommand(self,message):
                self.sock.sendto(message,(self.udpIp, self.udpPort))

        def formatFloat(self,number):
            number=str(number)[:6]
            if len(number)<6:
                    if("." in number):
                            number= (number+"00000")[:6]
                    else:
                            number= (number+".0000")[:6]
            return number

        def swapBuffers(self,setName):
                self.sendCommand(bytearray([0,0]+list(setName)+[0]))
                
        def drawCircle(self,posX,posY,radius,thickness,red,green,blue,setName):
                posX = self.formatFloat(posX)
                posY = self.formatFloat(posY)
                radius = self.formatFloat(radius)
                thickness = self.formatFloat(thickness)
                self.sendCommand(bytearray([1,0]+list(posX)+list(posY)+list(radius)+list(thickness)+[red,green,blue]+list(setName)+[0]))

        def drawLine(self,startX,startY,startZ,endX,endY,endZ,thickness,red,green,blue,setName):
                startX = self.formatFloat(startX)
                startY = self.formatFloat(startY)
                startZ = self.formatFloat(startZ)
                endX = self.formatFloat(endX)
                endY = self.formatFloat(endY)
                endZ = self.formatFloat(endZ)
                thickness = self.formatFloat(thickness)
                self.sendCommand(bytearray([1,1]+list(startX)+list(startY)+list(startZ)+list(endX)+list(endY)+list(endZ)+list(thickness)+[red,green,blue]+list(setName)+[0]))

        def drawPoint(self,posX,posY,posZ,size,red,green,blue,setName): #recommended Values for size are within [1,10]
                posX = self.formatFloat(posX)
                posY = self.formatFloat(posY)
                posZ = self.formatFloat(posZ)
                size = self.formatFloat(size)
                self.sendCommand(bytearray([1,2]+list(posX)+list(posY)+list(posZ)+list(size)+[red,green,blue]+list(setName)+[0]))

        def drawSphere(self,posX,posY,posZ,radius,red,green,blue,setName):
                posX = self.formatFloat(posX)
                posY = self.formatFloat(posY)
                posZ = self.formatFloat(posZ)
                radius = self.formatFloat(radius)
                self.sendCommand(bytearray([1,3]+list(posX)+list(posY)+list(posZ)+list(radius)+[red,green,blue]+list(setName)+[0]))

        def drawPolygon(self,vertices,red,green,blue,alpha,setName):
                vertexString = ""
                for i in vertices:
                    vertexString += self.formatFloat(i)
                self.sendCommand(bytearray([1,4,len(vertices)/3,red,green,blue,alpha]+list(vertexString)+list(setName)+[0]))

        def drawStandardAnnotation(self,posX,posY,posZ,red,green,blue,text,setName):
                posX = self.formatFloat(posX)
                posY = self.formatFloat(posY)
                posZ = self.formatFloat(posZ)
                msg = bytearray([2,0]+list(posX)+list(posY)+list(posZ)+[red,green,blue]+list(text)+[0]+list(setName)+[0])
                self.sendCommand(msg)

        def drawAgentAnnotation(self,agentTeam,red,green,blue,text):
                self.sendCommand(bytearray([2,1,agentTeam,red,green,blue]+list(text)+[0]))

        def removeAgentAnnotation(agentTeam):
                self.sendCommand(bytearray([2,2,agentTeam]))
