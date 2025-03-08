import pygame
import sys
import os
import random
import math

# Initialize Pygame
pygame.init()

# Base resolution (game logic uses these coordinates)
BASE_WIDTH = 800
BASE_HEIGHT = 500

# Current screen resolution (starts at base resolution)
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Hallway - Level 1")

# Colors
GREEN = (32, 96, 32)
BLACK = (10, 10, 30)  # Darker blue-black for Level 1
WHITE = (255, 255, 255)
PLAYER_COLOR = (74, 128, 245)
EXIT_COLOR = (255, 215, 0)  # Gold color for level transition

# Player settings (in base coordinates)
player_pos = [120, 250]  # Starting position
player_radius = 10
player_speed = 10

# Level transition portal
level_exit = [2800, 700, 50]  # x, y, radius

# Updated hallway definition with image_key for each segment
base_hallway = [
    # === MAIN ENTRANCE ===
    [100, 250, 600, 250, 300, "entrance_hall"],
    
    # === EASTERN PATHWAYS ===
    [600, 250, 600, 600, 150, "eastern_vertical"],
    [600, 600, 1200, 600, 150, "eastern_horizontal"],
    [1200, 600, 1200, 300, 150, "eastern_upper"],
    
    # === WESTERN CORRIDORS ===
    [300, 250, 300, 800, 120, "western_descent"],
    [300, 800, 800, 800, 140, "lower_western"],
    
    # === CENTRAL CHAMBER ===
    [800, 800, 1400, 800, 250, "central_chamber"],
    [1100, 800, 1100, 1200, 150, "southern_passage"],
    
    # === PUZZLE ROOM APPROACHES ===
    [1100, 1200, 700, 1200, 180, "puzzle_approach_west"],
    [1100, 1200, 1500, 1200, 180, "puzzle_approach_east"],
    
    # === PUZZLE ROOMS ===
    [700, 1200, 700, 1500, 200, "puzzle_room_1"],
    [1500, 1200, 1500, 1500, 200, "puzzle_room_2"],
    
    # === NORTHERN SECRET PATH ===
    [1200, 300, 1800, 300, 130, "northern_secret"],
    [1800, 300, 1800, 600, 130, "secret_vertical"],
    
    # === TREASURE SECTION ===
    [1800, 600, 2300, 600, 160, "treasure_approach"],
    [2300, 600, 2300, 900, 160, "treasure_vertical"],
    [2300, 900, 2000, 900, 220, "treasure_room_west"],
    [2300, 900, 2600, 900, 220, "treasure_room_east"],
    
    # === LEVEL EXIT PATH ===
    [2300, 600, 2800, 600, 170, "exit_corridor"],
    [2800, 600, 2800, 800, 170, "exit_room"],
]

# Special room markers (used to place enemies, treasures, etc.)
special_rooms = {
    "puzzle_area_1": [650, 1400, 300, 200, "puzzle"],
    "puzzle_area_2": [1450, 1400, 300, 200, "puzzle"],
    "treasure_vault": [2300, 850, 300, 200, "treasure"],
    "ambush_corner": [1100, 650, 200, 180, "combat"],
    "secret_stash": [1750, 350, 150, 150, "hidden_treasure"],
    "healing_fountain": [1250, 780, 150, 150, "healing"],
    "level_transition": [2750, 700, 150, 150, "transition"],
}

def load_image(filename, scale=1.0):
    try:
        image = pygame.image.load(os.path.join('src', 'assets', 'images', 'backgrounds', filename))
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        surf = pygame.Surface((64, 64))
        surf.fill((50, 50, 100))  # Different color for Level 1 placeholder
        pygame.draw.rect(surf, (30, 30, 70), (0, 0, 32, 32))
        pygame.draw.rect(surf, (30, 30, 70), (32, 32, 32, 32))
        return surf

# --- Image Setup for Level 1 - Darker Stone Dungeon Theme ---
shared_image = load_image("Level2Background.jpg")
default_hallway_img = load_image("Level2Background.jpg")
image = "lvl2_LavaCave_1.jpg"

