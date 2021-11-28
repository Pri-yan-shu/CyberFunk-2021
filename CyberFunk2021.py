'''
CyberFunk 2021.exe

The source lacks OOP.
Also some variables are passed to functions and some are just accessed globally because I stopped caring halfway.

CyberFunk 2021, None Rights Reserved.
'''

import ctypes
import time
import os
import enum
import math
import time
import itertools
import random

#Variables

AlienLimit = 10
StageSize = (60,30)
Score = 0
Level = 1
GameStatus = 1
VBorder = ['| |', '| |','|v|']
HBorder = [['  <',' < ','<  '],['>  ',' > ','  >']]
SpriteList = []
AlienList = []
FireList = []
AnimationList = []
StageList = [[' ' for _ in range(StageSize[0])] for _ in range(StageSize[1])]
SpriteGraphics = [
    
[[' | iAi=#='],['  A   /8\\ /|W|\\A=+=A^   ^','  A   /8\\ /|M|\\A=x=A*   *']],
[['\\i/=8="^"','_l_>O<`^`'],['\___//=O=\\\\___/// \\\\A   A','\___//O==\\\\___/|| || A A ','\___//=O=\\\\___/\\\\ //  M  ','\___//==O\\\\___/|| || A A ']],
[['^'],['A'],['*'],list('POWERUP')]   ,                                                
[[symb*((2*x + 1)**2) for symb in ' .o0O@' ] for x in range(3)]
# Generates the animation graphics by listcomp
]

#Game Functions

