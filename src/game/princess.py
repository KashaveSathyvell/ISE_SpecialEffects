import pygame
import os

class Princess:
    def __init__(self, x, y, scale=0.2):  # Add a scale parameter
        self.x = x
        self.y = y
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.following_player = False
        self.animation_speed = 300  # Time (ms) per frame

        # Load and scale princess images
        raw_images = [
            pygame.image.load(os.path.join("src/assets/images/princess", "princess.png")),
            pygame.image.load(os.path.join("src/assets/images/princess", "Princess2.png"))
        ]
        
        # Resize images
        self.images = [pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))) for img in raw_images]


    def update(self, player):
        """Animate princess and make her follow the player."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            self.last_update = current_time
            self.frame_index = (self.frame_index + 1) % len(self.images)

        # Follow player if the boss is defeated
        if self.following_player:
            target_x = player.x - 20  # Stay 20 pixels behind
            target_y = player.y - 100
            self.x += (target_x - self.x) * 0.1  # Smooth movement
            self.y += (target_y - self.y) * 0.1

    def draw(self, screen, camera_x, camera_y):
        """Draw the princess on the screen."""
        image = self.images[self.frame_index]
        screen.blit(image, (self.x - camera_x, self.y - camera_y))
