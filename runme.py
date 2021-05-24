import pygame
import math
from ray_class import Ray
from boundary_class import Boundary
import numpy as np

FPS = 60
Window = None
HospitalImage = pygame.image.load("../CreativityProject/Sanatoriam.jpg")
Startingx = 2700
Startingy = 360

#if True, it's in first person. if false, it's in top down view
IsFPDisplay = True

#angle that the player can see, also how many rays are cast out
FieldOfView = 100

#speeds
MovementSpeed = 1
TurningSpeed = 2

#if true, the 3d graphics adjust for fish eye effect
IsFishEyeCorrection = True
PerformanceValue = 0.8

#colors
skyvalue1 = 85
skyvalue2 = 109
skyvalue3 = 255

SquareColor = (188, 90, 13)
DarkSquareColor = (141, 50, 0)
FloorColor = (210, 190, 0)
SkyColor = (skyvalue1, skyvalue2, skyvalue3)
RayColor = (0, 255, 0) #green
PlayerColor = (0, 0, 255) #dark blue

WindowHeight = 500
WindowLength = 500
SquareNumber = 8
UnitLength = WindowLength / SquareNumber


#here's the map. if you rotate this grid 90' clockwise and flip it, you'll get the rendered map
mapArray = [[1, 1, 1, 1, 1, 1, 1, 1], 
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 0, 1, 1, 1]]

additionalrects = [pygame.Rect(1200, 250, 200, 10), 
                    pygame.Rect(1500, 275, 10, 10),
                    pygame.Rect(1800, 225, 20, 20),
                    pygame.Rect(1600, 270, 5, 5),
                    pygame.Rect(2000, 300, 10, 20),
                    pygame.Rect(2100, 315, 5, 5),
                    pygame.Rect(2400, 335, 10, 10)]

#creates all of the rectangles
activeRectangles = []
def CreateRectangles():
    for i in range(len(mapArray)):
        for j in range(len(mapArray[i])):
            if mapArray[i][j] == 1:
                thisrectangle = pygame.Rect(i * (WindowLength / len(mapArray)), j * (WindowHeight / len(mapArray[i])), WindowLength / len(mapArray), WindowHeight / len(mapArray[i]))
                activeRectangles.append(thisrectangle)
    for k in additionalrects:
        activeRectangles.append(k)

def DrawRectangles():
    for rectangles in activeRectangles:
        pygame.draw.rect(Window, SquareColor, rectangles)

activeBoundaries = []
def CreateBoundaries():
    for rectangles in activeRectangles:
        topboundary = Boundary(rectangles.x, rectangles.y, rectangles.x + rectangles.width, rectangles.y)
        bottomboundary = Boundary(rectangles.x, rectangles.y + rectangles.height, rectangles.x + rectangles.width, rectangles.y + rectangles.height)
        leftboundary = Boundary(rectangles.x, rectangles.y, rectangles.x, rectangles.y + rectangles.height)
        rightboundary = Boundary(rectangles.x + rectangles.width, rectangles.y, rectangles.x + rectangles.width, rectangles.y + rectangles.height)
        activeBoundaries.extend([topboundary, bottomboundary, leftboundary, rightboundary])

         
def DrawPlayer(player):
    pygame.draw.circle(Window, PlayerColor, player.center, player.radius)

def DrawRays(rayarray):
    for ray in rayarray:
        pygame.draw.line(Window, RayColor, (ray.startingx, ray.startingy), (ray.endx, ray.endy), 1)

def DrawTopDownBackground():
    bg = pygame.Rect(0, 0, WindowLength, WindowHeight)
    pygame.draw.rect(Window, FloorColor, bg)

def TopDownGraphics(player, rayarray):
    DrawTopDownBackground()
    DrawRectangles()
    DrawRays(rayarray)
    DrawPlayer(player)

