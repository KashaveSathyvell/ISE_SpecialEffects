import pygame
import math
import random

class Spark:
    def __init__(self, loc, angle, speed, color, scale=1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]
    
        self.speed -= 0.1
        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, camera_x=0, camera_y=0, scale_x=1, scale_y=1):
        if self.alive:
            # Convert world position to screen position using camera offsets
            screen_x = (self.loc[0] - camera_x) * scale_x
            screen_y = (self.loc[1] - camera_y) * scale_y
    
            # Ensure sparks are within screen bounds before drawing
            if 0 <= screen_x <= surf.get_width() and 0 <= screen_y <= surf.get_height():
                points = [
                    [screen_x + math.cos(self.angle) * self.speed * self.scale,
                     screen_y + math.sin(self.angle) * self.speed * self.scale],
                    [screen_x + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3,
                     screen_y + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                    [screen_x - math.cos(self.angle) * self.speed * self.scale * 3.5,
                     screen_y - math.sin(self.angle) * self.speed * self.scale * 3.5],
                    [screen_x + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3,
                     screen_y - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
                pygame.draw.polygon(surf, self.color, points)



