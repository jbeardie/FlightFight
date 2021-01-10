#!/usr/bin/python3

import math
import random
import pygame
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

SCREENWIDTH = 1280
SCREENHEIGHT = 720
MAXPROJECTILES = 100

# Physics constants
# 8 pixels = 1m
FPS = 100
GRAVITY = (9.81*8)/FPS**2

win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
# win = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flight Fight")

# Images
bg = pygame.image.load('images/testmap.png').convert()
bgmask = pygame.mask.from_surface(pygame.image.load('images/testmap_mask.png'))
rocket1Image = pygame.image.load('images/rocket.png').convert_alpha()
rocket2Image = pygame.image.load('images/rocket2.png').convert_alpha()

# Sound effects
pygame.mixer.set_num_channels(8)
thrust_sound = pygame.mixer.Sound('sfx/chopidle.wav')
bump_sound = pygame.mixer.Sound('sfx/bump.wav')
shot_sound = pygame.mixer.Sound('sfx/shot.wav')
hit_channel = pygame.mixer.Channel(5)
hit_sound = []
hit_sound.append(pygame.mixer.Sound('sfx/hit-1.wav'))
hit_sound.append(pygame.mixer.Sound('sfx/hit-2.wav'))
hit_sound.append(pygame.mixer.Sound('sfx/hit-3.wav'))
explosion_sound = pygame.mixer.Sound('sfx/explosion.wav')

font = pygame.font.SysFont('VeraMono.ttf', 20, True)

clock = pygame.time.Clock()

