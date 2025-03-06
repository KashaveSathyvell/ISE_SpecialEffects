import pygame
import sys
import os
import random  # New import for random selection

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
player_speed = 10

# Updated hallway definition with image_key for each segment
base_hallway = [
    # === WESTERN WING ===
    [175, 450, 175, 800, 150, "western_corridor"],
    [175, 800, -225, 800, 100, "treasure_approach"],
    [-225, 800, -225, 1500, 120, "miniboss_approach"],
    [-625, 1400, -225, 1400, 200, "miniboss_chamber"],
    
    # === CENTRAL PATHWAYS ===
    [900, 350, 1600, 350, 200, "main_hallway"],
    
    [500, 450, 500, 500, 130, "LavaJump"],
    [500, 500, 500, 1400, 130, "central_shaft"],
    [500, 1400, 1000, 1400, 130, "lower_connector"],
    [1000, 1400, 1000, 1800, 150, "water_entrance"],
    [700, 1800, 1000, 1800, 200, "water_room_west"],
    [1000, 1800, 1300, 1800, 200, "water_room_east"],
    
    # === EASTERN COMPLEX ===
    [1600, 350, 2400, 350, 200, "eastern_corridor"],
    [2400, 250, 2400, 900, 140, "eastern_descent"],
    [2000, 900, 2400, 900, 140, "middle_approach"],
    [2400, 900, 2800, 900, 180, "lower_chamber"],
    [2800, 900, 3200, 900, 80, "secret_passage"],
    [3200, 900, 3200, 600, 80, "secret_turn"],
    [3200, 600, 3600, 600, 80, "secret_treasure"],
    
    # === NEW PRINCESS RESCUE PATH ===
    [2800, 2200, 2800, 2600, 150, "princess_corridor"],
    
    # === LOWER LABYRINTH ===
    [900, 250, 900, 950, 150, "labyrinth_branch"],
    [900, 950, 1700, 950, 120, "labyrinth_upper"],
    [1200, 950, 1200, 1250, 120, "labyrinth_vert1"],
    [1700, 950, 1700, 1400, 120, "labyrinth_vert2"],
    [1200, 1250, 1700, 1250, 120, "labyrinth_lower"],
    [1700, 1250, 2000, 1250, 100, "trap_entrance"],
    
    # === ADDITIONAL MAZE-LIKE PATHS ===
    [1200, 1250, 1200, 1600, 120, "maze_section1"],
    [1200, 1600, 1700, 1600, 120, "maze_section2"],
    [1700, 1600, 1700, 1900, 120, "maze_section3"],
    [1400, 1250, 1400, 1600, 100, "maze_connection"],
    
    # === BOSS ARENA ACCESS ===
    [1700, 1400, 2200, 1400, 180, "preboss_corridor1"],
    [2200, 1400, 2200, 1900, 180, "preboss_corridor2"],
    [2200, 1900, 2600, 1900, 200, "boss_approach"],
    [2600, 1900, 2600, 2200, 250, "boss_entrance"],
    
    # === BOSS ARENA ===
    [2400, 2200, 2600, 2200, 350, "boss_arena_west"],
    [2600, 2200, 2800, 2200, 350, "boss_arena_east"],
    [2600, 2400, 2600, 2200, 350, "boss_arena_south"],
    [2650, 2300, 2750, 2300, 80, "boss_throne"],
    
    # === ENTRANCE ZONE ===
    [100, 250, 900, 250, 400, "entrance_hall"],
    [100, 415, 900, 415, 65, "entranceHall_Walkway"],
    
    [850, 250, 900, 250, 400, "mainHallway_Wall"],
    
    # === ESCAPE ROUTE ===
    [2800, 2200, 3200, 2200, 150, "escape_passage"],
    [3200, 2200, 3200, 1400, 150, "escape_vertical"],
    [3200, 1400, 3800, 1400, 200, "final_corridor"],
]

