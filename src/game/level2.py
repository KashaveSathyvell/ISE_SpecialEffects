import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Base resolution (game logic uses these coordinates)
BASE_WIDTH = 800
BASE_HEIGHT = 500

# Current screen resolution (starts at base resolution)
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Hallway Level 2")

# Colors
GREEN = (32, 96, 32)
BLACK = (13, 27, 10)
WHITE = (255, 255, 255)
PLAYER_COLOR = (74, 128, 245)
DOOR_COLOR = (150, 75, 0)
DOOR_FRAME_COLOR = (180, 100, 20)

# Player settings (in base coordinates)
player_pos = [120, 250]  # Starting position
player_radius = 10
player_speed = 10

# Door system for the Entrance Hall
doors = [
    {"x": 200, "y": 415, "width": 40, "height": 65,
     "destination": "western_wing", "dest_x": 175, "dest_y": 500, "name": "Western Wing"},
    {"x": 400, "y": 415, "width": 40, "height": 65,
     "destination": "central_pathways", "dest_x": 500, "dest_y": 450, "name": "Central Pathways"},
    {"x": 600, "y": 415, "width": 40, "height": 65,
     "destination": "eastern_complex", "dest_x": 1600, "dest_y": 350, "name": "Eastern Complex"},
    # Changed this door to lead directly to the Boss Arena:
    {"x": 800, "y": 415, "width": 40, "height": 65,
     "destination": "Boss_room", "dest_x": 2400, "dest_y": 2200, "name": "Boss Room"}
]

# # New area transition door: (if needed, but now the door from Entrance goes directly to Boss Arena)
area_transition_doors = {
    # You can leave this in place if you want an alternative transition; otherwise, it may not be used.
    "lower_labyrinth": {  # This key is no longer used, since lower_labyrinth is removed.
        "x": 1700, "y": 1850, "width": 40, "height": 65,
        "destination": "Boss_arena", "dest_x": 2400, "dest_y": 2200,
        "name": "Enter Boss Arena"
    }
}

# Return doors (for teleporting back to the entrance)
area_return_doors = {
    "western_wing": {"x": 175, "y": 450, "destination": "entrance_hall", "dest_x": 200, "dest_y": 300, "name": "Return to Entrance"},
    "central_pathways": {"x": 500, "y": 450, "destination": "entrance_hall", "dest_x": 400, "dest_y": 300, "name": "Return to Entrance"},
    "eastern_complex": {"x": 1600, "y": 350, "destination": "entrance_hall", "dest_x": 600, "dest_y": 300, "name": "Return to Entrance"},
    "boss_arena": {"x": 2400, "y": 2200, "destination": "entrance_hall", "dest_x": 500, "dest_y": 300, "name": "Emergency Exit"}
}

# The current area the player is in
current_area = "entrance_hall"

# Updated hallway definitions.
# Removed the Lower Labyrinth and maze segments.
base_hallway = [
    # === ENTRANCE ZONE (always accessible initially) ===
    [100, 250, 900, 250, 400, "entrance_hall"],
    
    # === WESTERN WING ===
    [175, 450, 175, 800, 150, "western_corridor"],
    [160, 800, -225, 800, 100, "treasure_approach"],
    [-225, 850, -225, 900, 120, "LavaJump_Western"],
    [-225, 900, -225, 1500, 120, "miniboss_approach"],
    [-685, 1400, -285, 1400, 200, "miniboss_chamber"],
    
    # === CENTRAL PATHWAYS ===
    [500, 450, 500, 1400, 130, "central_shaft"],
    [430, 1400, 1000, 1400, 130, "lower_connector"],
    [1000, 1000, 1000, 1900, 150, "room_entrance"],
    [850, 1850, 925, 1850, 100, "room_hallway"],
    [250, 1800, 850, 1800, 200, "central_mainRoom"],
    
    
    # === EASTERN COMPLEX ===
    [1600, 350, 2400, 350, 200, "eastern_corridor"],
    [2325, 425, 2325, 800, 150, "eastern_down"],
    [2250, 870, 3400, 870, 140, "eastern_middle"],
    [3000, 800, 3000, 620, 150, "eastern_up_bottom"],
    [3000, 620, 3000, 470, 150, "eastern_up_transition"],
    [3000, 470, 3000, 240, 150, "eastern_up_top"],
    [2600, 150, 3400, 150, 400, "eastern_room"],
    
    # === NEW PRINCESS RESCUE PATH ===
    [3000, 2275, 3500, 2275, 250, "princess_corridor"],
    
    # === BOSS ARENA ===
    [2200, 2200, 3000, 2200, 400, "boss_room"],
    [2650, 2300, 2750, 2300, 80, "boss_throne"],
    [3500, 2325, 3800, 2325, 150, "escape_passage"],
    [3800, 2400, 3800, 1800, 150, "escape_vertical"],
    [3725, 1800, 4400, 1800, 200, "final_corridor"],
]

