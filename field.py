#pylint:disable=W0703
try:
    import logging
except:
    input("Module logging not installed!")
    exit()

logging.basicConfig(filename='render.log', filemode='w', format='Logg - %(message)s')

try:
    import os
    import time 
    import math
    import logging
    import random
    import time
    import numpy as np
    from resources import *
    from ObjLoader import ObjLoader
    
except Exception as e:
                logging.error(e, exc_info=True)
    
class RenderField:
    def __init__(self, widthHeightDepth, background=(-1,-1,-1), pixel=(255,255,255), colorGradiant=True):        
        print("Initiating the field!")
        
        self.width, self.height, self.depth = widthHeightDepth
        self.widthHeightDepth = widthHeightDepth
        self.background = background
        self.pixel = pixel
        
        #self.depthASCII = list("@#8&$*ox%/\|{}?:_+~!-,\"^'`. ") #Choose between 2 sets of characters for depth imitation
        self.depthASCII = list("@#%+=-:. ")
        
        t = time.time()
        self.field = [[[self.background for z in range(self.depth)] for y in range(self.height)] for x in range(self.width)] #Create 3d-(actually 4d)-list as coordinate-system
        print("It took ",time.time()-t,"s to create field!")
        
        self.drawnPixels = []
        self.colorGradiant = colorGradiant


