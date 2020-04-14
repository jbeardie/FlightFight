#!/usr/bin/python3

import math
import random
import pygame
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

SCREENWIDTH = 640
SCREENHEIGHT = 480
MAXBULLETS = 100

# Physics constants
# 8 pixels = 1m
FPS = 100
GRAVITY = (9.81*8)/FPS**2

win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
# win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("First flight")

bg = pygame.image.load('images/bg.png')
rocket1Image = pygame.image.load('images/rocket.png')
rocket2Image = pygame.image.load('images/rocket2.png')


pygame.mixer.set_num_channels(8)
thrust_voice1 = pygame.mixer.Channel(5)
thrust_voice2 = pygame.mixer.Channel(6)
thrust_sound = pygame.mixer.Sound('sfx/chopidle.wav')
bump_sound = pygame.mixer.Sound('sfx/bump.wav')

font = pygame.font.SysFont('fixedsys', 20, True)

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

    def accelerate(self):
        self.xvel -= self.thrust * math.sin(math.radians(self.angle))
        self.yvel -= self.thrust * math.cos(math.radians(self.angle))

    def move(self):
        self.x += self.xvel
        self.y += self.yvel

    def handle(self, controls):
        if controls["up"]:
            self.accelerate()
            xvector = math.sin(math.radians(self.angle))
            yvector = math.cos(math.radians(self.angle))
            tailx = self.rect.center[0] + self.height * 0.5 * xvector
            taily = self.rect.center[1] + self.height * 0.5 * yvector
            # pygame.draw.circle(frame, (0, 255, 0), (tailx, taily), 5, 1)
            flames.append(RocketBurn(tailx, taily, self.xvel + 2 * xvector + (random.random() - 0.5), self.yvel + 2 * yvector + (random.random() - 0.5)))
            if not self.rocketsound.get_busy():
                self.rocketsound.play(thrust_sound, -1)
        else:
            if self.rocketsound.get_busy():
                self.rocketsound.stop()

        if controls["left"]:
            self.angle += 2 % 360
        if controls["right"]:
            self.angle -= 2 % 360

        self.yvel += GRAVITY

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

class RocketBurn(object):
    def __init__(self, x, y, xvel, yvel):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.age = 0
        self.lifeTime = 20
        self.color = (255, 255, 255)
        self.radius = 1
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
        pygame.draw.circle(frame, (r, g, b), (int(self.x), int(self.y)), int(self.radius))

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
                if event.key == pygame.K_SPACE:
                    self.p1_controls["shoot"] = True
                if event.key == pygame.K_LEFT:
                    self.p1_controls["left"] = True
                if event.key == pygame.K_UP:
                    self.p1_controls["up"] = True
                if event.key == pygame.K_RIGHT:
                    self.p1_controls["right"] = True
                if event.key == pygame.K_DOWN:
                    self.p1_controls["down"] = True

                if event.key == pygame.K_q:
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
                if event.key == pygame.K_SPACE:
                    self.p1_controls["shoot"] = False
                if event.key == pygame.K_LEFT:
                    self.p1_controls["left"] = False
                if event.key == pygame.K_UP:
                    self.p1_controls["up"] = False
                if event.key == pygame.K_RIGHT:
                    self.p1_controls["right"] = False
                if event.key == pygame.K_DOWN:
                    self.p1_controls["down"] = False

                if event.key == pygame.K_q:
                    self.p2_controls["shoot"] = False
                if event.key == pygame.K_a:
                    self.p2_controls["left"] = False
                if event.key == pygame.K_w:
                    self.p2_controls["up"] = False
                if event.key == pygame.K_d:
                    self.p2_controls["right"] = False
                if event.key == pygame.K_s:
                    self.p2_controls["down"] = False

def redrawGameWindow():
    global sc
    # pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREENWIDTH, SCREENHEIGHT))
    # pygame.draw.rect(win, (128, 128, 128), (0, 0, SCREENWIDTH, SCREENHEIGHT), 3)
    win.blit(bg, (0, 0))
    for flame in flames:
        flame.draw(win)
    player1.draw(win)
    player2.draw(win)
    text = font.render("xvel: " + '{:>10}'.format(str(round(player1.xvel, 3))) +
        " yvel: " + '{:>10}'.format(str(round(player1.yvel, 3))) +
        " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    win.blit(text, (10, 10))
    pygame.display.update()

# Objects
events = Events()
flames = []
player1 = Vessel(1, 540, 100, rocket1Image)
player2 = Vessel(2, 100, 100, rocket2Image)
screen_refresh = 0


# Mainloop
while events.run:
    clock.tick(FPS)

    events.handle()
    player1.handle(events.p1_controls)
    player2.handle(events.p2_controls)

    for flame in flames:
        if flame.age < flame.lifeTime:
            flame.move()
            flame.age += 1
        else:
            flames.pop(flames.index(flame))

    # collisions for p1
    if player1.y + player1.hitradius + player1.yvel < SCREENHEIGHT and player1.y - player1.hitradius + player1.yvel > 0:
        player1.move()

    else:
        if player1.y > SCREENHEIGHT - player1.hitradius:
            player1.y = SCREENHEIGHT - player1.hitradius
        elif player1.y < player1.hitradius:
            player1.y = player1.hitradius

        if abs(player1.yvel) > 40/FPS:
            player1.yvel = -player1.yvel * 0.5
            bump_sound.play()
        else:
            player1.yvel = 0
        player1.xvel *= 0.5
        player1.move()

    if player1.x > SCREENWIDTH:
        player1.x -= SCREENWIDTH
    elif player1.x < 0:
        player1.x += SCREENWIDTH

    # collisions for p2
    if player2.y + player2.hitradius + player2.yvel < SCREENHEIGHT and player2.y - player2.hitradius + player2.yvel > 0:
        player2.move()

    else:
        if player2.y > SCREENHEIGHT - player2.hitradius:
            player2.y = SCREENHEIGHT - player2.hitradius
        elif player2.y < player2.hitradius:
            player2.y = player2.hitradius

        if abs(player2.yvel) > 40/FPS:
            player2.yvel = -player2.yvel * 0.5
            bump_sound.play()
        else:
            player2.yvel = 0
        player2.xvel *= 0.5
        player2.move()

    if player2.x > SCREENWIDTH:
        player2.x -= SCREENWIDTH
    elif player2.x < 0:
        player2.x += SCREENWIDTH

    if screen_refresh == 1:
        redrawGameWindow()
        screen_refresh = 0
    screen_refresh += 1