#define list of hallway behind each portal
area_hallways = {
    "entrance_hall": ["entrance_hall"],
    "western_wing": ["western_corridor", "treasure_approach", "LavaJump_Western", "miniboss_approach", "miniboss_chamber"],
    "central_pathways": ["central_shaft", "lower_connector", "room_entrance", "room_hallway",
                         "central_mainRoom"],
    "eastern_complex": ["eastern_corridor", "eastern_down", "eastern_middle", "eastern_up_bottom", "eastern_up_transition", "eastern_up_top", "eastern_room"],
    "Boss_room": ["boss_room", "boss_throne", "princess_corridor", "escape_passage", "escape_vertical", "final_corridor"]
}

# -----------------------------------------------------------
# Helper function: load an image using a platform-independent path.
def load_image(filename, scale=1.0):
    try:
        filepath = os.path.join("src", "assets", "images", filename)
        image = pygame.image.load(filepath).convert_alpha()
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        placeholder = pygame.Surface((64, 64))
        placeholder.fill((100, 0, 100))
        return placeholder

def extract_tile(surface, x, y, width, height):
    """Extract a tile from a tileset at the given coordinates."""
    tile = pygame.Surface((width, height), pygame.SRCALPHA)
    tile.blit(surface, (0, 0), (x, y, width, height))
    return tile

def create_tileset_from_images():
    tiles = {}
    tileset1 = pygame.Surface((500, 500))
    tileset1.fill((0, 0, 0))
    colors1 = [
        (48, 52, 109),  # Dark blue (floor)
        (80, 69, 155),  # Medium blue (wall)
        (32, 39, 71),   # Darker blue (shadow)
        (60, 88, 122),  # Blue-gray (accent)
        (94, 84, 142)   # Purple-blue (feature)
    ]
    tileset2 = pygame.Surface((500, 500))
    tileset2.fill((0, 0, 0))
    colors2 = [
        (68, 72, 129),  # Dark blue-purple (floor)
        (100, 89, 175), # Lighter purple (wall)
        (52, 59, 91),   # Dark blue-gray (shadow)
        (80, 108, 142), # Blue-gray (accent)
        (114, 104, 162) # Lighter purple-blue (feature)
    ]
    # Floor tiles
    tiles["floor1"] = pygame.Surface((32, 32))
    tiles["floor1"].fill(colors1[0])
    tiles["floor2"] = pygame.Surface((32, 32))
    tiles["floor2"].fill(colors1[1])
    # Wall tiles
    tiles["wall1"] = pygame.Surface((32, 32))
    tiles["wall1"].fill(colors2[1])
    tiles["wall2"] = pygame.Surface((32, 32))
    tiles["wall2"].fill(colors2[2])
    # Accent tiles
    tiles["accent1"] = pygame.Surface((32, 32))
    tiles["accent1"].fill(colors1[3])
    tiles["accent2"] = pygame.Surface((32, 32))
    tiles["accent2"].fill(colors2[3])
    # Feature tiles
    tiles["feature1"] = pygame.Surface((32, 32))
    tiles["feature1"].fill(colors1[4])
    tiles["feature2"] = pygame.Surface((32, 32))
    tiles["feature2"].fill(colors2[4])
    # Add patterns for visual distinction
    for tile_name, tile in tiles.items():
        if "floor" in tile_name:
            pygame.draw.line(tile, (255, 255, 255, 100), (0, 0), (32, 0), 1)
            pygame.draw.line(tile, (255, 255, 255, 100), (0, 0), (0, 32), 1)
        elif "wall" in tile_name:
            for y in range(0, 32, 8):
                pygame.draw.line(tile, (0, 0, 0, 100), (0, y), (32, y), 1)
                offset = 8 if y % 16 == 0 else 0
                for x in range(offset, 32, 16):
                    pygame.draw.line(tile, (0, 0, 0, 100), (x, y), (x, y+8), 1)
    return tiles

tileset = create_tileset_from_images()

# Define tile collections for different hallway types.
horizontal_tiles = [tileset["floor1"], tileset["floor2"]]
vertical_tiles = [tileset["floor1"], tileset["floor2"]]
wall_tiles = [tileset["wall1"], tileset["wall2"]]
accent_tiles = [tileset["accent1"], tileset["accent2"]]
feature_tiles = [tileset["feature1"], tileset["feature2"]]

tiled_hallway_cache = {}

def preprocess_tile_images(image_list):
    fixed_w, fixed_h = image_list[0].get_size()
    processed = []
    for img in image_list:
        img_w, img_h = img.get_size()
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