#----HELPFUL-FUNCTIONS------------------------------------------------------------------------------------------------------------------
        
    def setField(self,inputField):
        try:
            self.field = inputField  #Set this RenderFields field to the input
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
            
    def clearField(self):
        self.field = [[[self.background for z in range(self.depth)] for y in range(self.height)] for x in range(self.width)] #Clears the field

    def clear(self):
        clearScreen()
        self.clearField()

    def getDepthASCII(self, depth, maxDepth): #Maps a depth/distance to a depthAscii and returns it
        return self.depthASCII[int(depth)*len(self.depthASCII)//int(maxDepth)]

    def lookupColor(self, p):
        try:
            x,y,z = p
            return self.field[x][y][z]
        except:
            return (0,0,0)
    
    def rotateShape(self, shape, a):
        mp = shape["mp"]
        shade = shape["shade"]
        for p in shape["points"]:
            amp = replaceInCoord(mp,y=p[1])
            self.drawPixel(p, self.background)
            self.drawPixel(rotatePoint(amp, p, a), shade)
        

#----DRAWING-------------------------------------------------------------------------------------------

    def drawPixel(self, xyz, shade=False): #Draws self.pixel into self.filed at point xyz
        try:
            y, x, z = xyz
            x = round(x)
            y = round(y)
            z = round(z)

            self.drawnPixels.append((xyz, shade, len(self.drawnPixels)))
       
            if shade == False:
                self.field[x][y][z] = self.pixel
            else:
                #s1,s2,s3 = shade
                #shade = (max(s1,0),max(s2,0),max(s3,0))
                
                self.field[x][y][z] = shade
                
        except Exception as e:
                    logging.error((e, xyz), exc_info=True)

    def drawLine(self, p1, p2, draw=True, shade=False): #Bresenham's line drawing algorithm. If not draw the points are returned but not drawn into self.field
       
        p1 = roundPoint(p1)
        p2 = roundPoint(p2)
        
        x1,y1,z1 = p1
        x2,y2,z2 = p2
        ListOfPoints = [] 
        ListOfPoints.append((x1, y1, z1)) 
        dx = abs(x2 - x1) 
        dy = abs(y2 - y1) 
        dz = abs(z2 - z1) 
        if (x2 > x1): 
            xs = 1
        else: 
            xs = -1
        if (y2 > y1): 
            ys = 1
        else: 
            ys = -1
        if (z2 > z1): 
            zs = 1
        else: 
            zs = -1
      
        #X
        if (dx >= dy and dx >= dz):         
            p1 = 2 * dy - dx 
            p2 = 2 * dz - dx 
            while (x1 != x2): 
                x1 += xs 
                if (p1 >= 0): 
                    y1 += ys 
                    p1 -= 2 * dx 
                if (p2 >= 0): 
                    z1 += zs 
                    p2 -= 2 * dx 
                p1 += 2 * dy 
                p2 += 2 * dz 
                ListOfPoints.append((x1, y1, z1)) 
      
        #Y-axis
        elif (dy >= dx and dy >= dz):        
            p1 = 2 * dx - dy 
            p2 = 2 * dz - dy 
            while (y1 != y2): 
                y1 += ys 
                if (p1 >= 0): 
                    x1 += xs 
                    p1 -= 2 * dy 
                if (p2 >= 0): 
                    z1 += zs 
                    p2 -= 2 * dy 
                p1 += 2 * dx 
                p2 += 2 * dz 
                ListOfPoints.append((x1, y1, z1)) 
      
        #Z" 
        else:         
            p1 = 2 * dy - dz 
            p2 = 2 * dx - dz 
            while (z1 != z2): 
                z1 += zs 
                if (p1 >= 0): 
                    y1 += ys 
                    p1 -= 2 * dz 
                if (p2 >= 0): 
                    x1 += xs 
                    p2 -= 2 * dz 
                p1 += 2 * dy 
                p2 += 2 * dx 
                ListOfPoints.append((x1, y1, z1))

        if draw:
            for c in ListOfPoints:
                self.drawPixel(c, shade=shade)
            
        return ListOfPoints


    def drawTriangle(self, p1p2p3, shade=False, draw=True, fill=False):
        p1, p2, p3 = p1p2p3
        
        p1p2 = self.drawLine(p1,p2,draw, shade)
        p2p3 = self.drawLine(p2,p3,draw, shade)
        p3p1 = self.drawLine(p3,p1,draw, shade)

        if fill:
            for p in p1p2:
                self.drawLine(p3,p)
            for p in p2p3:
                self.drawLine(p1,p)
            for p in p3p1:
                self.drawLine(p2,p)

        return [p1p2,p2p3,p3p1]

    def drawRect(self, p1p2p3p4, fill=False, shade=False, draw=True): #Should not be used. Try 2 triangle instead
        linesToReturn = []
        
        p1, p2, p3, p4 = p1p2p3p4
        
        # print(p1,p2,p3,p4)
        
        linesToReturn.append(self.drawLine(p1,p2, shade=shade, draw=draw))     #p4  ____  p1
        linesToReturn.append(self.drawLine(p2,p3, shade=shade, draw=draw))     #   |    |
        linesToReturn.append(self.drawLine(p3,p4, shade=shade, draw=draw))     #   |____|
        linesToReturn.append(self.drawLine(p4,p1, shade=shade, draw=draw))    #p3        p2
        
        
        
        if fill:
            index, line1 = max(enumerate(linesToReturn), key = lambda tup: len(tup[1]))
            line2 = linesToReturn[index-2][::-1]
            ll1 = len(line1)
            ll2 = len(line2)
            
            for i in range(len(line1)):
                il2 = int(mapFunc(i, 0, ll1, 0, ll2))
                #print(il2,ll2)
                self.drawLine(line1[i], line2[il2], shade=shade, draw=draw)
            
            
        return linesToReturn
    
    def drawPoly(self, points, fill=True, shade=False, draw=True):
        
        linesToReturn = []
        
        for i in range(len(points)):
            linesToReturn.append(self.drawLine(points[i-1], points[i], draw=draw, shade=shade))
        
        edgeLines = linesToReturn
        
        if fill:
            for i in range(len(edgeLines)):
                
                line1 = edgeLines[i]
                line2 = linesToReturn[i-len(edgeLines)//2][::-1]
                ll1 = len(line1)
                ll2 = len(line2)
                
                print("line1", ll1)
                print("line2", ll2)
            
                for o in range(len(line1)):
                    il2 = int(mapFunc(i, 0, ll1, 0, ll2))
                    #print(il2,ll2)
                    # print(o,il2)
                    self.drawLine(line1[o], line2[il2], shade=shade, draw=draw)
                
        
        
    def _drawCube(self, midPoint, size=10, fill=True, shade=False, draw=True): #Draws cube with size "size" from mid point.
        x, y, z = midPoint
        
        sh = int(size/2)
        
        p = {                     #                     H _____ E
            "A":(x+sh,y+sh,z-sh), #A                     /    /|
            "B":(x+sh,y-sh,z-sh), #B                    /    / |
            "C":(x-sh,y-sh,z-sh), #C                 D /____/A |
            "D":(x-sh,y+sh,z-sh), #D                   |  G |  | F
            "E":(x+sh,y+sh,z+sh), #E                   |    | /
            "F":(x+sh,y-sh,z+sh), #F                  c|____|/ B
            "G":(x-sh,y-sh,z+sh), #G
            "H":(x-sh,y+sh,z+sh)  #H
                  }
        
        allP = []

        allP.append(self.drawRect((p["A"],p["B"],p["C"],p["D"]),fill = fill, shade=shade, draw=draw))
        allP.append(self.drawRect((p["E"],p["F"],p["G"],p["H"]),fill = fill, shade=shade, draw=draw))
        allP.append(self.drawRect((p["A"],p["E"],p["H"],p["D"]),fill = fill, shade=shade, draw=draw))
        allP.append(self.drawRect((p["A"],p["E"],p["F"],p["B"]),fill = fill, shade=shade, draw=draw))
        allP.append(self.drawRect((p["B"],p["C"],p["G"],p["F"]),fill = fill, shade=shade, draw=draw))
        allP.append(self.drawRect((p["D"],p["C"],p["G"],p["H"]),fill = fill, shade=shade, draw=draw))
        
        return allP
    
    
    def drawCube(self, midpoint, size=10, fill=True, shade=False, draw=True): #Draws cube with size "size" from mid point.
        if draw:
            print("Drawing cube!")
        
        allPoints = []
         
        allPoints.append(self._drawCube(midpoint, size, fill, shade, draw))
        x,y,z = midpoint
        midpoint = (x-1,y,z)
        allPoints.append(self._drawCube(midpoint, size-1, fill, shade, draw))
        
        return {"type":"Cube", "fill":fill, "draw":draw, "shade":shade,"mp":midpoint,"size":size,"points":flattenList(allPoints,3)}

    def drawCircle(self, xyz, r, shade=False, draw=True): # Draws circle with radius "r" from midpoint "xyz". Note: Circle is parallel to x-axis
        xc, yc, zc = xyz
        coords = []
        def drawC(xc, yc, zc, x, y):
            coords.append((xc + x, yc + y, zc))
            coords.append((xc - x, yc + y, zc))
            coords.append((xc + x, yc - y, zc))
            coords.append((xc - x, yc - y, zc))
            coords.append((xc + y, yc + x, zc))
            coords.append((xc - y, yc + x, zc))
            coords.append((xc + y, yc - x, zc))
            coords.append((xc - y, yc - x, zc))

        x = 0
        y = r
        d = 3 - 2 * r
        drawC(xc, yc, zc, x, y)
        while y >= x:
            x += 1
            if (d > 0):
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            drawC(xc, yc, zc, x, y)
            #drawC(xc, yc, zc, x+1, y)
            #drawC(xc, yc, zc, x-1, y)
        
        if draw:
            for c in coords:
                self.drawPixel(c, shade=shade)
        return coords


    def drawSphere(self, xyz, r, shade=False, draw=True): #Draws sphere. Not quite functional yet
        print("Drawing sphere!")
        points = []
        x, y, z = xyz
        for sr in range(-1,r):
            #self.drawCircle((x,y,z-r+sr),sr-2, shade
            points.append(self.drawCircle((x+1,y,z-r+sr),sr-1, shade, draw))
            points.append(self.drawCircle((x,y,z-r+sr),sr-1, shade, draw))
            
            points.append(self.drawCircle((x+1,y,z-r+sr),sr, shade, draw))
            points.append(self.drawCircle((x,y,z-r+sr),sr, shade, draw))
            
        index = list(range(-1,r))
        for sr in index:
            #self.drawCircle((x,y,z+sr),index[-sr]-2, shade)
            points.append(self.drawCircle((x+1,y,z+sr),index[-sr]-1, shade, draw))
            points.append(self.drawCircle((x,y,z+sr),index[-sr]-1, shade, draw))
           
            points.append(self.drawCircle((x+1,y,z+sr),index[-sr], shade, draw))
            points.append(self.drawCircle((x,y,z+sr),index[-sr], shade, draw))
        
        return points
    
    def drawShallowSphere(self, xyz, r, shade=False, draw=True): #Draws sphere. Not quite functional yet
        print("Drawing sphere!")
        points = []
        x, y, z = xyz
        for sr in range(-1,r):
            points.append(self.drawCircle((x,y,z-r+sr),sr, shade, draw))
            
        index = list(range(-1,r))
        for sr in index:
            points.append(self.drawCircle((x,y,z+sr),index[-sr], shade, draw))
        
        return points
 

    def drawFloor(self,size=30,h=1): #Draws flat plane
        s = int(size/2)
        p1 = (s,h,-s)
        p2 = (-s,h,-s)
        p3 = (-s,h,s)
        p4 = (s,h,s)

        pp = self.drawLine(p3,p4,False)
        po = self.drawLine(p2,p1,False)
        for n in range(len(pp)):
            #print(po[i],pp[i])
            self.drawLine(po[n],pp[n])



    def drawRectFromTexture(self, p1, p2, p3, p4, pic):
        try:
            texture = readTexture(pic)
            
            points = []
            
            
            l12 = self.drawLine(p1,p2, draw = False)[1:]   
                                                                           
            l34 = self.drawLine(p3,p4, draw = False)[:-1] 
                                                                          
        
            l43 = l34[::-1]
            for p in range(len(l43)):
                points.append(self.drawLine(l43[p], l12[p], draw = False))
            
            for p, c in zip(flattenList(points),texture):
                self.drawPixel(p,c)

        
        except Exception as e:
            print("®ERROR® - couldnt draw rect from texture "+str(pic))
            logging.error(e)

    def drawTexturedCube(self, midPoint, side, top=False, bottom=False): #Draws cube with size "size" from mid point.
        if not top:
            top = side
        if not bottom:
            bottom = side
        
        x, y, z = midPoint
        size = 16
        
        sh = int(size/2)-1
        
        p = {                     #                     H _____ E
            "A":(x+sh,y+sh,z-sh), #A                     /    /|
            "B":(x+sh,y-sh,z-sh), #B                    /    / |
            "C":(x-sh,y-sh,z-sh), #C                 D /____/A |
            "D":(x-sh,y+sh,z-sh), #D                   |  G |  | F
            "E":(x+sh,y+sh,z+sh), #E                   |    | /
            "F":(x+sh,y-sh,z+sh), #F                  c|____|/ B
            "G":(x-sh,y-sh,z+sh), #G
            "H":(x-sh,y+sh,z+sh)  #H
                  }
        

        self.drawRectFromTexture(p["C"], p["D"], p["A"], p["B"], side)
        self.drawRectFromTexture(p["G"], p["H"], p["E"], p["F"], side)
        self.drawRectFromTexture(p["A"], p["E"], p["H"], p["D"], bottom)
        self.drawRectFromTexture(p["B"], p["A"], p["E"], p["F"], side)
        self.drawRectFromTexture(changePoint(p["B"],y=1), changePoint(p["C"],y=1), changePoint(p["G"],y=1), changePoint(p["F"],y=1), top)
        self.drawRectFromTexture(p["G"], p["H"], p["D"], p["C"], side)
        

    def drawTexturedBlockStack(self, bottomCube, height, texture):
        for n in range(height):
            self.drawTexturedCube(changePoint(bottomCube,y=-14*n), texture)

    def drawTexturedBlockRow(self, leftCube, width, texture):
        if type(texture) == str:
            for n in range(width):
                self.drawTexturedCube(changePoint(leftCube,x=14*n), texture)
        elif type(texture) == tuple:
            for n in range(width):
                self.drawTexturedCube(changePoint(leftCube,x=14*n), *texture)
        else:
            
            print("®®®®®®®®ERROR - In else!")
    
    def drawTexturedBlockRows(self,leftCube, width, depth, texture):
        if type(texture) == str:
            for n in range(depth):
                printProgressBar(n,depth, prefix="Textured rows")
                self.drawTexturedBlockRow(changePoint(leftCube,z=14*n), width, texture)
        elif type(texture) == tuple:
            for n in range(depth):
                printProgressBar(n,depth, prefix="Textured rows")
                self.drawTexturedBlockRow(changePoint(leftCube,z=14*n), width, (texture[0], texture[1], texture[2]))
        else:
            
            print("®®®®®®®®ERROR - In else!")
                
                
                
    def drawModel(self, name, ax=0, ay=0, factor=1):
        obj = ObjLoader(name, factor)
        print("drawing polygons!")
       
        
        polys = obj.polys
        # print(obj.polys)
        
        
        mp = calcModelMidpoint(polys)
        print("Model midpoint:",roundPoint(mp))
        
        #x,_,z = mp
        
        lenpols = len(polys)
        for npol in range(lenpols):
            #print("a")
            printProgressBar(npol+1,lenpols, prefix="drawing model")
            
            poly = polys[npol]
            
            #y = poly[0][1]
            
            #rp = (x, y, z)
            
            poly = [rotatePoint(getRotationPoint(mp,p), p, ax) for p in poly]
            
            l = len(poly)
           # print(l)
            #print(poly)
            if l == 3:
                self.drawTriangle(poly, fill=True)
                #print("triangle")
            else:
                triangles = turnIntoTriangles(poly)
                for triangle in triangles:
                    self.drawTriangle(triangle, fill=True)
               
                    

        print(" ",end="\r")       



    