# Special room markers (used to place enemies, treasures, etc.)
special_rooms = {
    "mini_boss": [200, 1150, 400, 200, "combat"],
    "water_puzzle": [700, 1750, 600, 200, "puzzle"],
    "treasure_room": [3400, 550, 300, 200, "treasure"],
    "princess_chamber": [2800, 2600, 350, 200, "rescue"],
    "trap_room": [1800, 1200, 300, 200, "traps"],
    "boss_arena": [2400, 2200, 400, 350, "boss_fight"],
    "secret_cache": [1400, 1500, 150, 150, "hidden_treasure"],
    "ambush_point": [1500, 250, 200, 180, "combat"],
    "poison_corridor": [900, 600, 150, 350, "hazard"],
    "healing_shrine": [2100, 900, 150, 150, "healing"],
    "weapon_upgrade": [800, 1250, 150, 150, "upgrade"],
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
        surf.fill((100, 0, 100))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, 32, 32))
        pygame.draw.rect(surf, (0, 0, 0), (32, 32, 32, 32))
        return surf

# --- Image Setup for Entrance Hall and Main Hallway ---
shared_image = load_image("Level2Background.jpg")
crop_offset = shared_image.get_height() // 2  # Crop the top half
cropped_main_hallway = shared_image.subsurface(
    pygame.Rect(0, crop_offset, shared_image.get_width(), shared_image.get_height() - crop_offset)
).copy()

# Define default image for fallback
default_hallway_img = load_image("lvl2_CrystalCave.jpg")

def preprocess_tile_images(image_list):
    """
    Returns a new list where every image is cropped or scaled to match
    the dimensions of the first image in the list.
    """
    fixed_w, fixed_h = image_list[0].get_size()
    processed = []
    for img in image_list:
        img_w, img_h = img.get_size()
        # If the image is larger, crop it; if it's smaller, scale it up.
        if img_w != fixed_w or img_h != fixed_h:
            if img_w >= fixed_w and img_h >= fixed_h:
                cropped = img.subsurface((0, 0, fixed_w, fixed_h)).copy()
                processed.append(cropped)
            else:
                scaled = pygame.transform.scale(img, (fixed_w, fixed_h))
                processed.append(scaled)
        else:
            processed.append(img)
    return processed

def tile_multiple_images(image_list, target_width, target_height, seed=None):
    """Creates a new Surface by tiling images from image_list (which are all preprocessed
    to have the same size) to fill a region of size (target_width, target_height).
    Uses a seed to ensure consistent tiling across frames."""
    processed_images = preprocess_tile_images(image_list)
    fixed_tile_w, fixed_tile_h = processed_images[0].get_size()

    if seed is None:
        seed = hash((target_width, target_height))
    random.seed(seed)
    
    tiled_surf = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
    
    for y in range(0, target_height, fixed_tile_h):
        for x in range(0, target_width, fixed_tile_w):
            chosen_image = random.choice(processed_images)
            blit_w = min(fixed_tile_w, target_width - x)
            blit_h = min(fixed_tile_h, target_height - y)
            src_rect = pygame.Rect(0, 0, blit_w, blit_h)
            tiled_surf.blit(chosen_image, (x, y), src_rect)
    
    random.seed()
    return tiled_surf

# Define a vertical tile set (using the same images as the central shaft)
vertical_tile_set = [load_image("CaveFloor.png"), load_image("CaveFloor.png"), load_image("CaveFloor.png"), load_image("CaveFloor1.png"), load_image("CaveFloor1.png"), load_image("CaveFloor1.png"), load_image("CaveFloor1.png"), load_image("CaveFloor1.png"), load_image("CaveFloor1.png"), load_image("Lava.png")]

Cave_Wall = [load_image("CaveWall.png")]

