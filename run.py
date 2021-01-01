import time
startTime = time.time()
from Camera import Camera
from render import RenderField
from Light import Light
from resources import *
from ObjLoader import ObjLoader

# Console-view = (200,200,200)
# mode = "controll"

#fieldSize = (500,500,400)
#resu = (500, 500)
fieldSize = (300, 300, 250)
# resu = (470,470)
#fieldSize = (300,300,251)
resu = (300,300)


# z,y,x
f = RenderField(fieldSize)
fov = 80

f.drawCube((25,40,100),40)

if __name__ == "__main__":
    c = Camera(f, (0, 0, 0), a=0, fov=80, res=resu, colorGradient=True)#, drawOutline=False)
    
    c.renderImage("pic")
    
print(f"The execution took {time.time()-startTime} s / {(time.time()-startTime)/60} min!")
