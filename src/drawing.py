import struct
import drawing_advanced
import world

''' This Class is supposed to make drawing calls a little easier. 
    For all coordinates it uses the Vector class from world.py.
    This means that all shapes will be 2-Dimensional only - 
    for 3D stuff you will have to use the more complex drawing_advanced.py
    There are also some more advanced functions like drawArrow'''
class Drawing:
        drawer = None

        ''' If you wish to use this locally you can just call this as 
            drawing.Drawing(0,0) otherwise udpIp should be a string'''
        def __init__(self, udpIp, udpPort):
                self.drawer = drawing_advanced.DrawingAdvanced(udpIp,udpPort)

        def _checkColor(self, color):
            if ((color[0]>255 or color[1]>255 or color[2]>255) or (color[0]<0 or color[1]<0 or color[2]<0)):
                        print("Color values should be between 0 and 255 - current values are " + str(color))
                        return 1
            return 0

        ''' This will display all drawings that have a name 
            starting with name AND have not been displayed yet.
            All the drawings with that name that have
            already been displayed WILL DISAPPEAR'''
        def showDrawingsNamed(self, name):
            self.drawer.swapBuffers(name)

        def drawCircle(self, center, radius, thickness, color, name):
                if self._checkColor(color) == 0:
                        self.drawer.drawCircle(center.x, center.y, radius, thickness, color[0], color[1], color[2], name)

        ''' startPoint and endPoint should be Vectors,
            thickness should be a float or int 
            color should be a list or array ([red, green, blue])'''
        def drawLine(self, startPoint, endPoint, thickness, color, name):
                if self._checkColor(color) == 0:
                        self.drawer.drawLine(startPoint.x, startPoint.y, 0, endPoint.x, endPoint.y, 0, thickness, color[0], color[1], color[2], name)
        
        def drawPoint(self, position, size, color, name):
                if self._checkColor(color) == 0:
                        self.drawer.drawPoint(position.x, position.y, 0, size, color[0], color[1], color[2], name)

        ''' in this case radius is measured in meters (don't ask me why)'''
        def drawSphere(self, center, radius, color, name):
                if self._checkColor(color) == 0:
                        self.drawer.drawSphere(center.x, center.y, 0, radius, color[0], color[1], color[2], name)

        ''' This one is a little special:
            vertices should be a list or array of Vectors 
            representing all the cornerpoints of the shape'''
        def drawPolygon(self, vertices, color, name):
                if self._checkColor(color) == 0:
                        _vertices = []
                        for v in vertices:
                                _vertices.extend([v.x, v.y, 0])
                        print(_vertices+color+[255])
                        self.drawer.drawPolygon(_vertices, color[0], color[1], color[2], 255, name)

        def drawStandardAnnotation(self, position, color, text, name):
                if self._checkColor(color) == 0:
                        self.drawer.drawStandardAnnotation(position.x, position.y, 0, color[0], color[1], color[2], text, name)

        def drawAgentAnnotaion(self, agentNum, teamNum, color, text):
                if self._checkColor(color) == 0:
                        if agentNum<128:
                                if teamNum == 0:
                                        agentTeam = agentNum - 1
                                elif teamNum == 1:
                                        agentTeam = agentNum + 127
                                else:
                                        print("Team number must be 0 or 1, but is "+str(teamNum))
                                        return
                                self.drawer.drawAgentAnnotation(agentTeam, color[0], color[1], color[2], text)
                        else:
                                print("agentNum must be lower than 128 but is "+str(agentNum))                        

        def removeAgentAnnotation(self, agentNum, teamNum):
                if agentNum<128:
                        if teamNum == 0:
                                agentTeam = agentNum - 1
                        elif teamNum == 1:
                                agentTeam = agentNum + 127
                        else:
                                print("Team number must be 0 or 1, but is "+str(teamNum))
                                return
                        self.drawer.removeAgentAnnotation(agentTeam)
                else:
                        print("agentNum must be lower than 128 but is "+str(agentNum))