class Vessel(pygame.sprite.Sprite):

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
        self.shotsound = pygame.mixer.Channel(pnumber+2)
        self.shot = False
        self.health = 100
        self.alive = True
        self.masksurf = pygame.Surface((self.hitradius*2, self.hitradius*2), pygame.SRCALPHA)
        # maskrect = pygame.draw.rect(self.masksurf, (0,0,255), self.masksurf.get_rect(), 1)
        maskCircle = pygame.draw.circle(self.masksurf, (255, 0, 0), (self.hitradius,self.hitradius), self.hitradius)
        self.mask = pygame.mask.from_surface(self.masksurf)
        self.hit = False

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
        projectiles.append(Projectile(frontx, fronty, self.xvel - 4 * xvector, self.yvel - 4 * yvector))
        if self.shotsound.get_busy():
            self.shotsound.stop()
        self.shotsound.play(shot_sound)

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

        # Cehck that the vessel is not outside screen height
        if self.y + self.hitradius + self.yvel < SCREENHEIGHT and self.y - self.hitradius + self.yvel > 0:
            self.x = self.x

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

        # Check if vessel hits to map mask in next loop
        futurex = self.x + self.xvel
        futurey = self.y + self.yvel
        xvel = self.xvel
        yvel = self.yvel
        hit = bgmask.overlap(self.mask, (int(futurex)-self.hitradius, int(futurey)-self.hitradius))
        while hit:
            # hitmatrix = [[bgmask.get_at((hit[0]-1, hit[1]-1)), bgmask.get_at((hit[0], hit[1]-1)), bgmask.get_at((hit[0]+1, hit[1]-1))],
            #     [bgmask.get_at((hit[0]-1, hit[1])), bgmask.get_at(hit), bgmask.get_at((hit[0]+1, hit[1]))],
            #     [bgmask.get_at((hit[0]-1, hit[1]+1)), bgmask.get_at((hit[0], hit[1]+1)), bgmask.get_at((hit[0]+1, hit[1]+1))]]
            
            # for i in hitmatrix:
            #     for j in i:
            #         print(j, end="")
            #     print()
            # print(self.x, self.xvel, self.y, self.yvel)
        
            if self.xvel >= 0 and self.yvel >= 0: # coming from upper left
                # print("NW")
                xcheck = bgmask.get_at((hit[0]-1, hit[1]))
                ycheck = bgmask.get_at((hit[0], hit[1]-1))
            elif self.xvel < 0 and self.yvel >= 0: # coming from upper right
                # print("NE")
                xcheck = bgmask.get_at((hit[0]+1, hit[1]))
                ycheck = bgmask.get_at((hit[0], hit[1]-1))
            elif self.xvel >= 0 and self.yvel <=0: # coming from lower left
                # print("SW")
                xcheck = bgmask.get_at((hit[0]-1, hit[1]))
                ycheck = bgmask.get_at((hit[0], hit[1]+1))
            else: # coming from lower right
                # print("SE")
                xcheck = bgmask.get_at((hit[0]+1, hit[1]))
                ycheck = bgmask.get_at((hit[0], hit[1]+1))

            if not xcheck and not ycheck: # corner hit
                if self.xvel >= 0 and self.yvel >= 0 or self.xvel < 0 and self.yvel < 0:
                    if abs(self.xvel) >= abs(self.yvel):
                        yvel = self.yvel
                        self.yvel = -self.xvel
                        self.xvel = yvel
                    else:
                        xvel = self.xvel
                        self.xvel = -self.yvel
                        self.yvel = xvel
                else:
                    if abs(self.xvel) >= abs(self.yvel):
                        yvel = self.yvel
                        self.yvel = self.xvel
                        self.xvel = -yvel
                    else:
                        xvel = self.xvel
                        self.xvel = self.yvel
                        self.yvel = -xvel

            elif xcheck and not ycheck: # vertical flat hit
                self.yvel = -self.yvel
            elif not xcheck and ycheck: # horizontal flat hit
                self.xvel = -self.xvel
            
            else: # Too much speed. Bounce the vessel back to original direction.
                self.xvel = -self.xvel
                self.yvel = -self.yvel
        
            # self.move()
            futurex = self.x + self.xvel
            futurey = self.y + self.yvel
            hit = bgmask.overlap(self.mask, (int(futurex)-self.hitradius, int(futurey)-self.hitradius))

            self.hit = True                

        self.move()

        if self.hit:
            hitforce = abs(xvel - self.xvel) + abs(yvel- self.yvel)
            if hitforce > 0.5:
                # print(hitforce)
                self.health -= int(hitforce)
                bump_sound.play()
            self.xvel *= 0.5
            self.yvel *= 0.5
            self.hit = False

        if self.x > SCREENWIDTH:
            self.x -= SCREENWIDTH
        elif self.x < 0:
            self.x += SCREENWIDTH

    def update(self):

        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (self.x, self.y)  # Put the new rect's center at old center.

    def draw(self, frame):
        self.update()
        frame.blit(self.image, self.rect)
        # frame.blit(self.masksurf, (self.rect.centerx-self.hitradius, self.rect.centery-self.hitradius))


        return self.rect
    
    def draw_healthbar(self, frame):
        healthbar = pygame.draw.rect(frame, (255, 0, 0), (self.x-13, self.y-24, 25, 6))
        if self.health >= 0:
            pygame.draw.rect(frame, (0, 255, 0), (self.x-13, self.y-24, 1 + self.health>>2, 6))
        
        return healthbar


    def explode(self):
        self.alive = False

        explosion_sound.play()

        particles = 100
        for x in range(particles):
            projectiles.append(Projectile(self.rect.center[0], self.rect.center[1], self.xvel + random.random()*4 - 2, self.yvel + random.random()*4 - 2))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, xvel, yvel):
        self.x = x
        self.y = y
        self.xvel = xvel
        self.yvel = yvel
        self.age = 0
        self.lifeTime = 1200
        self.color = (255, 255, 255)

    def move(self):
        # Add gravity
        self.yvel += GRAVITY

        self.x += self.xvel
        if self.x < 0:
            self.x += SCREENWIDTH
        elif self.x > SCREENWIDTH:
            self.x -= SCREENWIDTH
        self.y += self.yvel

    def draw(self, frame):
        # rect = pygame.draw.circle(frame, self.color, (int(self.x), int(self.y)), 0)
        self.rect = pygame.draw.rect(frame, self.color, (int(self.x), int(self.y), 2, 2), 1)
        return self.rect

    def hit_to_player(self, player):
        # Coarse hit check
        #if (player.x < self.x < player.x+player.width) and (player.y < self.y < player.y+player.height):
        # Radius hit check
        dx = abs(self.x-player.rect.center[0])
        dy = abs(self.y-player.rect.center[1])
        radius = player.hitradius

        # Check if the projectile is in the target square
        if dx < radius and dy < radius:
            # Check if the projectile is in the target circle
            if dx**2 + dy**2 <= radius**2:
                self.age = self.lifeTime
                dxvel = self.xvel - player.xvel
                dyvel = self.yvel - player.yvel
                magnitude = math.sqrt(dxvel**2 + dyvel**2)
                if hit_channel.get_busy():
                    hit_channel.stop()
                hit_channel.play(random.choice(hit_sound))
                player.health -= int(magnitude)
                player.xvel += self.xvel/16
                player.yvel += self.yvel/16
                # print("hit!", dxvel, dyvel, magnitude)


    def handle(self):
        
        # If projectile is not hitting a wall and not too old
        x = int(self.x)
        y = int(self.y)

        # This is a bug fix line
        if x > SCREENWIDTH-1:
            x -= SCREENWIDTH
        elif x < 0:
            x += SCREENWIDTH
        
        if y < 0 or y > SCREENHEIGHT-1:
            return False
        elif not bgmask.get_at((x, y)) and self.age < self.lifeTime:
            self.move()
            self.age += 1
            return True
        else:
            # Projectile is old and should be killed
            return False

