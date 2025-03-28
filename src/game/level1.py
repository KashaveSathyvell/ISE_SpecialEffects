import pygame
import sys
import os
import random
import math
import json

from enemy import Enemy, load_mob_animations, Boss1
from player import Character
from powerups import Spark

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound system
pygame.mixer.set_num_channels(32) 

# Base resolution (game logic uses these coordinates)
BASE_WIDTH = 800
BASE_HEIGHT = 500

# Current screen resolution (starts at base resolution)
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Rescue")

# Colors
GREEN = (32, 96, 32)
BLACK = (13, 27, 10)
WHITE = (255, 255, 255)
PLAYER_COLOR = (74, 128, 245)
DOOR_COLOR = (150, 75, 0)
DOOR_FRAME_COLOR = (180, 100, 20)


# Load and play background music
try:
    pygame.mixer.music.load(os.path.join("src", "assets", "sounds", "level1_bg_music.mp3"))
    pygame.mixer.music.set_volume(0.3)  # Adjust volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error as e:
    print(f"Error loading background music: {e}")


def show_story_screen():
    """Displays the story introduction screen before the game starts."""
    font_title = pygame.font.SysFont('Arial', 50, bold=True)
    font_text = pygame.font.SysFont('Arial', 28)

    # Story text
    title_text = "Dark Forces Have Struck!"
    story_lines = [
        "You were tasked with guarding the royal princess...",
        "But in the dead of night, a horde of demons attacked.",
        "The princess was taken into the depths of the dungeon.",
        "Now, you must embark on a dangerous quest to rescue her.",
        "Prepare yourself, brave warrior!"
    ]

    # Background color
    screen.fill((0, 0, 0))

    # Render title
    title_rendered = font_title.render(title_text, True, (255, 0, 0))
    screen.blit(title_rendered, (SCREEN_WIDTH // 2 - title_rendered.get_width() // 2, 50))

    # Render story text line by line
    for i, line in enumerate(story_lines):
        text_rendered = font_text.render(line, True, (255, 255, 255))
        screen.blit(text_rendered, (SCREEN_WIDTH // 2 - text_rendered.get_width() // 2, 150 + i * 40))

    # Render instruction text
    instruction = font_text.render("Press SPACE to begin your journey...", True, (200, 200, 0))
    screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()  # Update the display

    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Press SPACE to start
                    waiting = False



# --- Player Setup ---
player = Character(400, 667, "Knight", 85, 100)  # (x, y, character type, HP)
player.speed = 3  # Set movement speeds

boss1_defeated = False  # Track if Boss1 is defeated


# Set frame counts for animations
frame_counts = {
    "idle": 15,
    "move": 8,
    "attack": 22,
    "ultimate": 22,
    "death": 15,
    "jump": 14,
    "shield": 7
}
player.frame_counts = frame_counts

# Load player animations
player.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{player.character_type}"))



# Door system for the Entrance Hall
doors = [
    {"x": 316, "y": 529, "width": 40, "height": 65,
     "destination": "left_path", "dest_x": 250, "dest_y": 430, "name": "Left Path"},
    {"x": 450, "y": 529, "width": 40, "height": 65,
     "destination": "right_path", "dest_x": 550, "dest_y": 430, "name": "Right Path"},
     # Add the portal to level 2 (initially hidden)
]

portal_to_level2 = {
    "x": 380, "y": 529, "width": 40, "height": 65,
    "destination": "level2", "dest_x": 120, "dest_y": 425, 
    "name": "Portal to Level 2",
    "visible": False  # Initially hidden
}


# Transition to Level 2
area_transition_doors = {
    "final_area": {
        "x": 400, "y": 50, "width": 40, "height": 65,
        "destination": "level2", "dest_x": 400, "dest_y": 450,
        "name": "Enter Level 2"
    }
}

# Return doors for paths
area_return_doors = {
    "left_path": {"x": 250, "y": 430, "width": 40, "height": 65, "destination": "entrance_hall", "dest_x": 400, "dest_y": 667, "name": "Return to Entrance"},
    "right_path": {"x": 550, "y": 430, "width": 40, "height": 65, "destination": "entrance_hall", "dest_x": 400, "dest_y": 667, "name": "Return to Entrance"},
    "final_area": {"x": 400, "y": 100, "width": 40, "height": 65, "destination": "entrance_hall", "dest_x": 400, "dest_y": 667, "name": "Return to Entrance"}
}

# The current area the player is in
current_area = "entrance_hall"

# Base hallway definitions for Level 1
base_hallway = [
    # === ENTRANCE CAVE (starting area) ===
    [400, 680, 400, 400, 500, "entrance_hall"],  # Main entrance path
    
    # === LEFT PATH (more extensive) ===
    [250, 450, 250, 200, 120, "left_corridor"],  # Longer vertical corridor
    [250, 200, -150, 200, 150, "left_chamber"],  # Extended horizontal chamber to the left
    [-150, 200, -150, -200, 120, "left_deep"],   # Much deeper path going upward
    
    # === RIGHT PATH (more extensive) ===
    [550, 450, 550, 200, 120, "right_corridor"],  # Longer vertical corridor
    [550, 200, 950, 200, 150, "right_chamber"],   # Extended horizontal chamber to the right
    [950, 200, 950, -200, 120, "right_deep"],     # Much deeper path going upward
    
    # === PATHS REJOIN (longer approach) ===
    [-150, -200, 400, -200, 150, "left_return"],  # Longer horizontal return path
    [950, -200, 400, -200, 150, "right_return"],  # Longer horizontal return path
    
    # === FINAL AREA (transition to Level 2) ===
    [400, -200, 400, -400, 200, "level2_entrance"],  # Deeper final approach
]

# Add branch paths
base_hallway += [
    # Left path branch
    [-150, 0, -350, 0, 100, "left_branch"],
    [-350, 0, -350, -100, 100, "left_branch_vertical"],
    
    # Right path branch
    [950, 0, 1150, 0, 100, "right_branch"],
    [1150, 0, 1150, -100, 100, "right_branch_vertical"],
]

# Area groupings for Level 1
area_hallways = {
    "entrance_hall": ["entrance_hall"],
    "left_path": ["left_corridor", "left_chamber", "left_deep", "left_return", "left_branch", "left_branch_vertical"],
    "right_path": ["right_corridor", "right_chamber", "right_deep", "right_return", "right_branch", "right_branch_vertical"],
    "final_area": ["level2_entrance"]
}

# Load teleportation sound effects
try:
    teleport_start_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "teleport_start.wav"))
    teleport_end_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "teleport_end.wav"))
    teleport_travel_sound = pygame.mixer.Sound(os.path.join("src", "assets", "sounds", "teleport_travel.wav"))
    # Set volume
    teleport_start_sound.set_volume(0.7)
    teleport_end_sound.set_volume(0.7)
    teleport_travel_sound.set_volume(0.5)
except Exception as e:
    print(f"Error loading teleportation sounds: {e}")
    print("Creating silent sounds as fallbacks")
    # Create silent sounds as fallbacks
    buffer = pygame.mixer.Sound(buffer=bytes(bytearray([0] * 44)))
    teleport_start_sound = buffer
    teleport_end_sound = buffer
    teleport_travel_sound = buffer

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
    
    # Use a consistent seed for connected hallways
    if seed is None:
        seed = hash((target_width, target_height))
    random.seed(seed)
    
    # Create one surface at the exact target size
    tiled_surf = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
    
    # Ensure tiles align perfectly to grid
    for y in range(0, target_height, fixed_tile_h):
        for x in range(0, target_width, fixed_tile_w):
            chosen_image = random.choice(processed_images)
            # Calculate exact portion to blit
            blit_w = min(fixed_tile_w, target_width - x)
            blit_h = min(fixed_tile_h, target_height - y)
            src_rect = pygame.Rect(0, 0, blit_w, blit_h)
            tiled_surf.blit(chosen_image, (x, y), src_rect)
    
    random.seed()
    return tiled_surf

