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

pygame.mixer.set_num_channels(8)
thrust_voice = pygame.mixer.Channel(5)
thrust_sound = pygame.mixer.Sound('sfx/chopidle.wav')
bump_sound = pygame.mixer.Sound('sfx/bump.wav')

font = pygame.font.SysFont('fixedsys', 20, True)

clock = pygame.time.Clock()

class Vessel(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self. height = height
        self.xvel = 0
        self.yvel = 0
        self.thrust = GRAVITY * 2# + (12*8)/FPS**2
        self.originalImage = pygame.image.load('images/rocket.png')
        self.image = self.originalImage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = 0
        self.hitradius = 10

    def accelerate(self):
        self.xvel -= self.thrust * math.sin(math.radians(self.angle))
        self.yvel -= self.thrust * math.cos(math.radians(self.angle))

    def move(self):
        self.x += self.xvel
        self.y += self.yvel

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
        self.p1_up = False
        self.p1_left = False
        self.p1_right = False
        self.p1_down = False
        self.p1_space = False

    def handle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.p1_space = True
                if event.key == pygame.K_LEFT:
                    self.p1_left = True
                if event.key == pygame.K_UP:
                    self.p1_up = True
                if event.key == pygame.K_RIGHT:
                    self.p1_right = True
                if event.key == pygame.K_DOWN:
                    self.p1_down = True
                if event.key == pygame.K_ESCAPE:
                    self.run = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.p1_space = False
                if event.key == pygame.K_LEFT:
                    self.p1_left = False
                if event.key == pygame.K_UP:
                    self.p1_up = False
                if event.key == pygame.K_RIGHT:
                    self.p1_right = False
                if event.key == pygame.K_DOWN:
                    self.p1_down = False

def redrawGameWindow():
    # pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREENWIDTH, SCREENHEIGHT))
    # pygame.draw.rect(win, (128, 128, 128), (0, 0, SCREENWIDTH, SCREENHEIGHT), 3)
    win.blit(bg, (0, 0))
    for flame in flames:
        flame.draw(win)
    player.draw(win)
    text = font.render("xvel: " + '{:>10}'.format(str(round(player.xvel, 3))) +
        " yvel: " + '{:>10}'.format(str(round(player.yvel, 3))) +
        " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    win.blit(text, (10, 10))

    pygame.display.update()

# Objects
events = Events()
flames = []
player = Vessel(100, 100, 31, 31)
screen_refresh = 0

# Mainloop
while events.run:
    clock.tick(FPS)

    events.handle()

    if events.p1_up:
        player.accelerate()
        xvector = math.sin(math.radians(player.angle))
        yvector = math.cos(math.radians(player.angle))
        tailx = player.rect.center[0] + player.height * 0.5 * xvector
        taily = player.rect.center[1] + player.height * 0.5 * yvector
        # pygame.draw.circle(frame, (0, 255, 0), (tailx, taily), 5, 1)
        flames.append(RocketBurn(tailx, taily, player.xvel + 2 * xvector + (random.random() - 0.5), player.yvel + 2 * yvector + (random.random() - 0.5)))
        if not thrust_voice.get_busy():
            thrust_voice.play(thrust_sound, -1)
    else:
        if thrust_voice.get_busy():
            thrust_voice.stop()

    if events.p1_left:
        player.angle += 2 % 360
    if events.p1_right:
        player.angle -= 2 % 360
    # if events.p1_space:

    for flame in flames:
        if flame.age < flame.lifeTime:
            flame.move()
            flame.age += 1
        else:
            flames.pop(flames.index(flame))

    player.yvel += GRAVITY

    # collisions
    if player.y + player.hitradius + player.yvel < SCREENHEIGHT and player.y - player.hitradius + player.yvel > 0:
        player.move()

    else:
        if player.y > SCREENHEIGHT - player.hitradius:
            player.y = SCREENHEIGHT - player.hitradius
        elif player.y < player.hitradius:
            player.y = player.hitradius

        if abs(player.yvel) > 40/FPS:
            player.yvel = -player.yvel * 0.5
            bump_sound.play()
        else:
            player.yvel = 0
        player.xvel *= 0.5
        player.move()

    if player.x > SCREENWIDTH:
        player.x -= SCREENWIDTH
    elif player.x < 0:
        player.x += SCREENWIDTH

    if screen_refresh == 1:
        redrawGameWindow()
        screen_refresh = 0
    screen_refresh += 1