#handles the calculation and display of first person graphics
iiidrects = []
def FPGraphics(arraydistances):
    iiidrects.clear()
    rectwidth = WindowLength / len(arraydistances)
    multiplier = 10000
    for ii in range(len(arraydistances)):
        rectheight = multiplier * (1 / arraydistances[ii])
        if rectheight < 0:
            rectheight = rectheight * -1
        iiidrects.append(pygame.Rect(rectwidth * ii, (WindowHeight / 2) - (rectheight / 2), rectwidth, rectheight))
    
    #this part determines which color the rectangles should be by comparing them to adjacent rectangles
    for ii in range(len(iiidrects)):
        if ii >= len(iiidrects):
            if iiidrects[ii].height > iiidrects[ii - 1].height:
                pygame.draw.rect(Window, SquareColor, iiidrects[ii])
            else:
                pygame.draw.rect(Window, DarkSquareColor, iiidrects[ii])
        else:
            if iiidrects[ii].height < iiidrects[ii - 1].height:
                pygame.draw.rect(Window, SquareColor, iiidrects[ii])
            else:
                pygame.draw.rect(Window, DarkSquareColor, iiidrects[ii])

def DrawFloor():
    floor = pygame.Rect(0, WindowHeight / 2, WindowLength, WindowHeight / 2)
    pygame.draw.rect(Window, FloorColor, floor)