# Load two different sets of portal animations - one for entrance, one for internal portals
entrancePortalAnimation = [
    load_image("backgrounds/portal1.png", scale=1.2),  # Keep original size for entrance
    load_image("backgrounds/portal2.png", scale=1.2),
    load_image("backgrounds/portal3.png", scale=1.2),
    load_image("backgrounds/portal4.png", scale=1.2),
    load_image("backgrounds/portal5.png", scale=1.2),
    load_image("backgrounds/portal6.png", scale=1.2),
    load_image("backgrounds/portal7.png", scale=1.2),
]

internalPortalAnimation = [
    load_image("backgrounds/portal1.png", scale=2.5),  # Much bigger for internal portals
    load_image("backgrounds/portal2.png", scale=2.5),
    load_image("backgrounds/portal3.png", scale=2.5),
    load_image("backgrounds/portal4.png", scale=2.5),
    load_image("backgrounds/portal5.png", scale=2.5),
    load_image("backgrounds/portal6.png", scale=2.5),
    load_image("backgrounds/portal7.png", scale=2.5),
]

# Portal glow colors
portal_glow_colors = [
    (80, 140, 255, 100),   # Blue glow
    (100, 150, 255, 80),   # Lighter blue
    (120, 160, 255, 60),   # Even lighter
    (140, 170, 255, 40),   # Almost white-blue
]

# Try to load warp/space tunnel images
try:
    warp_images = [
        load_image("effects/warp1.png"),
        load_image("effects/warp2.png"),
        load_image("effects/warp3.png"),
        load_image("effects/warp4.png"),
    ]
except Exception as e:
    print(f"Error loading warp images: {e}")
    # Create procedural warp images as fallbacks
    warp_images = []
    for i in range(4):
        img = pygame.Surface((800, 500), pygame.SRCALPHA)
        color = (0, 50 + i*50, 100 + i*40)
        # Draw some circles to create a tunnel effect
        for j in range(5):
            radius = 400 - j*60 - i*20
            thickness = 20 - i*3
            pygame.draw.circle(img, color, (400, 250), radius, thickness)
        warp_images.append(img)

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

# Load the entrance image
try:
    entrance_img = load_image("backgrounds/image.png", scale=1.5)
    print(f"Image loaded successfully, size: {entrance_img.get_size()}")
except Exception as e:
    print(f"Failed to load entrance image: {e}")
    # Create a default surface if the image fails to load
    entrance_img = pygame.Surface((800, 500))
    entrance_img.fill((50, 30, 80))  # Dark purple color as fallback

# Define a small set of core textures for your level paths
rock_floor = [load_image("backgrounds/lvl2_CaveHallwayFloor.jpg")]
lava_floor = [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)]
boss_floor = load_image("backgrounds/lvl2_BossMain.jpg")

# Dictionary to store hallway images by key
hallway_images = {
    # Entrance Hall Background
    "entrance_hall": entrance_img,
    
    # Left path - all rock floor for consistency
    "left_corridor": rock_floor,
    "left_chamber": rock_floor,
    "left_deep": rock_floor,
    "left_branch": rock_floor,
    "left_branch_vertical": rock_floor,
    "left_return": rock_floor,
    
    # Right path - all lava floor for consistency
    "right_corridor": lava_floor,
    "right_chamber": lava_floor,
    "right_deep": lava_floor,
    "right_branch": lava_floor,
    "right_branch_vertical": lava_floor,
    "right_return": lava_floor,
    
    # Final area
    "level2_entrance": boss_floor,
}

default_hallway_img = horizontal_tiles

# Define decoration objects - with fallback error handling
def load_decoration_image(filename, scale=1.0):
    try:
        return load_image(f"backgrounds/decoration/{filename}", scale)
    except Exception as e:
        print(f"Error loading decoration {filename}: {e}")
        fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
        fallback.fill((255, 0, 255, 128))  # Purple semi-transparent for debugging
        return fallback

