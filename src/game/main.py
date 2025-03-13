import pygame
import sys
import math
import random
from pygame.locals import *

mainClock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((500, 500), 0, 32)

sparks = []

class Spark():
    def __init__(self, loc, angle, speed, color, scale=1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def point_towards(self, angle, rate):
        rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sing = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]


    # gravity and friction
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])
        # speed adjustment 

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]

        # angles
        #self.point_towards(math.pi / 2, 0.02)
        #self.velocity_adjust(0.975, 0.2, 8, dt)
        #self.angle += 0.1

        self.speed -= 0.1

        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, offset=[0, 0]):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.speed * self.scale, self.loc[1] + math.sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.speed * self.scale * 3.5, self.loc[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3, self.loc[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)


while True:

    screen.fill((0,0,0))

    for i, spark in sorted(enumerate(sparks), reverse=True):
        spark.move(1)
        spark.draw(screen)
        if not spark.alive:
            sparks.pop(i)


    mx, my = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        sparks.append(Spark([mx, my], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 255, 255), 2))
        sparks.append(Spark([mx, my], math.radians(random.randint(0, 360)), random.randint(3, 6), (255, 220, 70), 2))


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    pygame.display.update()
    mainClock.tick(60)





# import pygame
# import random

# screen_width = 750
# screen_height = 650

# screen = pygame.display.set_mode((screen_width, screen_height))

# clock = pygame.time.Clock()
# FPS = 60


# def scale(img: pygame.Surface, factor):
#     w, h = img.get_width() * factor, img.get_height() * factor
#     return pygame.transform.scale(img, (int(w), int(h)))


# SMOKE = pygame.image.load('src/assets/images/backgrounds/smoke.png').convert_alpha()


# class SmokeParticle:
#     # def __init__(self, x=screen_width // 2, y=screen_height // 2):
#     #     self.x = x
#     #     self.y = y
#     #     self.scale_k = 0.1
#     #     self.img = scale(IMAGE, self.scale_k)
#     #     self.alpha = 255
#     #     self.alpha_rate = 3
#     #     self.alive = True
#     #     self.vx = 0
#     #     self.vy = 4 + random.randint(7, 10) / 10
#     #     self.k = 0.01 * random.random() * random.choice([-1, 1])
        
#     def __init__(self, x=random.randint(1,screen_width), y=random.randint(1,screen_height)):
#         self.x = x
#         self.y = y
#         self.scale_k = 0.1
#         self.img = scale(SMOKE, self.scale_k)
#         self.alpha = 50
#         # self.alpha_rate = 3
#         self.alive = True
#         self.vx = 0
#         self.vy = 0 #4 + random.randint(7, 10) / 10
#         self.k = 0.01 * random.random() * random.choice([-1, 1])

#     def update(self):
#         self.x += self.vx
#         self.vx += self.k
#         self.y -= self.vy
#         self.vy *= 0.99
#         self.scale_k += 0.005
#         # self.alpha -= self.alpha_rate
#         if self.alpha < 0:
#             self.alpha = 0
#             self.alive = False
#         # self.alpha_rate -= 0.1
#         # if self.alpha_rate < 1.5:
#         #     self.alpha_rate = 1.5
#         self.img = scale(SMOKE, self.scale_k)
#         self.img.set_alpha(self.alpha)

#     def draw(self):
#         screen.blit(self.img, self.img.get_rect(center=(self.x, self.y)))


# class Smoke:
#     # def __init__(self, x=screen_width // 2, y=screen_height // 2 + 150):
#     #     self.x = x
#     #     self.y = y
#     #     self.particles = []
#     #     self.frames = 0
        
#     def __init__(self, x=200, y=200):
#         self.x = x
#         self.y = y
#         self.particles = []
#         self.frames = 0

#     def update(self):
#         self.particles = [i for i in self.particles if i.alive]
#         self.frames += 1
#         if self.frames % 2 == 0:
#             self.frames = 0
#             self.particles.append(SmokeParticle(self.x, self.y))
#         for i in self.particles:
#             i.update()

#     def draw(self):
#         for i in self.particles:
#             i.draw()


# smoke = Smoke()


# def main_game():
#     while True:
#         events = pygame.event.get()
#         for e in events:
#             if e.type == pygame.QUIT:
#                 quit()
#             if e.type == pygame.KEYDOWN:
#                 if e.key == pygame.K_ESCAPE:
#                     quit()
                    
#         screen.fill((0, 0, 0))
#         smoke.update()
#         smoke.draw()
        
#         pygame.display.update()
#         clock.tick(FPS)
#         pygame.display.set_caption(f'FPS = {clock.get_fps()}')


# main_game()