# Create dictionary for Level 1 hallway images
hallway_images = {
    "entrance_hall": shared_image,
    "eastern_vertical": default_hallway_img,
    "eastern_horizontal": default_hallway_img,
    "eastern_upper": default_hallway_img,
    "western_descent": load_image(image),
    "lower_western": default_hallway_img,
    "central_chamber": load_image(image),
    "southern_passage": default_hallway_img,
    "puzzle_approach_west": default_hallway_img,
    "puzzle_approach_east": default_hallway_img,
    "puzzle_room_1": load_image(image),
    "puzzle_room_2": load_image(image),
    "northern_secret": load_image(image),
    "secret_vertical": load_image(image),
    "treasure_approach": default_hallway_img,
    "treasure_vertical": default_hallway_img,
    "treasure_room_west": load_image(image),
    "treasure_room_east": load_image(image),
    "exit_corridor": load_image(image),
    "exit_room": load_image(image),
}

# Movement effects (stored in base coordinates)
class MovementEffect:
    def __init__(self, pos_x, pos_y):
        self.pos = [pos_x, pos_y]
        self.radius = 3
        self.alpha = 200
        self.color = (100, 150, 255, self.alpha)
    
    def update(self):
        self.radius += 0.5
        self.alpha -= 10
        self.color = (100, 150, 255, self.alpha)
        return self.alpha > 0
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        scaled_radius = int(self.radius * scale_x)
        scaled_pos = (int(self.pos[0] * scale_x) - camera_x, int(self.pos[1] * scale_y) - camera_y)
        s = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (scaled_radius, scaled_radius), scaled_radius)
        screen.blit(s, (scaled_pos[0] - scaled_radius, scaled_pos[1] - scaled_radius))

# Portal effect for level transition
class PortalEffect:
    def __init__(self, pos_x, pos_y, radius):
        self.pos = [pos_x, pos_y]
        self.radius = radius
        self.angle = 0
        self.particles = []
        # Create some initial particles
        for _ in range(20):
            self.particles.append({
                'radius': 2 + 5 * random.random(),
                'angle': 360 * random.random(),
                'distance': radius * 0.2 + radius * 0.6 * random.random(),
                'speed': 0.5 + random.random()
            })
    
    def update(self):
        self.angle = (self.angle + 1) % 360
        
        # Update existing particles
        for particle in self.particles:
            particle['angle'] = (particle['angle'] + particle['speed']) % 360
        
        # Occasionally add new particles
        if random.random() < 0.1:
            self.particles.append({
                'radius': 2 + 5 * random.random(),
                'angle': 360 * random.random(),
                'distance': self.radius * 0.2 + self.radius * 0.6 * random.random(),
                'speed': 0.5 + random.random()
            })
        
        # Remove random particles occasionally to prevent overcrowding
        if len(self.particles) > 40 and random.random() < 0.1:
            self.particles.pop(int(random.random() * len(self.particles)))
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        # Calculate scaled position for the center of the portal
        scaled_pos = (int(self.pos[0] * scale_x) - camera_x, int(self.pos[1] * scale_y) - camera_y)
        scaled_radius = int(self.radius * scale_x)
        
        # Draw outer glow
        for r in range(scaled_radius, int(scaled_radius * 1.5), 2):
            alpha = 150 - 100 * ((r - scaled_radius) / (scaled_radius * 0.5))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (EXIT_COLOR[0], EXIT_COLOR[1], EXIT_COLOR[2], alpha), (r, r), r)
            screen.blit(s, (scaled_pos[0] - r, scaled_pos[1] - r))
        
        # Draw base portal
        pygame.draw.circle(screen, EXIT_COLOR, scaled_pos, scaled_radius)
        pygame.draw.circle(screen, WHITE, scaled_pos, scaled_radius, 2)
        
        # Draw rotating particles
        for particle in self.particles:
            rad_angle = math.radians(particle['angle'])
            particle_pos = (
                scaled_pos[0] + particle['distance'] * scale_x * math.cos(rad_angle),
                scaled_pos[1] + particle['distance'] * scale_y * math.sin(rad_angle)
            )
            particle_radius = int(particle['radius'] * scale_x)
            
            pygame.draw.circle(
                screen, 
                (255, 255, 255), 
                (int(particle_pos[0]), int(particle_pos[1])), 
                particle_radius
            )