portalAnimation = [
    load_image("backgrounds/portal1.png", scale=2.5),
    load_image("backgrounds/portal2.png", scale=2.5),
    load_image("backgrounds/portal3.png", scale=2.5),
    load_image("backgrounds/portal4.png", scale=2.5),
    load_image("backgrounds/portal5.png", scale=2.5),
    load_image("backgrounds/portal6.png", scale=2.5),
    load_image("backgrounds/portal7.png", scale=2.5),
]
portalFrame = 0
portalTime = 0

def create_transition_tile(top_img, bottom_img, blend_height):
    # Use the minimum width of the two images.
    width = min(top_img.get_width(), bottom_img.get_width())
    
    # Ensure the images are tall enough by scaling or tiling them if necessary.
    if top_img.get_height() < blend_height:
        top_img = pygame.transform.scale(top_img, (width, blend_height))
    if bottom_img.get_height() < blend_height:
        bottom_img = pygame.transform.scale(bottom_img, (width, blend_height))
        # Alternatively, you could tile:
        # bottom_img = tile_multiple_images([bottom_img], width, blend_height)
    
    # Clamp blend_height to the available heights.
    blend_height = min(blend_height, top_img.get_height(), bottom_img.get_height())
    
    transition = pygame.Surface((width, blend_height), pygame.SRCALPHA)
    for i in range(blend_height):
        blend_factor = i / blend_height
        top_row = top_img.subsurface((0, top_img.get_height() - blend_height + i, width, 1)).copy()
        bottom_row = bottom_img.subsurface((0, i, width, 1)).copy()
        top_row.fill((255, 255, 255, int(255 * blend_factor)), special_flags=pygame.BLEND_RGBA_MULT)
        bottom_row.fill((255, 255, 255, int(255 * (1 - blend_factor))), special_flags=pygame.BLEND_RGBA_MULT)
        row_blend = pygame.Surface((width, 1), pygame.SRCALPHA)
        row_blend.blit(top_row, (0, 0))
        row_blend.blit(bottom_row, (0, 0))
        transition.blit(row_blend, (0, i))
    return transition

# Dictionary to store hallway images by key (grouped by door/area)
hallway_images = {
    # Entrance Hall Background
    "entrance_hall": load_image("backgrounds/Level2Background.jpg"),
    
    # --- Door 1: Western Wing ---
    "western_corridor": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "treasure_approach": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "LavaJump_Western": [load_image("backgrounds/Lava.png", scale=0.5)],
    "miniboss_approach": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "miniboss_chamber": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    
    # --- Door 2: Central Pathways ---
    "central_shaft": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "lower_connector": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "room_entrance": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "room_hallway": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "central_mainRoom": load_image("backgrounds/MysticalCave.jpg"),
    
    # --- Door 3: Eastern Complex ---
    "eastern_corridor": load_image("backgrounds/lvl2_CaveHallway.jpg"),   
    "eastern_down": [load_image("backgrounds/lvl2_CaveHallwayFloor.jpg")],         
    "eastern_middle": [load_image("backgrounds/lvl2_CaveHallwayFloor.jpg")],
    "eastern_up_bottom": [load_image("backgrounds/lvl2_CaveHallwayFloor.jpg")],
    "eastern_up_top": [load_image("backgrounds/lvl2_WaterPoolFloor1.jpg"), load_image("backgrounds/lvl2_WaterPoolFloor.jpg"), load_image("backgrounds/lvl2_WaterPoolFloor.jpg")],
    "eastern_up_transition": create_transition_tile(
        load_image("backgrounds/lvl2_CaveHallwayFloor.jpg", scale=0.5),
        load_image("backgrounds/lvl2_WaterPoolFloor.jpg", scale=0.5),
        150
    ),
    "eastern_room": load_image("backgrounds/lvl2_WaterPool.jpg"),
    
    # --- Boss Arena (directly reached from Lower Labyrinth) ---
    
    "princess_corridor": load_image("backgrounds/lvl2_PrincessCage.jpg"),

    "boss_room": load_image("backgrounds/lvl2_BossMain.jpg"),

    "boss_throne": feature_tiles,
    "escape_passage": [load_image("backgrounds/lvl2_BossCrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_BossCrystalCaveFloor1.jpg")],
    "escape_vertical": [load_image("backgrounds/lvl2_BossCrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_BossCrystalCaveFloor1.jpg")],
    "final_corridor": load_image("backgrounds/lvl2_BossCrystalCave.jpg"),
}

default_hallway_img = horizontal_tiles

# Movement effects (for visual trail)
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

# Allow movement only within segments of the current area.
def is_in_hallway(pos_x, pos_y):
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, image_key = segment
        if image_key not in area_hallways.get(current_area, []):
            continue
        half_width = width / 2
        if start_y == end_y:
            if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and (start_y - half_width) <= pos_y <= (start_y + half_width):
                return True
        elif start_x == end_x:
            if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and (start_x - half_width) <= pos_x <= (start_x + half_width):
                return True
    return False

