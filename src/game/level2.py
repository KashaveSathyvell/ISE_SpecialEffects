import pygame
import sys
import os
import random

from enemy import Enemy, load_mob_animations
from enemy import Golem
from player import Character   # New import for the updated player

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

# --- New Player Setup ---
# Create the player using the Character class (x is center, y is bottom)
player = Character(120, 425, "Knight", 75)
player.speed = 5  # Set speed as desired

# Set frame counts so the animations load properly.
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
# Reload animations from the correct folder.
player.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{player.character_type}"))

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

# New area transition door (if needed)
area_transition_doors = {
    "lower_labyrinth": {
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

base_hallway = [
    [100, 250, 900, 250, 400, "entrance_hall"],
    [175, 450, 175, 800, 150, "western_corridor"],
    [250, 800, -400, 800, 130, "treasure_approach"],
    [-225, 850, -225, 900, 120, "LavaJump_Western"],
    [-225, 900, -225, 1500, 120, "miniboss_approach"],
    [-685, 1400, -285, 1400, 200, "miniboss_chamber"],
    [500, 450, 500, 1400, 130, "central_shaft"],
    [430, 1400, 1000, 1400, 130, "lower_connector"],
    [1000, 1000, 1000, 1900, 150, "room_entrance"],
    [850, 1850, 925, 1850, 100, "room_hallway"],
    [250, 1800, 850, 1800, 200, "central_mainRoom"],
    [1600, 350, 2400, 350, 200, "eastern_corridor"],
    [2325, 425, 2325, 800, 150, "eastern_down"],
    [2250, 870, 3400, 870, 140, "eastern_middle"],
    [3000, 800, 3000, 620, 150, "eastern_up_bottom"],
    [3000, 620, 3000, 470, 150, "eastern_up_transition"],
    [3000, 470, 3000, 240, 150, "eastern_up_top"],
    [2600, 150, 3400, 150, 400, "eastern_room"],
    [3000, 2275, 3500, 2275, 250, "princess_corridor"],
    [2200, 2200, 3000, 2200, 400, "boss_room"],
    [2650, 2300, 2750, 2300, 80, "boss_throne"],
    [3500, 2325, 3800, 2325, 150, "escape_passage"],
    [3800, 2400, 3800, 1800, 150, "escape_vertical"],
    [3725, 1800, 4400, 1800, 200, "final_corridor"],
]

area_hallways = {
    "entrance_hall": ["entrance_hall"],
    "western_wing": ["western_corridor", "treasure_approach", "LavaJump_Western", "miniboss_approach", "miniboss_chamber"],
    "central_pathways": ["central_shaft", "lower_connector", "room_entrance", "room_hallway", "central_mainRoom"],
    "eastern_complex": ["eastern_corridor", "eastern_down", "eastern_middle", "eastern_up_bottom", "eastern_up_transition", "eastern_up_top", "eastern_room"],
    "Boss_room": ["boss_room", "boss_throne", "princess_corridor", "escape_passage", "escape_vertical", "final_corridor"]
}

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
        
def load_animation_frames(base_filename, fileType, num_frames, scale=1.0):
    frames = []
    for i in range(num_frames):
        filename = f"{base_filename}{i+1}.{fileType}"
        img = load_image(filename, scale=scale)
        frames.append(img)
    return frames

class AnimatedObject:
    def __init__(self, x, y, frames, animation_speed=100, loop=True, start_frame=None):
        self.x = x
        self.y = y
        self.frames = frames
        self.current_frame = start_frame if start_frame is not None else random.randint(0, len(frames) - 1)
        self.animation_time = 0
        self.animation_speed = animation_speed  # milliseconds per frame
        self.loop = loop
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.active = False

    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        if not self.active or not self.frames:
            return
        frame = self.frames[self.current_frame]
        scaled_x = int(self.x * scale_x) - camera_x
        scaled_y = int(self.y * scale_y) - camera_y
        newWidth = int(frame.get_width() * scale_x)
        newHeight = int(frame.get_height() * scale_y)
        scaledImage = pygame.transform.scale(frame, (newWidth, newHeight))
        if (scaled_x < -frame.get_width() or scaled_x > SCREEN_WIDTH or 
            scaled_y < -frame.get_height() or scaled_y > SCREEN_HEIGHT):
            return
        screen.blit(scaledImage, (scaled_x, scaled_y))
        
class Objects:
    def __init__(self, x, y, image, area):
        self.x = x
        self.y = y
        self.image = image
        self.area = area
        
    def update(self, dt):
        pass
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        scaled_x = int(self.x * scale_x) - camera_x
        scaled_y = int(self.y * scale_y) - camera_y
        newWidth = int(self.image.get_width() * scale_x)
        newHeight = int(self.image.get_height() * scale_y)
        scaledImage = pygame.transform.scale(self.image, (newWidth, newHeight))
        screen.blit(scaledImage, (scaled_x, scaled_y))

def scale(img: pygame.Surface, factor):
    w, h = img.get_width() * factor, img.get_height() * factor
    return pygame.transform.scale(img, (int(w), int(h)))

SMOKE = pygame.image.load('src/assets/images/backgrounds/smoke.png').convert_alpha()

def randomPosition(segments):
    segment = random.choice(segments)
    start_x, start_y, end_x, end_y, width, _ = segment
    half_width = width / 2
    if start_y == end_y:
        x = random.uniform(min(start_x, end_x), max(start_x, end_x))
        y = random.uniform(start_y - half_width, start_y + half_width)
    else:
        y = random.uniform(min(start_y, end_y), max(start_y, end_y))
        x = random.uniform(start_x - half_width, start_x + half_width)
    return x, y

class SmokeParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale_k = 1
        self.img = scale(SMOKE, self.scale_k)
        self.target_alpha = 50
        self.alpha = 50
        self.alive = True
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(-0.1, 0.1)
        self.fade_out_rate = 0.05
        self.fading_out = False

    def update(self, dt):
        clamped_dt = min(dt, 50)
        self.x += self.vx * clamped_dt * 0.01
        self.y += self.vy * clamped_dt * 0.01
        if not is_in_hallway(self.x, self.y):
            self.fading_out = True
        if self.fading_out:
            self.alpha -= self.fade_out_rate * clamped_dt
            if self.alpha <= 0:
                self.alpha = 0
                self.alive = False
        self.img = scale(SMOKE, self.scale_k)
        self.img.set_alpha(int(self.alpha))

    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        scaled_x = int(self.x * scale_x) - camera_x
        scaled_y = int(self.y * scale_y) - camera_y
        scaled_img = pygame.transform.scale(
            self.img, 
            (int(self.img.get_width() * scale_x), int(self.img.get_height() * scale_y))
        )
        scaled_img.set_alpha(int(self.alpha))
        screen.blit(scaled_img, (scaled_x - scaled_img.get_width() // 2,
                                 scaled_y - scaled_img.get_height() // 2))

class Smoke:
    def __init__(self, area):
        self.area = area
        self.particles = []
        self.max_particles = 100
        self.hallway_segments = []
        for hallway_name in area_hallways.get(self.area, []):
            for segment in base_hallway:
                if segment[5] == hallway_name:
                    self.hallway_segments.append(segment)
        for i in range(self.max_particles):
            x, y = randomPosition(self.hallway_segments)
            self.particles.append(SmokeParticle(x, y))

    def update(self, dt):
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
        while len(self.particles) < self.max_particles:
            x, y = randomPosition(self.hallway_segments)
            self.particles.append(SmokeParticle(x, y))

    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        for particle in self.particles:
            particle.draw(screen, scale_x, scale_y, camera_x, camera_y)

smoke = Smoke(area = "central_pathways")

def tile_multiple_images(image_list, target_width, target_height, seed=None):
    fixed_tile_w, fixed_tile_h = image_list[0].get_size()
    processed_images = []
    for img in image_list:
        img_w, img_h = img.get_size()
        if img_w != fixed_tile_w or img_h != fixed_tile_h:
            if img_w >= fixed_tile_w and img_h >= fixed_tile_h:
                cropped = img.subsurface((0, 0, fixed_tile_w, fixed_tile_h)).copy()
                processed_images.append(cropped)
            else:
                scaled = pygame.transform.scale(img, (fixed_tile_w, fixed_tile_h))
                processed_images.append(scaled)
        else:
            processed_images.append(img)
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

def create_transition_tile(top_img, bottom_img, blend_height):
    width = min(top_img.get_width(), bottom_img.get_width())
    if top_img.get_height() < blend_height:
        top_img = pygame.transform.scale(top_img, (width, blend_height))
    if bottom_img.get_height() < blend_height:
        bottom_img = pygame.transform.scale(bottom_img, (width, blend_height))
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

hallway_images = {
    "entrance_hall": load_image("backgrounds/Level2Background.jpg"),
    "western_corridor": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "treasure_approach": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "LavaJump_Western": [load_image("backgrounds/Lava.png", scale=0.5)],
    "miniboss_approach": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "miniboss_chamber": [load_image("backgrounds/LavaFloorRock1.png", scale=0.5)],
    "central_shaft": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "lower_connector": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "room_entrance": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "room_hallway": [load_image("backgrounds/lvl2_CrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_CrystalCaveFloor1.jpg")],
    "central_mainRoom": load_image("backgrounds/MysticalCave.jpg"),
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
    "princess_corridor": load_image("backgrounds/lvl2_PrincessCage.jpg"),
    "boss_room": load_image("backgrounds/lvl2_BossMain.jpg"),
    "boss_throne": [pygame.Surface((32, 32), pygame.SRCALPHA).fill((114, 104, 162))],
    "escape_passage": [load_image("backgrounds/lvl2_BossCrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_BossCrystalCaveFloor1.jpg")],
    "escape_vertical": [load_image("backgrounds/lvl2_BossCrystalCaveFloor.jpg"), load_image("backgrounds/lvl2_BossCrystalCaveFloor1.jpg")],
    "final_corridor": load_image("backgrounds/lvl2_BossCrystalCave.jpg"),
}
default_hallway_img = [pygame.Surface((32, 32), pygame.SRCALPHA).fill((48, 52, 109))]

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

def is_near_door():
    threshold = 30
    if current_area == "entrance_hall":
        for door in doors:
            door_center_x = door["x"] + door["width"] / 2
            door_center_y = door["y"] + door["height"] / 2
            distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
            if distance < threshold:
                return door
    if current_area in area_transition_doors:
        door = area_transition_doors[current_area]
        door_center_x = door["x"] + door["width"] / 2
        door_center_y = door["y"] + door["height"] / 2
        distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
        if distance < threshold:
            return door
    if current_area in area_return_doors:
        door = area_return_doors[current_area]
        door_center_x = door["x"] + door.get("width", 0) / 2
        door_center_y = door["y"] + door.get("height", 0) / 2
        distance = ((player.x - door_center_x) ** 2 + (player.y - door_center_y) ** 2) ** 0.5
        if distance < threshold:
            return door
    return None

def teleport_player(destination, dest_x, dest_y):
    global current_area
    current_area = destination
    player.x = dest_x
    player.y = dest_y
    spawn_enemies_for_area(current_area)
    for i in range(5):
        movement_effects.append(MovementEffect(player.x, player.y))

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

lava_bubble_frames = load_animation_frames("backgrounds/Magma/MagmaBubbling", "png", 11, scale=0.5)

animated_objects = []
Entrance_lava_positions = [
    (150, 340),
    (350, 320),
    (400, 340),
    (530, 330),
    (710, 320)
]
for pos in Entrance_lava_positions:
    animated_objects.append(AnimatedObject(
        pos[0],
        pos[1],
        lava_bubble_frames,
        animation_speed=random.randint(200, 400),
        loop=True
    ))

west_animated_objects = []
Western_lava_positions = [(-225, 850)]
for pos in Western_lava_positions:
    west_animated_objects.append(AnimatedObject(
        pos[0],
        pos[1],
        lava_bubble_frames,
        animation_speed=random.randint(200, 400),
        loop=True
    ))

GameObjects = []
objects = [
    {"x": -320, "y": 750, "image_file": "backgrounds/LavaPillar.png", "scale": 0.5, "area": "western_wing"},
    {"x": -520, "y": 1350, "image_file": "backgrounds/MiniVolcano.png", "scale": 0.4, "area": "western_wing"},
    {"x": 80, "y": 700, "image_file": "backgrounds/LavaRock1.png", "scale": 0.7, "area": "western_wing"},
    {"x": -290, "y": 1200, "image_file": "backgrounds/LavaRock2.png", "scale": 0.8, "area": "western_wing"},
]
for obj in objects:
    obj = Objects(obj["x"], obj["y"], load_image(obj["image_file"], scale=obj["scale"]), obj["area"])
    GameObjects.append(obj)

clock = pygame.time.Clock()
movement_effects = []
step_counter = 0
running = True

tiled_hallway_cache = {}

fade_alpha = 0
is_fading = False
fade_in = False
fade_speed = 15
destination_info = None

all_enemies = pygame.sprite.Group()

enemy_positions = {
    "central_pathways": [("Mob1", (150, 500)), ("Mob2", (-200, 800))],
    "western_wing": [("Mob2", (200, 600)), ("Mob3", (-300, 1000)), ("Golem", (-400, 1400))],
    "boss_room": [("Mob3", (2500, 2200)), ("Mob1", (2800, 2300))]
}

def spawn_enemies_for_area(area):
    global all_enemies
    all_enemies.empty()
    if area in enemy_positions:
        for enemy_type, pos in enemy_positions[area]:
            if enemy_type == "Golem":
                # Special handling for Golem
                enemy = Golem(pos[0], pos[1], is_in_hallway)
                all_enemies.add(enemy)
                print(f"Added Golem at position {pos}, rect: {enemy.rect}")
            else:
                # Regular enemy handling
                animations = load_mob_animations(enemy_type)
                enemy = Enemy(pos[0], pos[1], animations, is_in_hallway)
                all_enemies.add(enemy)
                print(f"Added Mob at position {pos}, rect: {enemy.rect}")


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
                print(f"Player hit! Damage: {damage}, Player health: {player.health}")



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
            #Player Controls
            if event.key == pygame.K_f:
                player.toggle_shield()
            if event.key == pygame.K_q:                
                player.attack(all_enemies)
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_x:
                player.use_ultimate(all_enemies)

    if current_area in enemy_positions:
        all_enemies.update(clock.get_time())

    screen.fill(BLACK)

    scale_x = SCREEN_WIDTH / BASE_WIDTH
    scale_y = SCREEN_HEIGHT / BASE_HEIGHT
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

    player.update()

    scaled_player_x = int(player.x * scale_x)
    scaled_player_y = int(player.y * scale_y)
    
    
    if current_area == "entrance_hall":
        camera_x = (BASE_WIDTH // 2) - (SCREEN_WIDTH // 2) +100 # Fixed center x
        camera_y = (BASE_HEIGHT // 2) - (SCREEN_HEIGHT // 2)  # Fixed center y
    else:
        camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
        camera_y = scaled_player_y - (SCREEN_HEIGHT // 2)
    
    
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

    dt = clock.tick(60) / 1000  
    
    for enemy in all_enemies:
        screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))
        enemy.draw_healthbar(screen)
        enemy.update(dt, player)
        if enemy.state == "attack" and player.check_collision(enemy):  
            check_enemy_attacks(player, all_enemies)
            player.take_damage(enemy.damage)  
            print(f"Player hit by enemy attack! Player HP: {player.health}/{player.max_health}")
            
    check_enemy_attacks(player, all_enemies)
            
    for obj in GameObjects:
        if obj.area == current_area:
            obj.update(clock.get_time())
            obj.draw(screen, scale_x, scale_y, camera_x, camera_y)

    portalTime += clock.get_time()
    if portalTime >= 500:
        portalTime = 0
        portalFrame = (portalFrame + 1) % len(portalAnimation)
    if current_area == "entrance_hall":
        for door in doors:
            door_x = door["x"] * scale_x - camera_x
            door_y = door["y"] * scale_y - camera_y
            screen.blit(portalAnimation[portalFrame], (door_x - 15, door_y - 30))
        for obj in animated_objects:
            obj.update(clock.get_time())
            obj.draw(screen, scale_x, scale_y, camera_x, camera_y)
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
    if current_area == "western_wing":
        for obj in west_animated_objects:
            obj.update(clock.get_time())
            obj.draw(screen, scale_x, scale_y, camera_x, camera_y)
    if current_area == "central_pathways":
        smoke.update(clock.get_time())
        smoke.draw(screen, scale_x, scale_y, camera_x, camera_y)
    movement_effects = [effect for effect in movement_effects if effect.update()]
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)

   
    # Calculate drawing position based on player's (x, y) where y is bottom.
    image = player.current_image
    scaled_image = pygame.transform.scale(image, (int(image.get_width()*scale_x), int(image.get_height()*scale_y)))
    draw_x = int(player.x * scale_x) - camera_x - scaled_image.get_width() // 2
    draw_y = int(player.y * scale_y) - camera_y - scaled_image.get_height()
    if player.hit_effect and not player.hit_visible:
        mask_outline = player.current_mask.to_surface(setcolor=(255, 255, 255, 220), unsetcolor=(0, 0, 0, 0))
        scaled_mask = pygame.transform.scale(mask_outline, (int(mask_outline.get_width()*scale_x), int(mask_outline.get_height()*scale_y)))
        screen.blit(scaled_mask, (draw_x, draw_y))
    else:
        screen.blit(scaled_image, (draw_x, draw_y))

    draw_ui(screen)
    player.draw_main_health_bar(screen, 20, 40, 200, 20)
    player.draw_ultimate_bar(screen, 20, 65, 200, 10)

    if is_fading:
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