def HospitalGraphics():
    Window.blit(HospitalImage, (0, 0))
    

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 2
        self.center = (self.x, self.y)
        self.angle = 180
        self.visionwidth = FieldOfView
        self.anglevelocity = TurningSpeed
        self.velocity = MovementSpeed
        self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
        self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
        self.rayarray = []
        self.allraydistances = []
        self.correctarraydistances = []
        self.quadrent = 1

        self.PopulateRayArray()
        
    def AngleCorrection(self):
        if self.angle < 0:
            self.angle == 359
        elif self.angle > 360:
            self.angle == 1
            
    def Move(self, keys_pressed):
        anglemovment = 0
        if keys_pressed[pygame.K_RIGHT]:
            self.angle += self.anglevelocity
            anglemovment = self.anglevelocity
        if keys_pressed[pygame.K_LEFT]:
            self.angle -= self.anglevelocity
            anglemovment = -self.anglevelocity
        if keys_pressed[pygame.K_DOWN]:
            self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
            self.x -= self.x_movement_amount
            self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
            self.y -= self.y_movment_amount
        if keys_pressed[pygame.K_UP]:
             self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
             self.x += self.x_movement_amount
             self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
             self.y += self.y_movment_amount

        if self.angle > 360:
            self.angle = 0 + self.anglevelocity

        if self.angle < 0:
            self.angle = 360 - self.anglevelocity

        self.center = (self.x, self.y)
        #self.UpdateQuadrent()
        self.CastingRays()
        self.UpdateRayArray(anglemovment)
        self.RayCorrection()

    def PopulateRayArray(self):
        for ii in np.arange((-self.visionwidth // 2) + self.angle, (self.visionwidth // 2) + self.angle, PerformanceValue):
            self.rayarray.append(Ray(self.x, self.y, ii))

    def UpdateRayArray(self, anglemovment):
        for rays in self.rayarray:
            rays.Update(self.x, self.y, rays.angle + anglemovment)

    def CastingRays(self):
        self.allraydistances.clear()
        for rays in self.rayarray:
            self.allraydistances.append(FindRayDistance(rays))

    def RayCorrection(self):
        self.correctarraydistances.clear()
        for ii in range(len(self.allraydistances)):
            self.correctarraydistances.append(self.allraydistances[ii] * math.cos(math.radians(self.rayarray[ii].angle - self.angle)))

    '''
    def UpdateQuadrent(self):
        global checks
        checks += 1
        if self.angle >= 0 and self.angle < 90:
            self.quadrent = 4
        elif self.angle >= 90 and self.angle < 180:
            self.quadrent = 3
        elif self.angle >= 180 and self.angle < 270:
            self.quadrent = 2
        else:
            self.quadrent = 1
    '''
        

#returns a filtered list of boundaries that should be checked. 
#all boundaries that do not need to be checked will be filtered out
#nevermind, this actually does more harm than good and will not be implemented
def BoundaryFilter(x, y, quadrent):
    filteredboundaries = []
    for wall in activeBoundaries:
        global checks
        checks += 1
        if quadrent == 1:
            if wall.startingx > x or wall.startingy < y:
                filteredboundaries.append(wall)
        elif quadrent == 2:
            if wall.startingx < x or wall.startingy < y:
                filteredboundaries.append(wall)
        elif quadrent == 3:
            if wall.startingx < x or wall.startingy > y:
                filteredboundaries.append(wall)
        else:
            if wall.startingx > x or wall.startingy > y:
                filteredboundaries.append(wall)
    return filteredboundaries
            


def FindRayDistance(ray):
    ray.distances.clear()
    #loops through every wall and determines whether an indefinite ray would hit it. if yes, it adds the distance to that wall to an array of distances
    #searchBoundaries = []
    for wall in activeBoundaries:
        x1 = wall.startingx
        y1 = wall.startingy
        x2 = wall.endingx
        y2 = wall.endingy
        x3 = ray.startingx
        y3 = ray.startingy
        x4 = ray.endx
        y4 = ray.endy

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            continue

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if (t > 0 and t < 1 and u > 0):
            ptx = x1 + t * (x2 - x1)
            pty = y1 + t * (y2 - y1)
            dis = math.sqrt(((ptx - ray.startingx) ** 2) + ((pty - ray.startingy) ** 2))
            ray.distances.append(dis)
        else:
            continue
    
    #finds the shortest distance out of the array and returns it
    ray.length = 10000
    for diss in ray.distances:
        if diss < ray.length:
            ray.length = diss
    return ray.length



def gameloop():
    MainPlayer = Player(Startingx, Startingy)
    CreateRectangles()
    CreateBoundaries()
    global IsFPDisplay
    global SquareColor
    global DarkSquareColor
    global FloorColor
    global SkyColor
    global skyvalue1
    global skyvalue2
    global skyvalue3

    secondtimer = 0
    ticker = 0
    storyticker = 0

    clock = pygame.time.Clock() 
    run = True
    while run == True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #changes the perspective when you click the space key
            #changes the color when you click the number keys
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if IsFPDisplay == True:
                            IsFPDisplay = False
                        else:
                            IsFPDisplay = True
                    
        #happens every loop
        keys_pressed = pygame.key.get_pressed()
        MainPlayer.Move(keys_pressed)
        
        Window.fill(SkyColor)
        if IsFPDisplay == True:
            if IsFishEyeCorrection:
                DrawFloor()
                FPGraphics(MainPlayer.correctarraydistances)
            else:
                DrawFloor()
                FPGraphics(MainPlayer.allraydistances)
        else:
            #TopDownGraphics(MainPlayer, MainPlayer.rayarray)
            HospitalGraphics()
               
        pygame.display.update()

        ticker += 1
        if ticker == 8:
            ticker = 0
            if skyvalue1 > 0:
                skyvalue1 -= 1
            if skyvalue2 > 0:
                skyvalue2 -= 1
            if skyvalue3 > 0:
                skyvalue3 -= 1
            SkyColor = (skyvalue1, skyvalue2, skyvalue3)

        storyticker += 1
        if storyticker == 60:
            secondtimer += 1
            StoryHandler(secondtimer)
            storyticker = 0
            

def StoryHandler(SecondNumber):
    printedstatment = ""
    if SecondNumber == 3:
        printedstatment = "Dahlmann accepted the walk as a small adventure."
    elif SecondNumber == 6:
        printedstatment = "[Use the arrow keys to move and look around]"
    elif SecondNumber == 15:
        printedstatment = "The sun had already dissapeared from view"
    elif SecondNumber == 20:
        printedstatment = "but a final splendor, exalted the vivid and silent plain"
    elif SecondNumber == 30:
        printedstatment = "before the night erased its color."
    elif SecondNumber == 35:
        printedstatment = "Less to avoid fatigue than to draw out his enjoyment of these sights, Dahmann walked slowly"
    elif SecondNumber == 43:
        printedstatment = "breathing in the oder of clover with sumptuous joy"
    elif SecondNumber == 60:
        printedstatment = "Press the space key"
    elif SecondNumber == 61:
        printedstatment = "Press the space key"
    elif SecondNumber == 62:
        printedstatment = "Press the space key"
    elif SecondNumber == 63:
        printedstatment = "Press the space key"
    elif SecondNumber == 64:
        printedstatment = "Press the space key"
    elif SecondNumber == 70:
        printedstatment = "Is this an honorable death?"

    print(printedstatment)

        

def main():
    global Window
    Window = pygame.display.set_mode((WindowLength, WindowHeight))
    gameloop()

if __name__ == "__main__":
    #write main() here
    main()
    