class RocketBurn(pygame.sprite.Sprite):
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
    global newrects
    global oldrects

    # update background over dirty rectangles
    for rect in oldrects:
        if rect[0] < 0:
            rect[2] == rect[0] 
            rect[0] = 0
        if rect[0] + rect[2] > SCREENWIDTH:
            rect[2] -= rect[0] + rect[2] - SCREENWIDTH
        if rect[1] < 0:
            rect[3] += rect[1] 
            rect[1] = 0
        if rect[1] + rect[3] > SCREENHEIGHT:
            rect[3] -= rect[1] + rect[3] - SCREENHEIGHT
        dirtyrect = bg.subsurface(rect)
        win.blit(dirtyrect, rect)



    for flame in flames:
        newrects.append(flame.draw(win))
    for projectile in projectiles:
        newrects.append(projectile.draw(win))
    if player1.alive:
        newrects.append(player1.draw(win))
        newrects.append(player1.draw_healthbar(win))
    if player2.alive:
        newrects.append(player2.draw(win))
        newrects.append(player2.draw_healthbar(win))
    text = font.render("P1: " + str(player1.health) +
        " P2: " + str(player2.health) +
        " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    # text = font.render("xvel: " + '{:+.3f}'.format(player1.xvel) +
    #     " yvel: " + '{:+.3f}'.format(player1.yvel, 3) +
    #     " FPS: " + str(int(clock.get_fps())), 1, (0, 255, 0))
    newrects.append(win.blit(text, (10, 700)))
    pygame.display.update(oldrects + newrects)
    # replace old rects with new rects
    oldrects = newrects[:]
    newrects.clear()

# Objects
events = Events()
flames = []
projectiles = []
player1 = Vessel(1, 700, 100, rocket1Image)
player2 = Vessel(2, 200, 100, rocket2Image)

# Update background
win.blit(bg, (0, 0))

pygame.display.update()

# Mainloop
while events.run:
    clock.tick(FPS)

    if player1.alive and player1.health <= 0:
        events.p1_controls = {"up": False,
                            "left": False,
                            "right": False,
                            "down": False,
                            "shoot": False}
        player1.handle(events.p1_controls)
        player1.explode()
    
    if player2.alive and player2.health <= 0:
        events.p2_controls = {"up": False,
                            "left": False,
                            "right": False,
                            "down": False,
                            "shoot": False}
        player2.handle(events.p2_controls)
        player2.explode()


    events.handle()
    if player1.alive:
        player1.handle(events.p1_controls)
    if player2.alive:
        player2.handle(events.p2_controls)

    for flame in flames:
        if not flame.handle():
            flames.pop(flames.index(flame))

    for projectile in projectiles:
            if player1.alive:
                projectile.hit_to_player(player1)
            if player2.alive:
                projectile.hit_to_player(player2)
            if not projectile.handle():
                projectiles.pop(projectiles.index(projectile))


    redrawGameWindow()