# Check if the player is near any door (entrance, transition, or return)
def is_near_door():
    threshold = 30  # Interaction distance
    if current_area == "entrance_hall":
        for door in doors:
            door_center_x = door["x"] + door["width"] / 2
            door_center_y = door["y"] + door["height"] / 2
            distance = ((player_pos[0] - door_center_x) ** 2 + (player_pos[1] - door_center_y) ** 2) ** 0.5
            if distance < threshold:
                return door
    if current_area in area_transition_doors:
        door = area_transition_doors[current_area]
        door_center_x = door["x"] + door["width"] / 2
        door_center_y = door["y"] + door["height"] / 2
        distance = ((player_pos[0] - door_center_x) ** 2 + (player_pos[1] - door_center_y) ** 2) ** 0.5
        if distance < threshold:
            return door
    if current_area in area_return_doors:
        door = area_return_doors[current_area]
        door_center_x = door["x"] + door.get("width", 0) / 2
        door_center_y = door["y"] + door.get("height", 0) / 2
        distance = ((player_pos[0] - door_center_x) ** 2 + (player_pos[1] - door_center_y) ** 2) ** 0.5
        if distance < threshold:
            return door
    return None

# Teleport player to a new area.
def teleport_player(destination, dest_x, dest_y):
    global current_area, player_pos
    current_area = destination
    player_pos = [dest_x, dest_y]
    for i in range(5):
        movement_effects.append(MovementEffect(player_pos[0], player_pos[1]))

def draw_ui(screen):
    font = pygame.font.SysFont('Arial', 24)
    area_name = current_area.replace('_', ' ').title()
    text = font.render(f"Area: {area_name}", True, WHITE)
    screen.blit(text, (10, 10))
    door = is_near_door()
    if door:
        prompt_text = f"Press E to enter {door['name']}"
        text = font.render(prompt_text, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 40))

clock = pygame.time.Clock()
movement_effects = []
step_counter = 0
running = True

# Fade transition settings.
fade_alpha = 0
is_fading = False
fade_in = False
fade_speed = 15
destination_info = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not is_fading:
                door = is_near_door()
                if door:
                    is_fading = True
                    fade_in = False
                    fade_alpha = 0
                    destination_info = door
    if is_fading:
        if not fade_in:
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_in = True
                teleport_player(destination_info["destination"], destination_info["dest_x"], destination_info["dest_y"])
        else:
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                is_fading = False
                destination_info = None
    if not is_fading or fade_alpha < 255:
        scale_x = SCREEN_WIDTH / BASE_WIDTH
        scale_y = SCREEN_HEIGHT / BASE_HEIGHT
        keys = pygame.key.get_pressed()
        original_pos = player_pos.copy()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
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
    screen.fill(BLACK)
    
    current_hallway_segments = []
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, image_key = segment
        if image_key in area_hallways.get(current_area, []):
            current_hallway_segments.append(segment)
    
    for segment in current_hallway_segments:
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
                    hallway_image, scaled_rect_width, scaled_rect_height, seed=hash(image_key)
                )
            screen.blit(tiled_hallway_cache[cache_key], (scaled_rect_x, scaled_rect_y))
        else:
            scaled_hallway = pygame.transform.scale(hallway_image, (scaled_rect_width, scaled_rect_height))
            screen.blit(scaled_hallway, (scaled_rect_x, scaled_rect_y))
    
    portalTime += clock.get_time()
    if portalTime >= 500:
        portalTime = 0
        portalFrame = (portalFrame + 1) % len(portalAnimation)
                
    if current_area == "entrance_hall":
        for door in doors:
            door_x = door["x"] * scale_x - camera_x
            door_y = door["y"] * scale_y - camera_y
            screen.blit(portalAnimation[portalFrame], (door_x - 15, door_y - 30))
    elif current_area in area_transition_doors:
        door = area_transition_doors[current_area]
        door_x = door["x"] * scale_x - camera_x
        door_y = door["y"] * scale_y - camera_y
        screen.blit(portalAnimation[portalFrame], (door_x - 35, door_y - 5))
    elif current_area in area_return_doors:
        door = area_return_doors[current_area]
        door_x = door["x"] * scale_x - camera_x
        door_y = door["y"] * scale_y - camera_y
        screen.blit(portalAnimation[portalFrame], (door_x - 35, door_y - 5))
            
    movement_effects = [effect for effect in movement_effects if effect.update()]
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
        
    scaled_player_radius = int(player_radius * scale_x)
    pygame.draw.circle(screen, PLAYER_COLOR, (scaled_player_x - camera_x, scaled_player_y - camera_y), scaled_player_radius)
    
    draw_ui(screen)
    
    if is_fading:
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