def is_in_hallway(pos_x, pos_y):
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, _ = segment
        half_width = width / 2
        if start_y == end_y:
            if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and (start_y - half_width) <= pos_y <= (start_y + half_width):
                return True
        elif start_x == end_x:
            if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and (start_x - half_width) <= pos_x <= (start_x + half_width):
                return True
    return False

def is_at_exit(pos_x, pos_y):
    exit_x, exit_y, exit_radius = level_exit
    distance = ((pos_x - exit_x) ** 2 + (pos_y - exit_y) ** 2) ** 0.5
    return distance <= exit_radius + player_radius

def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, image_key = segment
        half_width = width / 2
        
        hallway_image = hallway_images.get(image_key, default_hallway_img)
        
        if start_y == end_y:
            rect_x = min(start_x, end_x)
            rect_y = start_y - half_width
            rect_width = abs(end_x - start_x)
            rect_height = width
        else:
            rect_x = start_x - half_width
            rect_y = min(start_y, end_y)
            rect_width = width
            rect_height = abs(end_y - start_y)
        
        scaled_rect_x = rect_x * scale_x - camera_x
        scaled_rect_y = rect_y * scale_y - camera_y
        scaled_rect_width = rect_width * scale_x
        scaled_rect_height = rect_height * scale_y
        
        scaled_hallway = pygame.transform.scale(
            hallway_image,
            (int(scaled_rect_width), int(scaled_rect_height))
        )
        screen.blit(scaled_hallway, (scaled_rect_x, scaled_rect_y))
        
        if start_y == end_y:
            pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y),
                             (scaled_rect_x + scaled_rect_width, scaled_rect_y), 2)
            pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y + scaled_rect_height),
                             (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 2)
        else:
            pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y),
                             (scaled_rect_x, scaled_rect_y + scaled_rect_height), 2)
            pygame.draw.line(screen, WHITE, (scaled_rect_x + scaled_rect_width, scaled_rect_y),
                             (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 2)

def transition_to_level2():
    # Create a fade effect
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)  # 20ms delay for smooth transition
    
    # This is where you'd launch level 2
    # For now, we'll just print a message and restart level 1
    print("Transitioning to Level 2...")
    
    # Import and run level 2
    try:
        import level2  # This would be your level2.py file
        return "level2"
    except ImportError:
        print("Level 2 file not found. Restarting Level 1.")
        # Reset player position for level restart
        player_pos[0] = 120
        player_pos[1] = 250
        return "continue"

# Create portal effect
portal = PortalEffect(level_exit[0], level_exit[1], level_exit[2])

clock = pygame.time.Clock()
movement_effects = []
step_counter = 0
running = True
transitioning = False

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
    scale_x = SCREEN_WIDTH / BASE_WIDTH
    scale_y = SCREEN_HEIGHT / BASE_HEIGHT
    
    if not transitioning:
        keys = pygame.key.get_pressed()
        original_pos = player_pos.copy()
        
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            player_pos[1] += player_speed
        
        # Check if player is at the exit portal
        if is_at_exit(player_pos[0], player_pos[1]):
            transitioning = True
            next_action = transition_to_level2()
            if next_action == "level2":
                running = False  # Exit the current level's loop
            else:
                transitioning = False  # Continue in level 1
        
        if not is_in_hallway(player_pos[0], player_pos[1]):
            player_pos = original_pos
        else:
            step_counter += 1
            if step_counter % 10 == 0:
                movement_effects.append(MovementEffect(player_pos[0], player_pos[1]))
    
    scaled_player_x = int(player_pos[0] * scale_x)
    scaled_player_y = int(player_pos[1] * scale_y)
    camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
    camera_y = scaled_player_y - (SCREEN_HEIGHT // 2)
    
    movement_effects = [effect for effect in movement_effects if effect.update()]
    portal.update()
    
    screen.fill(BLACK)
    draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
    
    # Draw the portal
    portal.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
    # Draw movement effects
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
    # Draw player
    pygame.draw.circle(screen, PLAYER_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x))
    pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x), 2)
    
    # Display level indicator
    font = pygame.font.SysFont(None, 36)
    level_text = font.render("Level 1", True, WHITE)
    screen.blit(level_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()