# Load torch animation frames or create artificial animation
try:
    base_torch = load_decoration_image("torch.png", scale=0.3)
    if base_torch.get_width() == 64 and base_torch.get_height() == 64:  # Placeholder detected
        print("Warning: Using placeholder torch image")
        # Create a colored rectangle as fallback
        torch = pygame.Surface((20, 40), pygame.SRCALPHA)
        torch.fill((200, 100, 0))
        base_torch = torch
    
    # Create animation frames from the base torch if only one image is available
    torchAnimation = []
    for i in range(6):  # Increased to 6 frames for more variation
        # Create a copy of the base torch
        frame = base_torch.copy()
        
        # Add random variations for less predictable animation
        random_scale = random.uniform(0.9, 1.15)
        random_brightness = random.randint(-30, 50)
        
        # Scale frame randomly
        new_width = int(frame.get_width() * random_scale)
        new_height = int(frame.get_height() * random_scale)
        frame = pygame.transform.scale(frame, (new_width, new_height))
        
        # Adjust brightness randomly
        brightness_overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        if random_brightness > 0:
            # Brighter
            brightness_overlay.fill((random_brightness, random_brightness//2, 0, 0))
            frame.blit(brightness_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            # Darker
            brightness_overlay.fill((0, 0, 0, abs(random_brightness)))
            frame.blit(brightness_overlay, (0, 0))
        
        torchAnimation.append(frame)
    
    print(f"Created {len(torchAnimation)} torch animation frames")
except Exception as e:
    print(f"Error creating torch animation: {e}")
    # Emergency fallback
    torch = pygame.Surface((20, 40), pygame.SRCALPHA)
    torch.fill((200, 100, 0))
    torchAnimation = [torch, torch, torch, torch]

# Define decoration objects
wall_decorations = {
    "torch": torchAnimation[0],  # Will be updated dynamically during animation
}

# Helper function to place torch exactly on walls
def place_torch(segment_name, position, is_horizontal=True, side="left"):
    # For horizontal hallways, place on top/bottom edges
    # For vertical hallways, place on left/right edges
    if is_horizontal:
        if side == "top":
            return [segment_name, position, 0.0, "torch"]
        else:  # bottom
            return [segment_name, position, 1.17, "torch"]
    else:  # vertical
        if side == "left":
            return [segment_name, 0.0, position, "torch"]
        else:  # right
            return [segment_name, 1.17, position, "torch"]

# Define decoration placements - torches precisely along the borders
hallway_decorations = [
    # Left corridor (vertical hallway)
    place_torch("left_corridor", 0.1, False, "left"),
    place_torch("left_corridor", 0.3, False, "left"),
    place_torch("left_corridor", 0.7, False, "left"),
    place_torch("left_corridor", 0.9, False, "left"),
    place_torch("left_corridor", 0.1, False, "right"),
    place_torch("left_corridor", 0.3, False, "right"),
    place_torch("left_corridor", 0.7, False, "right"),
    place_torch("left_corridor", 0.9, False, "right"),
    
    # Left chamber (horizontal hallway)
    place_torch("left_chamber", 0.1, True, "top"),
    place_torch("left_chamber", 0.3, True, "top"),
    place_torch("left_chamber", 0.5, True, "top"),
    place_torch("left_chamber", 0.7, True, "top"),
    place_torch("left_chamber", 0.9, True, "top"),
    place_torch("left_chamber", 0.1, True, "bottom"),
    place_torch("left_chamber", 0.3, True, "bottom"),
    place_torch("left_chamber", 0.5, True, "bottom"),
    place_torch("left_chamber", 0.7, True, "bottom"),
    #place_torch("left_chamber", 0, True, "bottom"),
    
    # Left deep (vertical hallway)
    place_torch("left_deep", 0.1, False, "left"),
    place_torch("left_deep", 0.3, False, "left"),
   # place_torch("left_deep", 0.5, False, "left"),
    #place_torch("left_deep", 0.7, False, "left"),
    place_torch("left_deep", 0.9, False, "left"),
    place_torch("left_deep", 0.1, False, "right"),
    place_torch("left_deep", 0.3, False, "right"),
    place_torch("left_deep", 0.5, False, "right"),
    place_torch("left_deep", 0.7, False, "right"),
    #place_torch("left_deep", 0.9, False, "right"),
    
    # Right side corridors and rooms (similar pattern)
    place_torch("right_corridor", 0.1, False, "left"),
    place_torch("right_corridor", 0.3, False, "left"),
    place_torch("right_corridor", 0.7, False, "left"),
    place_torch("right_corridor", 0.9, False, "left"),
    place_torch("right_corridor", 0.1, False, "right"),
    place_torch("right_corridor", 0.3, False, "right"),
    place_torch("right_corridor", 0.7, False, "right"),
    place_torch("right_corridor", 0.9, False, "right"),
    
    place_torch("right_chamber", 0.1, True, "top"),
    place_torch("right_chamber", 0.3, True, "top"),
    place_torch("right_chamber", 0.5, True, "top"),
    place_torch("right_chamber", 0.7, True, "top"),
    place_torch("right_chamber", 0.9, True, "top"),
    #place_torch("right_chamber", 0.1, True, "bottom"),
    place_torch("right_chamber", 0.3, True, "bottom"),
    place_torch("right_chamber", 0.5, True, "bottom"),
    place_torch("right_chamber", 0.7, True, "bottom"),
    #place_torch("right_chamber", 0.9, True, "bottom"),
]

# Define floor objects - keeping only small_rocks
floor_objects = {
    "small_rocks": load_decoration_image("small_rocks.png", scale=0.3),
}

# Define floor object placements - keeping only small_rocks
floor_decorations = [
    # Format: [hallway_segment, relative_x, relative_y, object_type]
    ["left_chamber", 0.5, 0.5, "small_rocks"],
    ["left_chamber", 0.2, 0.3, "small_rocks"],
    ["left_chamber", 0.8, 0.7, "small_rocks"],
    ["left_deep", 0.3, 0.5, "small_rocks"],
    ["left_deep", 0.7, 0.3, "small_rocks"],
    ["right_chamber", 0.4, 0.6, "small_rocks"],
    ["right_chamber", 0.6, 0.4, "small_rocks"],
]

# Create stars/particles for the space travel effect
class SpaceParticle:
    def __init__(self, screen_width, screen_height, z_depth=10, forward=True):
        # Start from center of screen with random angle
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset(z_depth, forward)
        
    def reset(self, z_depth=10, forward=True):
        self.angle = random.uniform(0, math.pi * 2)
        self.z = random.uniform(1, z_depth) 
        # How far from center, 0 = center, 1 = edge
        self.distance = random.uniform(0.1, 0.9)
        self.speed = random.uniform(0.1, 0.3) * (1 if forward else -1)
        self.size = random.uniform(1, 3)
        self.color = random.choice([
            (255, 255, 255),  # White
            (200, 220, 255),  # Light blue
            (180, 180, 255),  # Light purple
            (255, 240, 200),  # Light yellow
        ])
        self.trail_length = random.randint(3, 8)
        self.alpha = random.randint(150, 255)
        
    def update(self, elapsed_ms):
        # Move the star along the z-axis (toward or away from viewer)
        self.z += self.speed * (elapsed_ms / 16.67)  # Scale by time
        
        # Reset if it's gone too far
        if self.z <= 0 or self.z > 20:
            self.reset(10, self.speed > 0)
            
        return True
        
    def draw(self, screen):
        # Calculate x,y based on z (perspective projection)
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Convert polar to cartesian coords with perspective
        perspective = 1 / self.z
        scale = self.distance * max(self.screen_width, self.screen_height) * 0.8
        x = center_x + math.cos(self.angle) * scale * perspective
        y = center_y + math.sin(self.angle) * scale * perspective
        
        # Size decreases with distance
        size = max(0.5, self.size / (self.z * 0.2))
        
        # Draw the star
        pygame.draw.circle(
            screen, 
            self.color, 
            (int(x), int(y)), 
            int(size)
        )
        
        # Draw trail
        for i in range(1, self.trail_length + 1):
            trail_size = max(0.5, size * (1 - i / self.trail_length))
            trail_x = x - (self.speed * math.cos(self.angle) * i * 2)
            trail_y = y - (self.speed * math.sin(self.angle) * i * 2)
            alpha = int(self.alpha * (1 - i / self.trail_length))
            
            s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                s, 
                (*self.color, alpha), 
                (int(trail_size), int(trail_size)), 
                int(trail_size)
            )
            screen.blit(s, (int(trail_x - trail_size), int(trail_y - trail_size)))

# Portal particles class for ambient portal effects
class PortalParticle:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        # Start from edge of portal and move outward
        self.angle = random.uniform(0, math.pi * 2)
        self.distance = random.uniform(10, radius)
        self.max_distance = radius + random.uniform(20, 50)
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.uniform(1, 3)
        self.alpha = random.randint(150, 255)
        self.color = random.choice([
            (100, 150, 255),  # Blue
            (120, 180, 255),  # Light blue
            (80, 120, 220),   # Dark blue
            (150, 200, 255),  # Very light blue
        ])
        
    def update(self):
        # Move particle outward
        self.distance += self.speed
        self.alpha -= 3
        
        # Check if particle should be removed
        if self.distance > self.max_distance or self.alpha <= 0:
            return False
        return True
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        # Calculate position based on angle and distance
        pos_x = self.x + math.cos(self.angle) * self.distance
        pos_y = self.y + math.sin(self.angle) * self.distance
        
        # Scale to screen coordinates
        scaled_x = pos_x * scale_x - camera_x
        scaled_y = pos_y * scale_y - camera_y
        scaled_size = self.size * scale_x
        
        # Draw particle
        s = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), 
                          (scaled_size, scaled_size), scaled_size)
        screen.blit(s, (scaled_x - scaled_size, scaled_y - scaled_size))

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

# Teleportation particles for the teleport effect
class TeleportParticle:
    def __init__(self, x, y, target_x, target_y, is_arrival=False):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.progress = 0.0 if not is_arrival else 0.7  # Start 70% through for arrival particles
        self.speed = random.uniform(0.01, 0.03)
        self.size = random.uniform(2, 5)
        self.color = (100, 150, 255)  # Base blue color
        self.alpha = 255
        self.is_arrival = is_arrival
        # Slightly random path
        self.angle_offset = random.uniform(-0.5, 0.5)
        self.radius_variance = random.uniform(0.8, 1.2)
        
    def update(self):
        self.progress += self.speed
        
        if self.is_arrival:
            # Arrival particles fade in then out
            if self.progress < 0.85:
                self.alpha = min(255, self.alpha + 10)
            else:
                self.alpha = max(0, self.alpha - 20)
        else:
            # Departure particles fade out
            self.alpha = max(0, int(255 * (1 - self.progress * 1.2)))
        
        return self.progress < 1.0 and self.alpha > 0
    
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        if self.is_arrival:
            # Arrival particles converge on destination
            t = 1.0 - (1.0 - self.progress) * (1.0 - self.progress)  # Ease in
            pos_x = self.target_x + (self.x - self.target_x) * (1.0 - t)
            pos_y = self.target_y + (self.y - self.target_y) * (1.0 - t)
        else:
            # Departure particles move from player to portal
            t = self.progress * self.progress  # Ease out
            pos_x = self.x + (self.target_x - self.x) * t
            pos_y = self.y + (self.target_y - self.y) * t
        
        # Add some swirl to the particles
        radius = 20 * self.radius_variance * (1 - self.progress)  # Gets smaller as it approaches target
        angle = self.progress * 10 + self.angle_offset
        pos_x += math.cos(angle) * radius
        pos_y += math.sin(angle) * radius
        
        # Scale to screen coordinates
        scaled_x = pos_x * scale_x - camera_x
        scaled_y = pos_y * scale_y - camera_y
        scaled_size = self.size * (1 - self.progress * 0.5) * scale_x
        
        # Color shifts based on progress - blue to white
        r = min(255, int(self.color[0] + (255 - self.color[0]) * self.progress))
        g = min(255, int(self.color[1] + (255 - self.color[1]) * self.progress))
        b = min(255, int(self.color[2] + (255 - self.color[2]) * self.progress))
        color = (r, g, b, self.alpha)
        
        # Draw particle
        s = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (scaled_size, scaled_size), scaled_size)
        screen.blit(s, (scaled_x - scaled_size, scaled_y - scaled_size))