def printStage(StageList,Frame):
    # Print the frame into the terminal

    Frame = Frame % 3
    for _ in range(StageSize[0]+2*len(VBorder)): print('-',end='')
    print()
    for _ in range((StageSize[0] + 2*len(VBorder))//6 + 1): print(HBorder[0][Frame],end='')
    for _ in range((StageSize[0] + 2*len(VBorder))//6): print(HBorder[1][Frame],end='')
    print()
    for _ in range(StageSize[0]+2*len(VBorder)): print('-',end='')
    print()

    # Print the StageList contents with their colors.
    for x,row in enumerate(StageList):
        print(VBorder[(x-Frame)%3],end='')
        for pixel in row:
            if len(pixel) == 1:
                print(pixel, end='')
            else:
                print(f'\033[0;9{pixel[1]}m{pixel[0]}\033[0m',end='')
        print(VBorder[(x-Frame)%3],end='')
        print()

    for _ in range(StageSize[0]+2*len(VBorder)): print('-',end='')
    print()
    print(f'Score:{Score}\t\tLevel:{Level}\t\t\tHP:{SpriteList[0][0]["HP"]}')
    print()
    for _ in range(StageSize[0]+2*len(VBorder)): print('-',end='')

    if GameStatus == 0:
        print('GameOver')

def clearStage(StageList):
    # Clear previous frame
    for y in range(StageSize[1]):
        for x in range(StageSize[0]):
            StageList[y][x] = ' '

def gameLoop(StageList, SpriteList,):
    # Run the game processes

    Alternate = itertools.cycle(range(30))

    while(GameStatus and not ctypes.windll.User32.GetAsyncKeyState(0x42)):
        Frame = next(Alternate)
        clearStage(StageList)
        printSprite(StageList, SpriteList)
        os.sys.stdout.flush()
        time.sleep(.05)

        shipRoutine(SpriteList[0][0],SpriteList[2],Frame)
        fireRoutine(SpriteList[2])
        alienRoutine(SpriteList[1],AlienLimit, Frame, SpriteList[2])
        animationRoutine(SpriteList[3])
        offscreenCheck(SpriteList)

        os.system('cls')
        printStage(StageList,Frame)
        controller()

#Sprite Functions

class Catg(enum.Enum):
    #Enum for sprite categories
    SHIP = 0
    ALIEN = 1
    PROJECTILE = 2
    ANIMATION = 3

def newSprite(Cat, HP, Hitbox, Position, Graphics = 0, Costume = 0, Color = 0, Parent = None):
    if Cat != Catg.PROJECTILE:
        return {'Catg': Cat, 'HP':HP, 'Hitbox':Hitbox, 'Position':Position, 'Graphics':Graphics, 'Costume':Costume, 'Color':Color}
    return {'Catg': Cat, 'HP':HP, 'Hitbox':Hitbox, 'Position':[Parent['Position'][0],Parent['Position'][1] + math.ceil(Parent['Hitbox']/2)*(-1 if Parent['Catg'].value == 0 else 1)], 'Parent':Parent, 'Graphics':Graphics, 'Costume':Costume, 'Color':Color}

def printSprite(StageList,SpriteList):
    # Print the sprite to the StageList as a tuple (Character,Color)

    for CatgList in SpriteList:
        for Sprite in CatgList:
            for z in range(Sprite['Hitbox']**2):
                #y & x are the pseudo 2d pointer to the imaginary 2d graphic list made from the 1d list.
                x,y = divmod(z,Sprite['Hitbox'])
                #y & xPointer point to the place on StageList which bears the character of sprite
                yPointer = Sprite['Position'][1] + y - (Sprite['Hitbox'])//2
                xPointer = Sprite['Position'][0] + x - (Sprite['Hitbox'])//2

                if(xPointer >= 0 and xPointer < StageSize[0] and yPointer >= 0 and yPointer < StageSize[1]):
                    StageList[yPointer][xPointer] = (SpriteGraphics[Sprite['Catg'].value][Sprite['Graphics']][Sprite['Costume']][x + y*Sprite['Hitbox']],Sprite['Color'])

def nextCostume(Sprite):
    # Cycle through costumes.
    if len(SpriteGraphics[Sprite['Catg'].value][Sprite['Graphics']]) > (Sprite['Costume'] + 1):
        Sprite['Costume'] += 1
    else:
        Sprite['Costume'] = 0

def collisionCheck(Sprite1, Sprite2):
    # Check if any two sprites are colliding
    if abs(Sprite1['Position'][1] - Sprite2['Position'][1])-1 < abs(Sprite1['Hitbox']//2 + Sprite2['Hitbox']//2) and abs(Sprite1['Position'][0] - Sprite2['Position'][0])-1 < abs(Sprite1['Hitbox']//2 + Sprite2['Hitbox']//2):
        return True

def offscreenCheck(SpriteList):
    # Check if any sprite except ship is vertically offscreen
    for CatgList in SpriteList:
        for Sprite in CatgList:
            if (Sprite['Position'][1] <= 0 or Sprite['Position'][1] >= StageSize[1]) and not (Sprite['Catg'] == Catg.SHIP):
                CatgList.remove(Sprite)

def disintegrate(Sprite):
    # Remove sprite and animate explosion
    newAnimation(Sprite,'Explosion')
    if Sprite in SpriteList[Sprite['Catg'].value]:
        SpriteList[Sprite['Catg'].value].remove(Sprite)

# Ship functions

def shipRoutine(Ship,FireList,Frame):
    nextCostume(SpriteList[0][0])

    #Check if the ship is big, small or dead
    if Ship['HP'] == 0:
        GameStatus = 0
    elif Ship['HP'] > 4:
        Ship['Hitbox'] = 5
        Ship['Graphics'] = 1
        Ship['Power'] = 2
    else:
        Ship['Hitbox'] = 3
        Ship['Graphics'] = 0
        Ship['Costume'] = 0
        Ship['Power'] = 1

    # Collision check with enemy projectiles
    for Shot in FireList:
            if collisionCheck(Ship, Shot):
                if Shot['HP'] < 0:
                    if Ship['HP'] != 5:
                        newAnimation(Ship,'Damage')
                    else:
                        newAnimation(Ship,'Explosion')
                disintegrate(Shot)
                Ship['HP'] += Shot['HP']

    # Shoot
    if not Frame % 4:
        addFire(SpriteList[2], SpriteList[0][0],-Ship['Power'])
    
def controller():
    # Wait for user input for 1 millisecond then continue with game 
    state = ctypes.windll.User32.GetAsyncKeyState
    pos = SpriteList[0][0]['Position']
    Lap = time.perf_counter()

    while(time.perf_counter() - Lap) < .001:
        if(state(0x41) and pos[0] >= 0):
            pos[0] += -2
            time.sleep(.001)
        if(state(0x53) and pos[1] < StageSize[1]):
            pos[1] += 1
            time.sleep(.01)
        if(state(0x44)and pos[0] < StageSize[0]):
            pos[0] += 2
            time.sleep(.001)
        if(state(0x57) and pos[1] >= 0):
            pos[1] -= 1
            time.sleep(.01)

#Shot functions

def addFire(FireList, Sprite, HP = -1):
    # Deal with enemy projectile/powerup
    if Sprite['Catg'] == Catg.ALIEN:
        if HP > 0:
            Graphics = 3
            Colour = 2
        else:
            Graphics = 2
            Colour = 1

        FireList.append(newSprite(Catg.PROJECTILE,HP,1,'Position',Graphics,0,Colour,Sprite))
    # Deal with ship projectile
    else:
        if Sprite['HP'] >= 5:
            Graphics = 1
        else:
            Graphics = 0
        FireList.append(newSprite(Catg.PROJECTILE,HP,1,'Position',Graphics,0,2,Sprite))

def fireRoutine(FireList):
    # Move all projectiles in their respective directions
    if FireList:
        for Shot in FireList:
            nextCostume(Shot)
            if Shot['Parent']['Catg'].value == 0:
                Shot['Position'][1] -= 1
            else:
                Shot['Position'][1] += 1

# Alien functions

def spawnAlien(AlienList,AlienLimit):
    # Spawn aliens randomly at random position till limit
    if len(AlienList) < AlienLimit:
        # Randomize alien type
        AlienType = random.randint(0,1)
        if AlienType == 0:
            NewAlien = newSprite(Catg.ALIEN,3,3,[0,1],0,Color=random.choice((0,4,5,6)))
        elif AlienType == 1:
            NewAlien = newSprite(Catg.ALIEN,5,5,[0,1],1,Color=random.choice((0,4,5,6)))
        NewAlien['Position'][0] = random.randint(0,StageSize[0])

        # Check that the spawn position is not preoccupied
        if not brethrenCollision(NewAlien,AlienList):
            AlienList.append(NewAlien)

def brethrenCollision(Alien,AlienList):
    isColliding = False

    for Brethren in AlienList:
        if Brethren != Alien and not isColliding:
            isColliding = collisionCheck(Alien,Brethren)

    return isColliding


def alienRoutine(AlienList, AlienLimit, Frame, FireList):
    if not random.randint(0,5):
        spawnAlien(AlienList, AlienLimit)

    # Randomly fire and assign projectile to random alien
    if SpriteList[1] and not random.randint(0,4):
        addFire(SpriteList[2], SpriteList[1][random.randint(0,len(AlienList) - 1)])

    for Alien in AlienList:
        if not Frame%2:
            randomHStep(Alien)
        if not Frame % 30:
            VStep(Alien)

        # Check collision and do collision and score stuff
        for Shot in FireList:
            if Shot['Catg'] != Catg.ALIEN:
                if collisionCheck(Alien, Shot):
                    newAnimation(Alien,'Damage')
                    Alien['HP'] += Shot['HP']
                    disintegrate(Shot)
                    global Score
                    Score += 1
                    if Alien['HP'] < 1:
                        if not random.randint(0,4):
                            addFire(FireList,Alien,1)
                        disintegrate(Alien)
                        Score += 10
        if not Frame % 4: nextCostume(Alien)


def randomHStep(Alien):
    #If the alien doesnt collide with others then move randomly
    Step = random.randint(-1,1)
    if (Alien['Position'][0] + Step) > 0 and (Alien['Position'][0] + Step) < StageSize[0]:
        Alien['Position'][0] += Step
        if brethrenCollision(Alien,SpriteList[1]):
            Alien['Position'][0] -= Step


def VStep(Alien):
    # Step down
    if Alien['Position'][1] < StageSize[1]:
        Alien['Position'][1] += 1

#Animation functions

def newAnimation(Sprite,type):
    # Spawn a short lived sprite of highest priority with no routines except costume cycle
    if type == 'Explosion':
        SpriteList[3].append(newSprite(Catg.ANIMATION,6,Sprite['Hitbox'],Sprite['Position'],int((Sprite['Hitbox']-1)/2),Color=3))
    elif type == 'Damage':
        SpriteList[3].append(newSprite(Sprite['Catg'],2,Sprite['Hitbox'],Sprite['Position'],Sprite['Graphics'],Color=1))

def animationRoutine(AnimationList):
    # Animate the animation sprite
    for Animation in AnimationList:
        nextCostume(Animation)
        Animation['HP'] -= 1
        if Animation['HP'] == 0:
            AnimationList.remove(Animation)

def main():
    SpriteList.append([newSprite(Catg.SHIP,3,5,[25,18],1,0,2)])
    SpriteList.append(AlienList)
    SpriteList.append(FireList)
    SpriteList.append(AnimationList)

    gameLoop(StageList,SpriteList)

if __name__ == '__main__':
    main()