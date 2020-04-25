#!/usr/bin/python3

import math
import random
import pygame
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

SCREENWIDTH = 1280
SCREENHEIGHT = 720
MAXBULLETS = 100

# Physics constants
# 8 pixels = 1m
FPS = 100
GRAVITY = (9.81*8)/FPS**2

# win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("First flight")

bg = pygame.image.load('images/kuva.png')
rocket1Image = pygame.image.load('images/rocket.png')
rocket2Image = pygame.image.load('images/rocket2.png')


pygame.mixer.set_num_channels(8)
thrust_voice1 = pygame.mixer.Channel(5)
thrust_voice2 = pygame.mixer.Channel(6)
thrust_sound = pygame.mixer.Sound('sfx/chopidle.wav')
bump_sound = pygame.mixer.Sound('sfx/bump.wav')

font = pygame.font.SysFont('VeraMono.ttf', 20, True)

clock = pygame.time.Clock()

class Vessel(object):

    def __init__(self, pnumber, x, y, bitmap):
        self.pnumber = pnumber
        self.x = x
        self.y = y
        self.width = bitmap.get_size()[0]
        self.height = bitmap.get_size()[1]
        self.xvel = 0
        self.yvel = 0
        self.thrust = GRAVITY * 3# + (12*8)/FPS**2
        self.originalImage = bitmap
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = 0
        self.hitradius = 10
        self.rocketsound = pygame.mixer.Channel(pnumber)
        self.shot = False

    def accelerate(self):
        self.xvel -= self.thrust * math.sin(math.radians(self.angle))
        self.yvel -= self.thrust * math.cos(math.radians(self.angle))

        # Make visual rocket burn and sound
        xvector = math.sin(math.radians(self.angle))
        yvector = math.cos(math.radians(self.angle))
        tailx = self.rect.center[0] + self.width * 0.5 * xvector
        taily = self.rect.center[1] + self.height * 0.5 * yvector
        flames.append(RocketBurn(tailx, taily, self.xvel + 2 * xvector + (random.random() - 0.5), self.yvel + 2 * yvector + (random.random() - 0.5)))
        if not self.rocketsound.get_busy():
            self.rocketsound.play(thrust_sound, -1)

    def shoot(self):
        xvector = math.sin(math.radians(self.angle))
        yvector = math.cos(math.radians(self.angle))
        frontx = self.rect.center[0] - self.width * 0.5 * xvector
        fronty = self.rect.center[1] - self.height * 0.5 * yvector
        projectiles.append(Bullet(frontx, fronty, self.xvel - 4 * xvector, self.yvel - 4 * yvector))

    def move(self):
        self.x += self.xvel
        self.y += self.yvel

    def handle(self, controls):
        # Handle controls
        if controls["up"]:
            self.accelerate()
        else:
            if self.rocketsound.get_busy():
                self.rocketsound.stop()

        if controls["left"]:
            self.angle += 2 % 360
        if controls["right"]:
            self.angle -= 2 % 360

        if controls["shoot"] and not self.shot:
            self.shoot()
            self.shot = True

        if not controls["shoot"]:
            self.shot = False

        # Add gravity
        self.yvel += GRAVITY

        # Check collisions
        if self.y + self.hitradius + self.yvel < SCREENHEIGHT and self.y - self.hitradius + self.yvel > 0:
            self.move()

        else:
            if self.y > SCREENHEIGHT - self.hitradius:
                self.y = SCREENHEIGHT - self.hitradius
            elif self.y < self.hitradius:
                self.y = self.hitradius

            if abs(self.yvel) > 40/FPS:
                self.yvel = -self.yvel * 0.5
                bump_sound.play()
            else:
                self.yvel = 0

            self.xvel *= 0.5
            self.move()

        if self.x > SCREENWIDTH:
            self.x -= SCREENWIDTH
        elif self.x < 0:
            self.x += SCREENWIDTH

    def update(self):

        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        # x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (self.x, self.y)  # Put the new rect's center at old center.

    def draw(self, frame):
        self.update()
        frame.blit(self.image, self.rect)
        # pygame.draw.rect(frame, (255, 0, 0), (self.rect[0] + (self.rect[2]//2), self.rect[1] + self.rect[3] //2, self.rect[2], self.rect[3]), 1)
        # tailx = int(self.rect.center[0] + self.height * 0.5 * math.sin(math.radians(self.angle)))
        # taily = int(self.rect.center[1] + self.height * 0.5 * math.cos(math.radians(self.angle)))
        # pygame.draw.circle(frame, (0, 255, 0), (tailx, taily), 5, 1)
        # pygame.draw.rect(frame, (255, 0, 0), self.rect, 1)
        # pygame.draw.circle(frame, (0, 255, 0), (int(self.x), int(self.y)), self.hitradius, 1)
        # offscreen from right
        if self.x + self.width > SCREENWIDTH:
            frame.blit(self.image, (self.rect[0] - SCREENWIDTH, self.rect[1], self.rect[2], self.rect[3]))
        # elif self.x < SCREENWIDTH:
        #     frame.blit(self.image, (self.rect[0] + SCREENWIDTH, self.rect[1], self.rect[2], self.rect[3]))

        return self.rect