# Standard particle class
class Particle:
    def __init__(self, x, y, color, speed, size, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        # Add some horizontal drift
        self.drift_x = random.uniform(-0.2, 0.2)
        
    def update(self):
        self.y -= self.speed
        self.x += self.drift_x
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        scaled_x = self.x * scale_x - camera_x
        scaled_y = self.y * scale_y - camera_y
        scaled_size = self.size * scale_x
        alpha = 255 * (1 - self.age / self.lifetime)
        color_with_alpha = (*self.color, int(alpha))
        s = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (scaled_size, scaled_size), scaled_size)
        screen.blit(s, (scaled_x - scaled_size, scaled_y - scaled_size))

# Create portal and teleport particle lists
portal_particles = {}  # Dictionary to store particles for each door
teleport_particles = []
space_particles = []

# Function to generate portal particles
def generate_portal_particles(door_id, x, y, radius=30):
    if door_id not in portal_particles:
        portal_particles[door_id] = []
    
    # Add new particles occasionally
    if random.random() < 0.2:  # Adjust rate as needed
        portal_particles[door_id].append(PortalParticle(x, y, radius))
    
    # Update existing particles
    portal_particles[door_id] = [p for p in portal_particles[door_id] if p.update()]

# Initialize space particles
def initialize_space_particles(count=150):
    global space_particles
    space_particles = []
    for _ in range(count):
        space_particles.append(SpaceParticle(SCREEN_WIDTH, SCREEN_HEIGHT))

# Function to draw portal with enhanced effects but different sizes
def draw_enhanced_portal(screen, door, door_x, door_y, scale_x, scale_y, camera_x, camera_y, is_entrance=False):
    door_id = f"{door['destination']}_{door['dest_x']}_{door['dest_y']}"
    
    # Handle missing width/height in door definition
    door_width = door.get("width", 40)  # Default width if not specified
    door_height = door.get("height", 65)  # Default height if not specified
    
    door_center_x = door["x"] + door_width / 2
    door_center_y = door["y"] + door_height / 2
    
    # Choose appropriate portal animation and glow size based on portal type
    if is_entrance:
        # Entrance portals - smaller glows and original animation
        portal_frames = entrancePortalAnimation
        glow_sizes = [10, 15, 20, 25]  # Smaller glow sizes
        particle_radius = 25  # Smaller particle radius
    else:
        # Internal portals - larger glows and bigger animation
        portal_frames = internalPortalAnimation
        glow_sizes = [15, 25, 35, 45]  # Larger glow sizes
        particle_radius = 40  # Larger particle radius
    
    # Draw portal glow (multiple concentric circles with decreasing alpha)
    for i, color in enumerate(portal_glow_colors):
        glow_size = glow_sizes[i]
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface, 
                   (door_x - glow_size + door_width/2 * scale_x, 
                    door_y - glow_size + door_height/2 * scale_y))
    
    # Apply a slight pulse/scale effect to the portal
    pulse = 0.05 * math.sin(pygame.time.get_ticks() / 200)
    portal_scale = 1.0 + pulse
    
    # Get portal image and scale it
    portal_img = portal_frames[portalFrame]
    orig_width, orig_height = portal_img.get_size()
    
    # Apply pulse scaling
    new_width = int(orig_width * portal_scale)
    new_height = int(orig_height * portal_scale)
    scaled_portal = pygame.transform.scale(portal_img, (new_width, new_height))
    
    # Draw the portal image (centered on door)
    portal_x = door_x - (new_width - door_width * scale_x) / 2
    portal_y = door_y - (new_height - door_height * scale_y) / 2
    screen.blit(scaled_portal, (portal_x, portal_y))
    
    # Generate and draw portal particles
    generate_portal_particles(door_id, door_center_x, door_center_y, particle_radius)
    for particle in portal_particles.get(door_id, []):
        particle.draw(screen, scale_x, scale_y, camera_x, camera_y)

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
    threshold = 50  # Interaction distance
    
    # Check entrance hall doors
    if current_area == "entrance_hall":
        for door in doors:
            door_center_x = door["x"] + door["width"] / 2
            door_center_y = door["y"] + door["height"] / 2
            distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
            
            if distance < threshold:
                return door
    
    # Check area transition doors
    if current_area in area_transition_doors:
        door = area_transition_doors[current_area]
        door_center_x = door["x"] + door["width"] / 2
        door_center_y = door["y"] + door["height"] / 2
        distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
        
        if distance < threshold:
            return door
    
    # Check area return doors with better error handling
    if current_area in area_return_doors:
        door = area_return_doors[current_area]
        # Make sure width and height exist, default to 40x65 if not specified
        door_width = door.get("width", 40)
        door_height = door.get("height", 65)
        
        door_center_x = door["x"] + door_width / 2
        door_center_y = door["y"] + door_height / 2
        
        distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
        
        if distance < threshold:
            return door
            
    return None

# Enhanced teleport effect function
def initiate_teleport_effect(origin_x, origin_y, dest_x, dest_y, particles_count=50):
    # Clear existing teleport particles
    teleport_particles.clear()
    
    # Create departure particles (from player to portal)
    for _ in range(particles_count):
        teleport_particles.append(
            TeleportParticle(origin_x, origin_y, dest_x, dest_y, is_arrival=False)
        )
    
    # Create arrival particles (from random positions toward destination)
    for _ in range(particles_count):
        # Random positions around destination
        rand_x = dest_x + random.uniform(-100, 100)
        rand_y = dest_y + random.uniform(-100, 100)
        teleport_particles.append(
            TeleportParticle(rand_x, rand_y, dest_x, dest_y, is_arrival=True)
        )

# Enhanced space teleportation variables
teleport_active = False
teleport_start_time = 0
teleport_duration = 5500 # ms
teleport_origin = None
teleport_destination = None
teleport_destination_info = None
teleport_warp_frame = 0
teleport_warp_time = 0

# Enhanced space teleportation
def initiate_space_teleport(destination, dest_x, dest_y):
    global teleport_active, teleport_start_time, teleport_origin, teleport_destination
    global teleport_destination_info, teleport_warp_frame, teleport_warp_time
    
    # Store teleport information
    teleport_active = True
    teleport_start_time = pygame.time.get_ticks()
    teleport_origin = (player.x, player.y) 
    teleport_destination = [dest_x, dest_y]
    teleport_destination_info = {
        "destination": destination,
        "dest_x": dest_x,
        "dest_y": dest_y
    }
    teleport_warp_frame = 0
    teleport_warp_time = 0
    
    # Play start sound
    teleport_start_sound.play()
    
    # Initialize space particles going forward
    for particle in space_particles:
        particle.reset(10, True)
    
    # Also start the travel sound
    teleport_travel_sound.play(-1)  # Loop until stopped