LavaCaveFloor_crop = load_image("LavaHallwayFloor2.jpg")
cropped_LavaCaveFloor = LavaCaveFloor_crop.subsurface(
    pygame.Rect(0, 0, LavaCaveFloor_crop.get_width(), LavaCaveFloor_crop.get_height()//2)
).copy()

# Cache for tiled hallway images
tiled_hallway_cache = {}

# Dictionary to store hallway images by key.
# For vertical hallways (where start_x == end_x), we assign the vertical tile set.
hallway_images = {
    "entrance_hall": shared_image,
    "entranceHall_Walkway" : cropped_LavaCaveFloor,
    "main_hallway": cropped_main_hallway,
    "mainHallway_Wall": Cave_Wall,
    
    
    "western_corridor": load_image("LavaHallwayFloor1.jpg"), #vertical_tile_set,
    "treasure_approach": load_image("lvl2_LavaCave.jpg"),
    "miniboss_approach": vertical_tile_set,
    "miniboss_chamber": load_image("lvl2_MiniBoss2.jpg"),
    
    
    "LavaJump" : load_image("Lava.png"),
    "central_shaft": vertical_tile_set,
    "lower_connector": default_hallway_img,
    "water_entrance": vertical_tile_set,
    "water_room_west": load_image("lvl2_AcidCave.avif"),
    "water_room_east": load_image("lvl2_AcidCave.avif"),
    "eastern_corridor": cropped_main_hallway,
    "eastern_descent": vertical_tile_set,
    "middle_approach": default_hallway_img,
    "lower_chamber": default_hallway_img,
    "secret_passage": default_hallway_img,
    "secret_turn": vertical_tile_set,
    "secret_treasure": default_hallway_img,
    "princess_corridor": vertical_tile_set,
    "labyrinth_branch": vertical_tile_set,
    "labyrinth_upper": default_hallway_img,
    "labyrinth_vert1": vertical_tile_set,
    "labyrinth_vert2": vertical_tile_set,
    "labyrinth_lower": default_hallway_img,
    "trap_entrance": default_hallway_img,
    "maze_section1": vertical_tile_set,
    "maze_section2": default_hallway_img,
    "maze_section3": vertical_tile_set,
    "maze_connection": vertical_tile_set,
    "preboss_corridor1": default_hallway_img,
    "preboss_corridor2": vertical_tile_set,
    "boss_approach": default_hallway_img,
    "boss_entrance": vertical_tile_set,
    "boss_arena_west": default_hallway_img,
    "boss_arena_east": default_hallway_img,
    "boss_arena_south": vertical_tile_set,
    "boss_throne": default_hallway_img,
    "escape_passage": default_hallway_img,
    "escape_vertical": vertical_tile_set,
    "final_corridor": default_hallway_img,
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
        scaled_rect_width = int(rect_width * scale_x)
        scaled_rect_height = int(rect_height * scale_y)
        
        if isinstance(hallway_image, list):
            cache_key = (image_key, scaled_rect_width, scaled_rect_height)
            if cache_key not in tiled_hallway_cache:
                tiled_hallway_cache[cache_key] = tile_multiple_images(
                    hallway_image, 
                    scaled_rect_width, 
                    scaled_rect_height, 
                    seed=hash(image_key)
                )
            screen.blit(tiled_hallway_cache[cache_key], (scaled_rect_x, scaled_rect_y))
        else:
            scaled_hallway = pygame.transform.scale(hallway_image, (scaled_rect_width, scaled_rect_height))
            screen.blit(scaled_hallway, (scaled_rect_x, scaled_rect_y))
        
        # if start_y == end_y:
        #     pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y),
        #                      (scaled_rect_x + scaled_rect_width, scaled_rect_y), 2)
        #     pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y + scaled_rect_height),
        #                      (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 2)
        # else:
        #     pygame.draw.line(screen, WHITE, (scaled_rect_x, scaled_rect_y),
        #                      (scaled_rect_x, scaled_rect_y + scaled_rect_height), 2)
        #     pygame.draw.line(screen, WHITE, (scaled_rect_x + scaled_rect_width, scaled_rect_y),
        #                      (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 2)

clock = pygame.time.Clock()
movement_effects = []
step_counter = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
    scale_x = SCREEN_WIDTH / BASE_WIDTH
    scale_y = SCREEN_HEIGHT / BASE_HEIGHT
    
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
    
    screen.fill(BLACK)
    draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
    pygame.draw.circle(screen, PLAYER_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x))
    pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x), 2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