class Bullet(object):
    def __init__(self, x, y, xvel, yvel):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.age = 0
        self.lifeTime = 1000
        self.color = (255, 255, 255)

    def move(self):
        # Add gravity
        self.yvel += GRAVITY

        self.x += self.xvel
        self.y += self.yvel

    def draw(self, frame):
        rect = pygame.draw.circle(frame, self.color, (int(self.x), int(self.y)), 0)
        return rect

    def handle(self):
        if self.age < self.lifeTime:
            self.move()
            self.age += 1
            return True
        else:
            # Bullet is old and should be killed
            return False

class RocketBurn(object):
    def __init__(self, x, y, xvel, yvel):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.age = 0
        self.lifeTime = 20
        self.color = (255, 255, 255)
        self.radius = 2
        self.opacity = 0

    def move(self):
        self.radius += 0.25
        # self.opacity = int((256 / self.lifeTime) * (self.lifeTime - self.age))
        self.x += self.xvel
        self.y += self.yvel

    def draw(self, frame):
        r = 0xff >> (self.age >> 4)
        g = 0xff >> (self.age >> 3)
        b = 0xff >> (self.age >> 2)
        return pygame.draw.circle(frame, (r, g, b), (int(self.x), int(self.y)), int(self.radius))

    def handle(self):
        if self.age < self.lifeTime:
            self.move()
            self.age += 1
            return True
        else:
            # Flame is old and should be killed
            return False


class Events(object):
    def __init__(self):
        self.run = True

        self.p1_controls = {"up": False,
                            "left": False,
                            "right": False,
                            "down": False,
                            "shoot": False}
        self.p2_controls = {"up": False,
                            "left": False,
                            "right": False,
                            "down": False,
                            "shoot": False}

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RCTRL:
                    self.p1_controls["shoot"] = True
                if event.key == pygame.K_LEFT:
                    self.p1_controls["left"] = True
                if event.key == pygame.K_UP:
                    self.p1_controls["up"] = True
                if event.key == pygame.K_RIGHT:
                    self.p1_controls["right"] = True
                if event.key == pygame.K_DOWN:
                    self.p1_controls["down"] = True

                if event.key == pygame.K_LCTRL:
                    self.p2_controls["shoot"] = True
                if event.key == pygame.K_a:
                    self.p2_controls["left"] = True
                if event.key == pygame.K_w:
                    self.p2_controls["up"] = True
                if event.key == pygame.K_d:
                    self.p2_controls["right"] = True
                if event.key == pygame.K_s:
                    self.p2_controls["down"] = True

                if event.key == pygame.K_ESCAPE:
                    self.run = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RCTRL:
                    self.p1_controls["shoot"] = False
                if event.key == pygame.K_LEFT:
                    self.p1_controls["left"] = False
                if event.key == pygame.K_UP:
                    self.p1_controls["up"] = False
                if event.key == pygame.K_RIGHT:
                    self.p1_controls["right"] = False
                if event.key == pygame.K_DOWN:
                    self.p1_controls["down"] = False

                if event.key == pygame.K_LCTRL:
                    self.p2_controls["shoot"] = False
                if event.key == pygame.K_a:
                    self.p2_controls["left"] = False
                if event.key == pygame.K_w:
                    self.p2_controls["up"] = False
                if event.key == pygame.K_d:
                    self.p2_controls["right"] = False
                if event.key == pygame.K_s:
                    self.p2_controls["down"] = False

newrects = []
oldrects = []

def redrawGameWindow():
    # pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREENWIDTH, SCREENHEIGHT))
    # pygame.draw.rect(win, (128, 128, 128), (0, 0, SCREENWIDTH, SCREENHEIGHT), 3)

    global newrects
    global oldrects

    for rect in oldrects:
        if rect[0] + rect[2] <= SCREENWIDTH and rect[0] >=0 and rect[1] >= 0 and rect[1] + rect[3] <= SCREENHEIGHT:
            dirtyrect = bg.subsurface(rect)
            win.blit(dirtyrect, rect)

    # win.blit(bg, (0, 0))
    for flame in flames:
        newrects.append(flame.draw(win))
    for projectile in projectiles:
        newrects.append(projectile.draw(win))
    newrects.append(player1.draw(win))
    newrects.append(player2.draw(win))
    text = font.render("xvel: " + '{:+.3f}'.format(player1.xvel) +
        " yvel: " + '{:+.3f}'.format(player1.yvel, 3) +
        " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    #    text = font.render("xvel: " + '{:+>10}'.format(str(round(player1.xvel, 3))) +
    #    " yvel: " + '{:+>10}'.format(str(round(player1.yvel, 3))) +
    #    " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    newrects.append(win.blit(text, (10, 700)))
    # print(oldrects+newrects)
    pygame.display.update(oldrects + newrects)
    # replace old rects with new rects
    oldrects = newrects[:]
    newrects.clear()



# Objects
events = Events()
flames = []
projectiles = []
player1 = Vessel(1, 540, 100, rocket1Image)
player2 = Vessel(2, 100, 100, rocket2Image)

# Update background
win.blit(bg, (0, 0))
pygame.display.update()

# Mainloop
while events.run:
    clock.tick(FPS)

    events.handle()
    player1.handle(events.p1_controls)
    player2.handle(events.p2_controls)

    for flame in flames:
        if not flame.handle():
            flames.pop(flames.index(flame))

    for projectile in projectiles:
            if not projectile.handle():
                projectiles.pop(projectiles.index(projectile))


    redrawGameWindow()