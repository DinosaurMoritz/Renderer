#pylint:disable=W0702
#pylint:disable=R1722
#pylint:disable=W0401
#pylint:disable=W0703
try:
    import logging
except:
    input("Module logging not installed!")
    exit()
logging.basicConfig(filename='camera.log', filemode='w', format='%(levelname)s - %(message)s', level=10)
try:
    import math
    import os
    from PIL import Image
    import numpy as np
    import random
    from resources import *
    # import psutil

except Exception as e:
    logging.error(e, exc_info=True)
    raise


class Camera:
    radian = math.pi / 180  # Useful to convert degres to radians
    def __init__(self, field, position, a=0, fov=80, res=(127 - 1, 230), rDis=False, colorGradient=True):
        print("Initiating camera!")
        self.field = field  # Instance of RenderField class
        x,y,z = position
        self.pos = (y,x,z)
        self.a = -a
        
        if self.a != 0:
            self.rotateAllPoints()
            
        self.fov = fov  # Field of view
        self.res = res  # Resolution
        
        if not rDis:  # rDis == render distance
            self.rDis = int(min(self.res[0], self.res[1]) / 2 / math.tan(self.fov / 2 * self.radian)) - 1
        else:
            self.rDis = rDis
            
        
        # I define "picture plane" as the plane containing all points to wich a ray is cast to check if it collides with anything solid
        self.ep = self.getEdgepoints()  # Dict with edge points of pictureplane
        self.pp = flattenList(self.getPictureplane())
        self.picture = [(0, 0, 0) for x in range(min(res[0], res[1]) ** 2)]  # [(v,v,v) for n, v in zip(range(min(res[0], res[1])**2),[random.randint(0,255) for x in range(min(res[0], res[1])**2)])]
        
        self.stepSize = int(len(self.picture) / 10)
        
        self.sil = list(range(len(self.pp)))
        random.shuffle(self.sil)
        
        self.colorGradient = colorGradient
        # self.sil.append((0,0,0))

    def getInfo(self):
        return f"position: {str(self.pos)}; fov: {str(self.fov)}; render distance: {str(self.rDis)}; render plane width: {str(self.ep['ab'])}; render mid point: {str(self.ep['mp'])}"

    def rotateAllPoints(self):
        print("Rotating points")
        oldPoints = self.field.drawnPixels
        newPoints = []
        for p in oldPoints:
            pos = self.pos
            pos = (pos[0], p[0][1], pos[2])
            newp = (rotatePoint(pos, p[0], self.a), p[1])
            newPoints.append(newp)
        self.field.clearField()
        self.field.drawnPixels = []
        for p in newPoints:
            self.field.drawPixel(p[0], p[1])

        print("done Rotating points")

    def getEdgepoints(self):  # Returns dict with picture plane edge points
        mp = (self.pos[0], self.pos[1], self.pos[2] + self.rDis)  # Gets mid point of picture plane
        ab = min(self.res[0], self.res[1])  # round(2*(self.rDis * math.tan(self.fov/2*(math.pi/180))))
        ad = ab
        return {"mp": mp, "a": (mp[0] + ab / 2, mp[1] + ad / 2, mp[2]), "b": (mp[0] - ab / 2, mp[1] + ad / 2, mp[2]),
                "d": (mp[0] + ab / 2, mp[1] - ad / 2, mp[2]), "c": (mp[0] - ab / 2, mp[1] - ad / 2, mp[2]), "ab": ab,
                "ad": ad}

    def getPictureplane(self):  # Returns 2d-list of points on picture plane
        return [[(self.ep["c"][0] + x, self.ep["c"][1] + y, self.ep["c"][2]) for y in range(self.ep["ad"])] for x in
                range(self.ep["ab"])]
                
                
    def pictureAsArray(self, steps=False):
        if not steps:
            steps = self.stepSize
        elif steps == 1:
            steps = len(self.picture)

        w = False

        usil = self.sil[:steps]
        self.sil = self.sil[steps:]
        
        if self.colorGradient:
           
            for n in usil:
                p = self.pp[n]
                
                line = self.field.drawLine(self.pos, p, False)
                for p2 in line:
                    try:
                        pixelColor = self.field.lookupColor(p2)
                        #print(pixelColor)
                        if pixelColor != (-1,-1,-1):#self.field.background:
                            bright = int(mapFunc(round(calcDistance(self.pos, p2)), 0, calcDist(self.pos, p), 0, 255))
                            self.picture[n] = (max(pixelColor[0] - bright, 0), max(pixelColor[1] - bright, 0), max(pixelColor[2] - bright, 0))
                            w = True
                            break
    
                    except Exception as e:
                        logging.error(e, exc_info=True)
                        raise
                        
                if not w:
                    self.picture[n] = (0, 0, 0)
                w = False
        else:
            for n in usil:
                p = self.pp[n]
                
                line = self.field.drawLine(self.pos, p, False)
                for p2 in line:
                    try:
                        pixelColor = self.field.lookupColor(p2)
                        #print(pixelColor)
                        if pixelColor != (-1,-1,-1):#self.field.background:
                            self.picture[n] = pixelColor 
                            w = True
                            break
    
                    except Exception as e:
                        logging.error(e, exc_info=True)
                        raise
                        
                if not w:
                    self.picture[n] = (0, 0, 0)
                w = False
            
    
        return self.picture

    def renderImage(self, name, consec=True, show=True):
        print("In render!")
        #roundNumber = 1
        if consec:

            def doRound(number):
                array = self.pictureAsArray()
                array = [array[i:i + self.ep["ab"]] for i in range(0, len(array), self.ep["ab"])]
                img = Image.fromarray(np.asarray(array, dtype=np.uint8))

                if show:
                    img.show()
            
            roundAmount = int(len(self.picture) / self.stepSize)
            for r in range(roundAmount):
                printProgressBar(r, roundAmount, prefix = 'Rendering:', suffix = 'Complete', length = 10)
                doRound(r)
                
                array = self.picture
                array = [array[i:i + self.ep["ab"]] for i in range(0, len(array), self.ep["ab"])]
                img = Image.fromarray(np.asarray(array, dtype=np.uint8))
                img.save(name + '.png')

            printProgressBar(roundAmount, roundAmount, prefix = 'Rendering:', suffix = 'Complete', length = 10)

            

        else:
            print("In render")
            array = self.pictureAsArray(1)
            # array = self.picture
            array = [array[i:i + self.ep["ab"]] for i in range(0, len(array), self.ep["ab"])]
            img = Image.fromarray(np.asarray(array, dtype=np.uint8))
            if show:
                img.show()
            img.save(name + '.png')