# Next, modify the update_space_teleport function to ensure sounds and visuals are in sync
def update_space_teleport(elapsed_ms):
    global teleport_active, current_area, teleport_warp_frame
    global teleport_warp_time, teleport_destination_info
    
    current_time = pygame.time.get_ticks()
    teleport_elapsed = current_time - teleport_start_time
    
    # Update warp animation frame
    teleport_warp_time += elapsed_ms
    if teleport_warp_time >= 100:  # Change frame every 100ms
        teleport_warp_time = 0
        teleport_warp_frame = (teleport_warp_frame + 1) % len(warp_images)
    
    # Update space particles
    for particle in space_particles:
        particle.update(elapsed_ms)
    
    # Check if teleport is complete
    if teleport_elapsed >= teleport_duration:
        # Complete the teleport
        teleport_active = False
        
        # Stop the travel sound
        teleport_travel_sound.stop()
        
        # Play end sound
        teleport_end_sound.play()
        
        #spawn enemy
        spawn_enemies_for_area(teleport_destination_info["destination"])
        
        # Actually teleport the player
        if teleport_destination_info:
            current_area = teleport_destination_info["destination"]
            player.x = teleport_destination_info["dest_x"]
            player.y = teleport_destination_info["dest_y"]
            
            # Add movement trail effect
            for i in range(10):  # Add more effects
                movement_effects.append(MovementEffect(player.x, player.y))
            
            # Initialize arrival teleport particles
            initiate_teleport_effect(
                player.x, player.y, 
                player.x, player.y, 
                particles_count=100
            )
            
            teleport_destination_info = None
            
            # Reinitialize some particles going backward
            for i in range(len(space_particles) // 2):
                space_particles[i].reset(10, False)
                
    return teleport_active



def draw_space_teleport(screen):
    if not teleport_active:
        return
    
    current_time = pygame.time.get_ticks()
    teleport_elapsed = current_time - teleport_start_time
    progress = min(1.0, teleport_elapsed / teleport_duration)
    
    # Warp tunnel effect parameters
    warp_img = warp_images[teleport_warp_frame]
    rotation_angle = (teleport_elapsed / 50) % 360
    pulse_amount = math.sin(teleport_elapsed / 200) * 0.15

    # Spiral zoom effect
    if progress < 0.25:
        base_scale = progress / 0.25
        spiral_factor = math.sin(teleport_elapsed / 100) * 0.1 * progress
    elif progress > 0.75:
        base_scale = (1.0 - progress) / 0.25
        spiral_factor = math.sin(teleport_elapsed / 100) * 0.1 * (1.0 - progress)
    else:
        base_scale = 1.0
        spiral_factor = math.sin(teleport_elapsed / 100) * 0.1

    scale = base_scale * (1.0 + pulse_amount)
    alpha = 255 if 0.25 <= progress <= 0.75 else int(255 * (progress * 3 if progress < 0.25 else (1 - progress) * 3))

    # Create warp tunnel surface
    scaled_warp = pygame.transform.scale(warp_img, (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)))
    temp_surface = pygame.Surface(scaled_warp.get_size(), pygame.SRCALPHA)
    temp_surface.blit(scaled_warp, (0, 0))

    # Apply spiral distortion
    vortex_surface = pygame.Surface(temp_surface.get_size(), pygame.SRCALPHA)
    for x in range(0, temp_surface.get_width(), 4):
        for y in range(0, temp_surface.get_height(), 4):
            dx = x - temp_surface.get_width() // 2
            dy = y - temp_surface.get_height() // 2
            distance = math.hypot(dx, dy)
            if distance > 0:
                angle = math.atan2(dy, dx)
                new_angle = angle + spiral_factor * distance / (temp_surface.get_width() / 2)
                new_distance = distance * (1.0 + pulse_amount * math.sin(angle * 4))
                new_x = int(new_distance * math.cos(new_angle)) + temp_surface.get_width() // 2
                new_y = int(new_distance * math.sin(new_angle)) + temp_surface.get_height() // 2
                if 0 <= new_x < temp_surface.get_width() and 0 <= new_y < temp_surface.get_height():
                    vortex_surface.blit(temp_surface, (x, y), (new_x, new_y, 4, 4))

    # Final warp tunnel rendering
    rotated_surface = pygame.transform.rotate(vortex_surface, rotation_angle * (1 if progress < 0.5 else -1))
    rotated_surface.set_alpha(alpha)
    screen.blit(rotated_surface, 
               ((SCREEN_WIDTH - rotated_surface.get_width()) // 2 + math.sin(teleport_elapsed / 300) * SCREEN_WIDTH * 0.05,
                (SCREEN_HEIGHT - rotated_surface.get_height()) // 2 + math.cos(teleport_elapsed / 250) * SCREEN_HEIGHT * 0.05))

    # Player teleportation effects
    if teleport_origin and teleport_destination and player:
        FADE_DURATION = 0.3
        SHOCKWAVE_DURATION = 0.15
        
        # Position and alpha calculation
        if progress < FADE_DURATION:
            pos = pygame.math.Vector2(teleport_origin)
            alpha_player = 255 * (1 - progress / FADE_DURATION)
            show_shockwave = progress < SHOCKWAVE_DURATION
        elif progress > 1 - FADE_DURATION:
            t = (progress - (1 - FADE_DURATION)) / FADE_DURATION
            pos = pygame.math.Vector2(teleport_destination)
            alpha_player = 255 * t
            show_shockwave = (1 - progress) < SHOCKWAVE_DURATION
        else:
            pos = pygame.math.Vector2(-1000, -1000)
            alpha_player = 0
            show_shockwave = False

        # Screen coordinates
        scale_x = SCREEN_WIDTH / BASE_WIDTH
        scale_y = SCREEN_HEIGHT / BASE_HEIGHT
        screen_pos = (pos.x * scale_x, pos.y * scale_y)
        centered_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if alpha_player > 0:
            # Save player state
            original_rect = player.rect.copy()
            original_pos = (player.x, player.y)
            player.rect.midbottom = centered_pos

            # 1. Shockwave effect
            if show_shockwave:
                shockwave_radius = 100 * (progress % SHOCKWAVE_DURATION) / SHOCKWAVE_DURATION
                pygame.draw.circle(screen, (100, 150, 255), centered_pos, int(shockwave_radius), 4)
                pygame.draw.circle(screen, (200, 255, 255, 100), centered_pos, int(shockwave_radius * 0.8), 2)

            # 2. Motion trail
            if not hasattr(player, 'teleport_trail'):
                player.teleport_trail = []
            
            if random.random() < 0.3:
                trail_image = pygame.transform.rotozoom(
                    player.current_image,
                    random.uniform(-20, 20),
                    0.5 + 0.5 * random.random()
                )
                trail_image.set_alpha(int(alpha_player * 0.6))
                player.teleport_trail.append({
                    'image': trail_image,
                    'pos': centered_pos,
                    'time': current_time
                })
            
            # Draw and decay trail
            for i in reversed(range(len(player.teleport_trail))):
                segment = player.teleport_trail[i]
                age = current_time - segment['time']
                if age > 300:
                    del player.teleport_trail[i]
                else:
                    segment['image'].set_alpha(int(255 - age * 0.8))
                    screen.blit(segment['image'], segment['pos'])

            # 3. Distortion effect
            distortion_size = (player.rect.width * 2, player.rect.height * 2)
            distortion_surface = pygame.Surface(distortion_size, pygame.SRCALPHA)
            pygame.draw.circle(distortion_surface, (255, 255, 255, 50), 
                              (player.rect.width, player.rect.height), 
                              player.rect.width // 2)
            screen.blit(distortion_surface, 
                       (centered_pos[0] - player.rect.width, 
                        centered_pos[1] - player.rect.height * 1.5))

            # 4. Enhanced glow
            glow_size = 20 + 10 * math.sin(current_time / 50)
            glow_surface = pygame.Surface((player.rect.width + glow_size * 2, 
                                          player.rect.height + glow_size * 2), 
                                         pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surface, 
                              (100, 150, 255, 100 + 50 * math.sin(current_time / 100)), 
                              (0, 0) + glow_surface.get_size())
            screen.blit(glow_surface, 
                       (centered_pos[0] - player.rect.width // 2 - glow_size, 
                        centered_pos[1] - player.rect.height - glow_size))

            # 5. Main player sprite with shake
            current_image = player.current_image.copy()
            current_image.set_alpha(int(alpha_player))
            
            if progress > FADE_DURATION and progress < 1 - FADE_DURATION:
                shake_offset = pygame.math.Vector2(random.uniform(-5, 5), 
                                                  random.uniform(-5, 5))
                screen.blit(current_image, 
                           (centered_pos[0] + shake_offset.x, 
                            centered_pos[1] + shake_offset.y))
            else:
                screen.blit(current_image, centered_pos)

            # Restore player state
            player.rect = original_rect
            player.x, player.y = original_pos

    # Enhanced particle system
    for particle in space_particles:
        particle.speed *= 1.01 if teleport_elapsed % 500 < 250 else 0.99
        particle.draw(screen)

        # Additional particle effects during teleport
        if hasattr(particle, 'teleport_interaction'):
            dx = particle.x - centered_pos[0]
            dy = particle.y - centered_pos[1]
            distance = math.hypot(dx, dy)
            
            if distance < 200:
                particle.color = (255, 255, 255)
                particle.size *= 1.02
                particle.speed *= 0.95
                particle.angle += math.atan2(dy, dx) * 0.1

    # Swirling color effects
    for i in range(12):
        angle = (i / 12) * math.tau + teleport_elapsed / 1000
        radius = SCREEN_WIDTH * 0.4 * (1 + math.sin(teleport_elapsed / 500) * 0.2)
        pos = pygame.math.Vector2(SCREEN_WIDTH // 2 + math.cos(angle) * radius,
                                 SCREEN_HEIGHT // 2 + math.sin(angle) * radius)
        hue = (i * 255 / 12 + teleport_elapsed / 20) % 255
        color = pygame.Color(0)
        color.hsva = (hue, 70, 100, 50)
        pygame.draw.circle(screen, color, pos, 10 * scale)

    # Overlay flash effect
    if progress < 0.08 or progress > 0.92:
        flash_intensity = (0.08 - abs(progress - 0.08)) * 12 if progress < 0.08 else (0.08 - abs(progress - 0.92)) * 12
        flash_alpha = int(255 * flash_intensity)
        flash_color = (255, 255, 255) if progress < 0.08 else (
            int(255 * (1 - (progress - 0.92) / 0.08) + 100 * ((progress - 0.92) / 0.08)),
            int(255 * (1 - (progress - 0.92) / 0.08) + 150 * ((progress - 0.92) / 0.08)),
            int(255 * (1 - (progress - 0.92) / 0.08) + 255 * ((progress - 0.92) / 0.08))
        )
        flash_surface = pygame.Surface(screen.get_size())
        flash_surface.fill(flash_color)
        flash_surface.set_alpha(flash_alpha)
        screen.blit(flash_surface, (0, 0))
# Enhanced SpaceParticle class with more dynamic movement
class SpaceParticle:
    def __init__(self, screen_width, screen_height, z_depth=10, forward=True):
        # Start from center of screen with random angle
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset(z_depth, forward)
        # Add oscillation parameters
        self.oscillation_speed = random.uniform(0.01, 0.05)
        self.oscillation_amplitude = random.uniform(0.1, 0.3)
        self.oscillation_offset = random.uniform(0, math.pi * 2)
        
    def reset(self, z_depth=10, forward=True):
        self.angle = random.uniform(0, math.pi * 2)
        self.z = random.uniform(1, z_depth) 
        # How far from center, 0 = center, 1 = edge
        self.distance = random.uniform(0.1, 0.9)
        self.speed = random.uniform(0.1, 0.3) * (1 if forward else -1)
        self.size = random.uniform(1, 3)
        self.color = random.choice([
            (255, 255, 255),  # White
            (200, 220, 255),  # Light blue
            (180, 180, 255),  # Light purple
            (255, 240, 200),  # Light yellow
            (150, 230, 255),  # Cyan-blue
            (230, 210, 255),  # Light lavender
        ])
        self.trail_length = random.randint(5, 12)  # Longer trails
        self.alpha = random.randint(150, 255)
        # Add spiral motion
        self.spiral_factor = random.uniform(-0.1, 0.1)
        # Reset oscillation offset
        self.oscillation_offset = random.uniform(0, math.pi * 2)
        
    def update(self, elapsed_ms):
        # Move the star along the z-axis (toward or away from viewer)
        self.z += self.speed * (elapsed_ms / 16.67)  # Scale by time
        
        # Add spiral motion to angle
        self.angle += self.spiral_factor * (elapsed_ms / 100)
        
        # Reset if it's gone too far
        if self.z <= 0 or self.z > 20:
            self.reset(10, self.speed > 0)
            
        return True
        
    def draw(self, screen):
        # Calculate x,y based on z (perspective projection)
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Current time for oscillation
        current_time = pygame.time.get_ticks() / 1000
        
        # Add oscillation to distance for more dynamic movement
        oscillating_distance = self.distance * (1 + self.oscillation_amplitude * 
                                               math.sin(current_time * self.oscillation_speed + self.oscillation_offset))
        
        # Convert polar to cartesian coords with perspective
        perspective = 1 / self.z
        scale = oscillating_distance * max(self.screen_width, self.screen_height) * 0.8
        
        # Add wobble to the angle
        wobble_angle = self.angle + math.sin(current_time * 2 + self.oscillation_offset) * 0.1
        
        x = center_x + math.cos(wobble_angle) * scale * perspective
        y = center_y + math.sin(wobble_angle) * scale * perspective
        
        # Size decreases with distance but pulses slightly
        pulse = 1.0 + 0.2 * math.sin(current_time * 3 + self.oscillation_offset)
        size = max(0.5, self.size * pulse / (self.z * 0.2))
        
        # Color pulsation
        color_pulse = abs(math.sin(current_time + self.oscillation_offset))
        r = min(255, int(self.color[0] * (0.8 + 0.2 * color_pulse)))
        g = min(255, int(self.color[1] * (0.8 + 0.2 * color_pulse)))
        b = min(255, int(self.color[2] * (0.8 + 0.2 * color_pulse)))
        current_color = (r, g, b)
        
        # Draw the star
        pygame.draw.circle(
            screen, 
            current_color, 
            (int(x), int(y)), 
            int(size)
        )
        
        # Draw enhanced trail with wave motion
        for i in range(1, self.trail_length + 1):
            trail_ratio = i / self.trail_length
            trail_size = max(0.5, size * (1 - trail_ratio))
            
            # Add wave motion to trail
            wave_factor = math.sin(trail_ratio * math.pi * 4 + current_time * 2) * 2
            
            trail_x = x - (self.speed * math.cos(wobble_angle) * i * 2) + wave_factor
            trail_y = y - (self.speed * math.sin(wobble_angle) * i * 2) + wave_factor
            
            alpha = int(self.alpha * (1 - trail_ratio))
            
            s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                s, 
                (*current_color, alpha), 
                (int(trail_size), int(trail_size)), 
                int(trail_size)
            )
            screen.blit(s, (int(trail_x - trail_size), int(trail_y - trail_size)))

# Render decorations in a hallway segment
def draw_decorations(screen, segment, scale_x, scale_y, camera_x, camera_y):
    start_x, start_y, end_x, end_y, width, image_key = segment
    half_width = width / 2
    
    # Calculate segment rectangle
    if start_y == end_y:
        rect_x = min(start_x, end_x)
        rect_y = start_y - half_width
        rect_width = abs(end_x - start_x)
        rect_height = width
        is_horizontal = True
    else:
        rect_x = start_x - half_width
        rect_y = min(start_y, end_y)
        rect_width = width
        rect_height = abs(end_y - start_y)
        is_horizontal = False
        
    # Draw wall decorations (torches) for this segment
    for decor in hallway_decorations:
        segment_name, rel_x, rel_y, decor_type = decor
        if segment_name == image_key:
            # Position torches exactly on walls
            decor_x = rect_x + (rect_width * rel_x)
            decor_y = rect_y + (rect_height * rel_y)
            
            # Fine-tune torch positioning based on hallway orientation
            if is_horizontal:
                # For horizontal hallways, offset torch position slightly inward from wall
                if rel_y == 0.0:  # Top wall
                    decor_y += 5  # Offset from top wall
                else:  # Bottom wall
                    decor_y -= 20  # Offset from bottom wall
            else:
                # For vertical hallways, offset torch position slightly inward from wall
                if rel_x == 0.0:  # Left wall
                    decor_x += 5  # Offset from left wall
                else:  # Right wall
                    decor_x -= 20  # Offset from right wall
            
            scaled_decor_x = decor_x * scale_x - camera_x
            scaled_decor_y = decor_y * scale_y - camera_y
            
            try:
                # Use the current animation frame for torches
                if decor_type == "torch":
                    # Always use the current animation frame
                    decor_img = torchAnimation[torchFrame]
                else:
                    decor_img = wall_decorations[decor_type]
                
                # Center the torch image at its base
                img_width, img_height = decor_img.get_size()
                screen.blit(decor_img, (scaled_decor_x - img_width//2, scaled_decor_y - img_height))
            except Exception as e:
                print(f"Error drawing decoration {decor_type}: {e}")
    
    # Draw floor objects for this segment
    for obj in floor_decorations:
        segment_name, rel_x, rel_y, obj_type = obj
        if segment_name == image_key:
            obj_x = rect_x + (rect_width * rel_x)
            obj_y = rect_y + (rect_height * rel_y)
            scaled_obj_x = obj_x * scale_x - camera_x
            scaled_obj_y = obj_y * scale_y - camera_y
            try:
                obj_img = floor_objects[obj_type]
                # Center the floor object
                img_width, img_height = obj_img.get_size()
                screen.blit(obj_img, (scaled_obj_x - img_width//2, scaled_obj_y - img_height//2))
            except Exception as e:
                print(f"Error drawing floor object {obj_type}: {e}")

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



all_enemies = pygame.sprite.Group()

enemy_positions = {
    "left_path": [("Mob1", (250, 400)), ("Mob3", (250, 250)), ("Mob2", (-150, -100)), ("Mob2", (-50, 200)), ("Mob3", (-250, 0)), ("Mob1", (-100, 200))], 
    "right_path": [("Mob1", (-100, 200)), ("Mob2", (-50, 200)), ("Mob3", (550, 200)), ("Mob2", (800, 220)), ("Mob3", (1000, 0)), ("Boss1", (600, -200))],
}

def spawn_enemies_for_area(area):
    """Spawn enemies when entering a new area."""
    global all_enemies
    all_enemies.empty()

    if area in enemy_positions:
        for enemy_type, pos in enemy_positions[area]:
            if enemy_type == "Boss1":
                enemy = Boss1(pos[0], pos[1], is_in_hallway)
            else:
                animations = load_mob_animations(enemy_type)
                enemy = Enemy(pos[0], pos[1], animations, is_in_hallway)
            
            all_enemies.add(enemy)



def check_enemy_attacks(player, enemies):
    """Check for enemy attacks hitting the player"""
    for enemy in enemies:
        # Only check enemies that are currently in an attack state
        if enemy.can_attack():
            # Calculate offset for mask collision detection
            offset_x = enemy.rect.x - player.rect.x
            offset_y = enemy.rect.y - player.rect.y
            
            # Check if attack hitbox overlaps with player
            if player.current_mask.overlap(enemy.mask, (offset_x, offset_y)):
                # Deal damage to player
                damage = enemy.get_damage()
                player.take_damage(damage)


def show_game_over_screen():
    global running

    # Load font and set text
    font = pygame.font.SysFont('Arial', 36)
    game_over_text = font.render("YOU DIED", True, (200, 0, 0))
    restart_text = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

    # Ensure death animation has enough frames
    death_frames = player.animations.get("death", [player.current_image])
    death_frame = death_frames[min(2, len(death_frames) - 1)]  # Use frame 2 if possible, else last frame
    scaled_death_frame = pygame.transform.scale(death_frame, (150, 150))  # Resize image

    while True:
        screen.fill((0, 0, 0))

        # Draw text
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 20))

        # Draw player's death frame
        screen.blit(scaled_death_frame, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 200))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    reset_player()  # Call reset function
                    return  # Exit game over screen


def reset_player():
    global current_area
    
    player.health = player.max_health  # Restore full health
    player.dead = False  # Remove death state
    player.frame_index = 0  # Reset animation frame
    player.x, player.y = 400, 667  # Move player back to starting position
    player.attacking = False
    player.using_ultimate = False
    player.shielding = False

    # Ensure animations are working properly
    player.action = "idle"  
    
    current_area = "entrance_hall"
    
    all_enemies.empty()
    
    
def show_level_transition(text):
    #Displays a transition screen before switching levels.
    font = pygame.font.SysFont('Arial', 48, bold=True)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))  # Black background

    fade_alpha = 0
    fade_duration = 2000  # Transition lasts 2 seconds
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < fade_duration:
        fade_alpha = min(255, (pygame.time.get_ticks() - start_time) / fade_duration * 255)
        fade_surface.set_alpha(int(fade_alpha))  #

        screen.fill((0, 0, 0))  # Clear screen
        screen.blit(fade_surface, (0, 0))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)  # Maintain frame rate


# Global variable to store player data
player_state = {}

def save_player_state(player):
    global player_state  # Use the global dictionary
    player_state = {
        "health": player.health,
        "max_health": player.max_health,
    }

    # Save to a file as backup
    with open("player_state.json", "w") as f:
        json.dump(player_state, f)    

# Initialize game state variables
clock = pygame.time.Clock()
movement_effects = []
particles = []
step_counter = 0
running = True

boss_defeat_count = 0

sparks = []

# Animation timers
portalFrame = 0
portalTime = 0
torchFrame = 0
torchTime = 0

# Initialize space particles
initialize_space_particles(200)  # Create 200 space particles

# ==================== MAIN GAME LOOP ====================
show_story_screen()

while running:      
    if not player.dead:
        # Get elapsed time for animations
        elapsed_ms = clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                # Reinitialize space particles for new screen size
                initialize_space_particles(200)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and not teleport_active:
                    door = is_near_door()
                    if door:
                        # Start space teleport instead of regular teleport
                        initiate_space_teleport(door["destination"], door["dest_x"], door["dest_y"])
                        
                #Player Controls
                if event.key == pygame.K_f:
                    player.toggle_shield()
                if event.key == pygame.K_q:
                    if player.shielding:
                        player.shielding = False
                    player.attack(all_enemies, sparks)
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_x:
                    if player.shielding:
                        player.shielding = False
                    player.use_ultimate(all_enemies, sparks)
        
        if current_area in enemy_positions:
                all_enemies.update(clock.get_time())
        
        # Spawn new particles based on area
        if current_area == "left_path" and random.random() < 0.05:
            # Dust particles in left path
            x = player.x + random.randint(-100, 100)
            y = player.y + random.randint(-100, 100)
            color = (200, 200, 200)  # Dust color
            particles.append(Particle(x, y, color, 0.2, 2, 60))
            
        if current_area == "right_path" and random.random() < 0.05:
            # Ember particles in right path (lava area)
            x = player.x + random.randint(-100, 100)
            y = player.y + random.randint(-100, 100)
            color = (255, 165, 0)  # Orange embers
            particles.append(Particle(x, y, color, 0.5, 1, 40))                
            
        # Handle space teleport if active, otherwise normal movement
        if teleport_active:
            # Update the space teleport effect
            update_space_teleport(elapsed_ms)
        else:
            # Handle normal player movement
            scale_x = SCREEN_WIDTH / BASE_WIDTH
            scale_y = SCREEN_HEIGHT / BASE_HEIGHT
            original_pos = (player.x, player.y)

            keys = pygame.key.get_pressed()

            old_x, old_y = player.x, player.y
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = player.speed
            player.move(dx, dy)
            if not is_in_hallway(player.x, player.y):
                player.x, player.y = old_x, old_y
            
    
            # Check if new position is valid
            valid_position = True
    
            # Special handling for entrance hall (cave shape)
            if current_area == "entrance_hall":
                # Base on the visible cave floor
                # The floor area (bottom of screen)
                if player.y >= 465:  # Bottom area
                    min_x = 320  # Left boundary
                    max_x = 480  # Right boundary
                # Near the steps
                else:
                    min_x = 450  # Left boundary
                    max_x = 480  # Right boundary
                
                # Vertical limits - IMPORTANT!
                min_y = 400  # Don't go above this (near stairs)
                max_y = 667  # Don't go below this (bottom of visible floor)
                
                # Check if position is within entrance bounds
                within_entrance = min_x <= player.x <= max_x and min_y <= player.y <= max_y
                
                if not within_entrance:
                    valid_position = False
    
            # If position is invalid, roll back to previous position
            if not valid_position:
                player.x, player.y = old_x, old_y
                player.moving = False  # Stop the walking animation
    
            # Update player state
            player.update()
                
        # Camera positioning (only if not teleporting)
        if not teleport_active:
            scale_x = SCREEN_WIDTH / BASE_WIDTH
            scale_y = SCREEN_HEIGHT / BASE_HEIGHT
            scaled_player_x = int(player.x * scale_x)
            scaled_player_y = int(player.y * scale_y)
            camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
            camera_y = scaled_player_y - (SCREEN_HEIGHT // 2)
            screen.fill(BLACK)
            
            # Get current hallway segments
            current_hallway_segments = []
            for segment in base_hallway:
                start_x, start_y, end_x, end_y, width, image_key = segment
                if image_key in area_hallways.get(current_area, []):
                    current_hallway_segments.append(segment)
            
            # Draw hallways and decorations
            for segment in current_hallway_segments:
                start_x, start_y, end_x, end_y, width, image_key = segment
                half_width = width / 2
                hallway_image = hallway_images.get(image_key, default_hallway_img)
                
                # Calculate segment rectangle
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
                
                # Draw hallway segment
                if isinstance(hallway_image, list):
                    cache_key = (image_key, scaled_rect_width, scaled_rect_height)
                    if cache_key not in tiled_hallway_cache:
                        segment_seed = hash(image_key)
                        tiled_hallway_cache[cache_key] = tile_multiple_images(
                            hallway_image, scaled_rect_width, scaled_rect_height, seed=segment_seed
                        )
                    screen.blit(tiled_hallway_cache[cache_key], (scaled_rect_x, scaled_rect_y))
                else:
                    scaled_hallway = pygame.transform.scale(hallway_image, (scaled_rect_width, scaled_rect_height))
                    screen.blit(scaled_hallway, (scaled_rect_x, scaled_rect_y))
                    
                # Draw decorations for this segment
                draw_decorations(screen, segment, scale_x, scale_y, camera_x, camera_y)
            
            # Handle portal animations
            portalTime += elapsed_ms
            if portalTime >= 500:
                portalTime = 0
                portalFrame = (portalFrame + 1) % len(entrancePortalAnimation)
                
            # Handle torch animations with randomized timing for less predictable flickering
            torchTime += elapsed_ms
            
            # Use random timing between 50-120ms for unpredictable flickering
            flicker_threshold = random.randint(50, 120)
            
            if torchTime >= flicker_threshold:
                torchTime = 0
                
                # Occasionally skip frames or go backward for more natural flickering
                if random.random() < 0.7:
                    # Normal forward animation 70% of the time
                    torchFrame = (torchFrame + 1) % len(torchAnimation)
                elif random.random() < 0.5:
                    # Jump to random frame 15% of the time
                    torchFrame = random.randint(0, len(torchAnimation) - 1)
                else:
                    # Backward animation 15% of the time
                    torchFrame = (torchFrame - 1) % len(torchAnimation)
                    
                # Update the torch in wall_decorations dictionary to the current frame
                wall_decorations["torch"] = torchAnimation[torchFrame]
            
            # Draw portals with enhanced visuals - different sizes for entrance vs internal
            if current_area == "entrance_hall":
                for door in doors:
                    door_x = door["x"] * scale_x - camera_x
                    door_y = door["y"] * scale_y - camera_y
                    # Pass is_entrance=True for entrance hall portals
                    draw_enhanced_portal(screen, door, door_x, door_y, scale_x, scale_y, camera_x, camera_y, is_entrance=True)
            
                    if portal_to_level2["visible"]:
                        door_x = portal_to_level2["x"] * scale_x - camera_x
                        door_y = portal_to_level2["y"] * scale_y - camera_y
                        draw_enhanced_portal(screen, portal_to_level2, door_x, door_y, scale_x, scale_y, camera_x, camera_y, is_entrance=True)

                
            elif current_area in area_transition_doors:
                door = area_transition_doors[current_area]
                door_x = door["x"] * scale_x - camera_x
                door_y = door["y"] * scale_y - camera_y
                # Internal portal (is_entrance=False is default)
                draw_enhanced_portal(screen, door, door_x, door_y, scale_x, scale_y, camera_x, camera_y)
            elif current_area in area_return_doors:
                door = area_return_doors[current_area]
                door_x = door["x"] * scale_x - camera_x
                door_y = door["y"] * scale_y - camera_y
                # Internal portal (is_entrance=False is default)
                draw_enhanced_portal(screen, door, door_x, door_y, scale_x, scale_y, camera_x, camera_y)
            
            # Update and draw movement trail effects        
            movement_effects = [effect for effect in movement_effects if effect.update()]
            for effect in movement_effects:
                effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
            
            # Update and draw particles
            particles = [p for p in particles if p.update()]
            for particle in particles:
                particle.draw(screen, scale_x, scale_y, camera_x, camera_y)
            
            # Draw teleport particles
            teleport_particles = [p for p in teleport_particles if p.update()]
            for particle in teleport_particles:
                particle.draw(screen, scale_x, scale_y, camera_x, camera_y)
                    
                    
            dt = clock.tick(60) / 1000  
            
            for enemy in all_enemies:
                screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))
                enemy.update(dt, player)
                
                
                if enemy.state == "attack" and player.check_collision(enemy):  
                    check_enemy_attacks(player, all_enemies)
                    player.take_damage(enemy.damage)  
                    print(f"Player hit by enemy attack! Player HP: {player.health}/{player.max_health}")
                
                if current_area == "right_path" and all(enemy.dead for enemy in all_enemies if isinstance(enemy, Boss1)):
                    if boss_defeat_count == 0:
                        boss_defeat_count += 1
                        print (boss_defeat_count, ": boss defeated")
                    boss1_defeated = True
                    portal_to_level2["visible"] = True
                    
                    if portal_to_level2 not in doors:  # Add portal to doors list if not already there
                        doors.append(portal_to_level2)
                    
            check_enemy_attacks(player, all_enemies)
            
            # Player update
            player.update()
        
            # With this:
            player_screen_x = player.x * scale_x - camera_x
            player_screen_y = player.y * scale_y - camera_y
            # Save original rect
            original_rect = player.rect.copy()
            # Set rect to screen position
            player.rect.midbottom = (player_screen_x, player_screen_y)
            # Draw the player
            player.draw(screen)
            # Restore original rect (important for collision detection)
            player.rect = original_rect
    
            
            # Draw UI elements
            draw_ui(screen)
            player.draw_main_health_bar(screen, 20, 40, 200, 20)
            player.draw_ultimate_bar(screen, 20, 65, 200, 10)
            
            
            # Check if player collides with the Level 2 portal
            if portal_to_level2["visible"] and boss_defeat_count > 0:
                if (portal_to_level2["x"] <= player.x <= portal_to_level2["x"] + portal_to_level2["width"] and 
                    portal_to_level2["y"] <= player.y <= portal_to_level2["y"] + portal_to_level2["height"]):
                    pygame.mixer.music.stop()
                    
                    # Save player state to a file or global variables
                    save_player_state(player)
                    
                    # Play teleport sound
                    teleport_start_sound.play()
                    
                    show_level_transition("Level 2")  
                    
                    # Exit lvl1 game loop
                    running = False
                    
                    # Load level2
                    import level2 
                    sys.exit()
            
            for i, spark in sorted(enumerate(sparks), reverse=True):
                spark.move(1)
                # Position is already in world coordinates, we just need to apply scaling and camera offset
                spark.draw(screen, camera_x, camera_y, scale_x, scale_y)
                if not spark.alive:
                    sparks.pop(i)                
                
        # If teleport is active, draw the space teleport effect over everything
        if teleport_active:
            screen.fill(BLACK)  # Clear screen for teleport effect
            draw_space_teleport(screen)
        
        # Update display and maintain framerate
        pygame.display.flip()
        clock.tick(60)
    else:
        show_game_over_screen()
        continue
    
    
# Cleanup and exit
pygame.quit()
sys.exit()