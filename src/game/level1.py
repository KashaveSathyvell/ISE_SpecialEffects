import pygame
import sys

# Initialize Pygame
pygame.init()

# Base resolution (game logic uses these coordinates)
BASE_WIDTH = 800
BASE_HEIGHT = 500

# Current screen resolution (starts at base resolution)
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Hallway")

# Colors
GREEN = (32, 96, 32)
BLACK = (13, 27, 10)
WHITE = (255, 255, 255)
PLAYER_COLOR = (74, 128, 245)

# Player settings (in base coordinates)
player_pos = [120, 250]  # Starting position
player_radius = 10
player_speed = 3

# Base hallway path coordinates (in base coordinates)
base_hallway = [
    [100, 250, 450, 250, 100],  # First horizontal segment
    [450, 250, 450, 50, 100],
    [300, 250, 300, 500, 100],  # Vertical segment down
    [300, 500, 500, 500, 100],  # Second horizontal segment
    [500, 350, 500, 150, 100],  # Vertical segment up
    [500, 150, 800, 150, 200],  # Third horizontal segment
    [800, 150, 800, 550, 200],
]

# Movement effects (stored in base coordinates)
class MovementEffect:
    def __init__(self, pos_x, pos_y):
        self.pos = [pos_x, pos_y]
        self.radius = 3  # base radius
        self.alpha = 200  # starting opacity
        self.color = (100, 150, 255, self.alpha)
    
    def update(self):
        self.radius += 0.5
        self.alpha -= 10
        self.color = (100, 150, 255, self.alpha)
        return self.alpha > 0
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        # Scale radius (using scale_x here; you could average scale_x and scale_y)
        scaled_radius = int(self.radius * scale_x)
        # Compute scaled position
        scaled_pos = (int(self.pos[0] * scale_x) - camera_x, int(self.pos[1] * scale_y) - camera_y)
        # Create a surface with alpha channel for the effect
        s = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (scaled_radius, scaled_radius), scaled_radius)
        screen.blit(s, (scaled_pos[0] - scaled_radius, scaled_pos[1] - scaled_radius))

def is_in_hallway(pos_x, pos_y):
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width = segment
        half_width = width / 2
        if start_y == end_y:
            if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and start_y - half_width <= pos_y <= start_y + half_width:
                return True
        elif start_x == end_x:
            if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and start_x - half_width <= pos_x <= start_x + half_width:
                return True
    return False

def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width = segment
        scaled_start = (int(start_x * scale_x) - camera_x, int(start_y * scale_y) - camera_y)
        scaled_end = (int(end_x * scale_x) - camera_x, int(end_y * scale_y) - camera_y)
        scaled_width = int(width * scale_x)  # Scale width
        pygame.draw.line(screen, GREEN, scaled_start, scaled_end, scaled_width)

clock = pygame.time.Clock()
movement_effects = []
step_counter = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # Update the current screen resolution and window
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
    # Calculate scaling factors based on the current resolution relative to the base resolution
    scale_x = SCREEN_WIDTH / BASE_WIDTH
    scale_y = SCREEN_HEIGHT / BASE_HEIGHT
    
    keys = pygame.key.get_pressed()
    original_pos = player_pos.copy()
    
    # Handle player movement (in base coordinates)
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed
    
    # Collision checking against the base hallway coordinates
    if not is_in_hallway(player_pos[0], player_pos[1]):
        player_pos = original_pos
    else:
        step_counter += 1
        if step_counter % 10 == 0:
            movement_effects.append(MovementEffect(player_pos[0], player_pos[1]))
    
    # Compute the player's scaled position
    scaled_player_x = int(player_pos[0] * scale_x)
    scaled_player_y = int(player_pos[1] * scale_y)
    
    # Compute the camera offset so that the player remains centered
    camera_x = scaled_player_x - SCREEN_WIDTH // 2
    camera_y = scaled_player_y - SCREEN_HEIGHT // 2
    
    # Update movement effects and remove faded ones
    for effect in movement_effects[:]:
        if not effect.update():
            movement_effects.remove(effect)
    
    screen.fill(BLACK)
    
    # Draw the hallway, movement effects, and player using scaled coordinates
    draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
    pygame.draw.circle(screen, PLAYER_COLOR, (scaled_player_x - camera_x, scaled_player_y - camera_y), int(player_radius * scale_x))
    pygame.draw.circle(screen, WHITE, (scaled_player_x - camera_x, scaled_player_y - camera_y), int(player_radius * scale_x), 2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
