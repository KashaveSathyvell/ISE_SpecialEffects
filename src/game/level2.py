import pygame
import sys
import os
import random
import math

from enemy import Enemy, Golem, Boss2, load_mob_animations
from player import Character   
from powerups import Spark
from princess import Princess

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


# Create the player(x is center, y is bottom)
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

portal_victory = {"x": 4400, "y": 1800, "radius": 50}
victory_activated = False

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
    "western_wing": {"x": 175, "y": 450, "destination": "entrance_hall", "dest_x": 200, "dest_y": 450, "name": "Return to Entrance"},
    "central_pathways": {"x": 500, "y": 450, "destination": "entrance_hall", "dest_x": 400, "dest_y": 300, "name": "Return to Entrance"},
    "eastern_complex": {"x": 1600, "y": 350, "destination": "entrance_hall", "dest_x": 600, "dest_y": 300, "name": "Return to Entrance"},
    "boss_arena": {"x": 2400, "y": 2200, "destination": "entrance_hall", "dest_x": 500, "dest_y": 300, "name": "Emergency Exit"}
}

# The current area the player is in
current_area = "entrance_hall"

base_hallway = [
    #western_wing
    [100, 250, 900, 250, 400, "entrance_hall"],
    [175, 450, 175, 800, 150, "western_corridor"],
    [250, 800, -400, 800, 130, "treasure_approach"],
    [-225, 850, -225, 900, 120, "LavaJump_Western"],
    [-225, 900, -225, 1500, 120, "miniboss_approach"],
    [-685, 1400, -285, 1400, 200, "miniboss_chamber"],
    #central pathways
    [500, 450, 500, 1400, 130, "central_shaft"],
    [430, 1400, 1000, 1400, 130, "lower_connector"],
    [1000, 1000, 1000, 1900, 150, "room_entrance"],
    [850, 1850, 925, 1850, 100, "room_hallway"],
    [250, 1800, 850, 1800, 200, "central_mainRoom"],
    #eastern complex
    [1600, 350, 2400, 350, 200, "eastern_corridor"],
    [2325, 425, 2325, 800, 150, "eastern_down"],
    [2250, 870, 3400, 870, 140, "eastern_middle"],
    [3000, 800, 3000, 620, 150, "eastern_up_bottom"],
    [3000, 620, 3000, 470, 150, "eastern_up_transition"],
    [3000, 470, 3000, 240, 150, "eastern_up_top"],
    [2600, 150, 3400, 150, 400, "eastern_room"],
    #boss room
    [3000, 2275, 3500, 2275, 250, "princess_corridor"],
    [2200, 2200, 3000, 2200, 400, "boss_room"],
    [3500, 2325, 3800, 2325, 150, "escape_passage"],
    [3800, 2400, 3800, 1800, 150, "escape_vertical"],
    [3725, 1800, 4400, 1800, 200, "final_corridor"],
]

area_hallways = {
    "entrance_hall": ["entrance_hall"],
    "western_wing": ["western_corridor", "treasure_approach", "LavaJump_Western", "miniboss_approach", "miniboss_chamber"],
    "central_pathways": ["central_shaft", "lower_connector", "room_entrance", "room_hallway", "central_mainRoom"],
    "eastern_complex": ["eastern_corridor", "eastern_down", "eastern_middle", "eastern_up_bottom", "eastern_up_transition", "eastern_up_top", "eastern_room"],
    "Boss_room": ["boss_room", "princess_corridor", "escape_passage", "escape_vertical", "final_corridor"]
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

portal_glow_colors = [
    (80, 140, 255, 100),   # Blue glow
    (100, 150, 255, 80),   # Lighter blue
    (120, 160, 255, 60),   # Even lighter
    (140, 170, 255, 40),   # Almost white-blue
]


# Portal particles class for ambient portal effects
class PortalParticle:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
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
        self.distance += self.speed
        self.alpha -= 3
        if self.distance > self.max_distance or self.alpha <= 0:
            return False
        return True
        
    def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
        pos_x = self.x + math.cos(self.angle) * self.distance
        pos_y = self.y + math.sin(self.angle) * self.distance
        scaled_x = pos_x * scale_x - camera_x
        scaled_y = pos_y * scale_y - camera_y
        scaled_size = self.size * scale_x
        s = pygame.Surface((scaled_size * 2, scaled_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (scaled_size, scaled_size), scaled_size)
        screen.blit(s, (scaled_x - scaled_size, scaled_y - scaled_size))

# Teleportation particles for the teleport effect
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
        for j in range(5):
            radius = 400 - j*60 - i*20
            thickness = 20 - i*3
            pygame.draw.circle(img, color, (400, 250), radius, thickness)
        warp_images.append(img)

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
        
        # Play end sounda
        teleport_end_sound.play()
        
        #spawn enemy
        print("spawning enemies")
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


# Initialize space particles
def initialize_space_particles(count=150):
    global space_particles
    space_particles = []
    for _ in range(count):
        space_particles.append(SpaceParticle(SCREEN_WIDTH, SCREEN_HEIGHT))



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

is_teleporting = False


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
    player.x, player.y = 120, 425  # Move player back to starting position
    player.attacking = False
    player.using_ultimate = False
    player.shielding = False

    # Ensure animations are working properly
    player.action = "idle"  
    
    current_area = "entrance_hall"


all_enemies = pygame.sprite.Group()

enemy_positions = {
    "central_pathways": [("Mob1", (500, 900)), ("Mob2", (500, 700)), ("Mob3", (600, 1380)), ("Mob2", (1000, 1200)), ("Mob1", (1000, 1800)), ("Mob3", (900, 1850)), ("Golem", (500, 1900))],
    "western_wing": [("Mob2", (200, 600)), ("Mob3", (175, 600)), ("Mob3", (-200, 1000)), ("Golem", (-400, 1400)), ],
    "eastern_complex": [("Mob1", (1900, 400)), ("Mob1", (2325, 600)), ("Mob2", (2400, 850)), ("Mob3", (3000, 700)), ("Mob1", (2800, 340)), ("Mob2", (3000, 400)), ("Golem", (3200, 360))],
    "Boss_room": [("Boss2", (2500, 2200))]
}

def spawn_enemies_for_area(area):
    """Spawn enemies when entering a new area."""
    global all_enemies
    all_enemies.empty()
    print("Spawning enemies for area:", area)
    print("Enemy positions:", enemy_positions)

    if area in enemy_positions:
        for enemy_type, pos in enemy_positions[area]:
            if enemy_type == "Golem":
                enemy = Golem(pos[0], pos[1], is_in_hallway)
            elif enemy_type == "Boss2":  
                enemy = Boss2(pos[0], pos[1], is_in_hallway)
            else:
                animations = load_mob_animations(enemy_type)
                enemy = Enemy(pos[0], pos[1], animations, is_in_hallway)
            
            print("Spawning enemies")
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


def show_victory_screen():
    font = pygame.font.SysFont('Arial', 48)
    victory_text = font.render("Princess Rescued!!", True, (255, 255, 0))

    # Use the first frame of the princess' idle animation
    princess_img = princess.images[0]  # Adjust if needed
    player_img = player.current_image  # Assuming this is the correct player sprite

    # Scale images
    princess_scaled = pygame.transform.scale(princess_img, (100, 150))
    player_scaled = pygame.transform.scale(player_img, (400, 300))

    while True:
        screen.fill((0, 0, 0))  # Black background
        screen.blit(victory_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
        screen.blit(player_scaled, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))
        screen.blit(princess_scaled, (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def shake_screen():
    # Apply screen shake effect
    global camera_x, camera_y, shake_intensity, shake_duration
    
    if shake_duration > 0:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
        camera_x += offset_x
        camera_y += offset_y
        shake_duration -= 1
        return True
    return False

princess = Princess(3200, 2400)  # Adjust spawn position

sparks = []
shake_intensity = 0 
shake_duration = 0

initialize_space_particles(200) 

while running:
    if not player.dead:
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
        
        if not 'previous_area' in locals():
            previous_area = current_area
        
        if current_area in enemy_positions:
            all_enemies.update(clock.get_time())
    
    
        screen.fill(BLACK)
        
        if teleport_active:
            # Update the space teleport effect
            update_space_teleport(dt)
        
        else:
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
        elif current_area == "Boss_room" and not all(enemy.dead for enemy in all_enemies if isinstance(enemy, Boss2)):
            scaled_center_x = int(2600 * scale_x)
            scaled_center_y = int(2200 * scale_y)
            camera_x = scaled_center_x - (SCREEN_WIDTH // 2)
            camera_y = scaled_center_y - (SCREEN_HEIGHT // 2)
        else:
            camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
            camera_y = scaled_player_y - (SCREEN_HEIGHT // 2) 
        
        shake_applied = shake_screen()
        if shake_applied:
            print(f"Shake applied: remaining duration={shake_duration}")
        
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
    
        if previous_area != current_area:
            print(f"Area changed from {previous_area} to {current_area}")
            
        # Check if we're entering the boss room
        if current_area == "Boss_room" and previous_area != "Boss_room":
            print("Entering Boss room! Triggering shake!")
            shake_intensity = 20
            shake_duration = 40
        
        # Update previous_area for next frame
        previous_area = current_area
    
        
        if current_area == "Boss_room" and all(enemy.dead for enemy in all_enemies if isinstance(enemy, Boss2)):
            princess.following_player = True
        
        # Update and draw the princess in the appropriate areas
        if current_area == "Boss_room" or (current_area == "Boss_room" and princess.following_player):
            princess.update(player)
            princess.draw(screen, camera_x, camera_y)

        
        draw_ui(screen)
        player.draw_main_health_bar(screen, 20, 40, 200, 20)
        player.draw_ultimate_bar(screen, 20, 65, 200, 10)
        
        
        for i, spark in sorted(enumerate(sparks), reverse=True):
            spark.move(1)
            # Position is already in world coordinates, we just need to apply scaling and camera offset
            spark.draw(screen, camera_x, camera_y, scale_x, scale_y)
            if not spark.alive:
                sparks.pop(i)
    
        if is_teleporting:
            update_space_teleport(dt * 1000) 
            screen.fill((0, 0, 20))  # Dark background
            elapsed_time = pygame.time.get_ticks() - teleport_start_time
            
            # Scale warp image to current screen size
            warp_index = (elapsed_time // 150) % len(warp_images)
            scaled_warp = pygame.transform.scale(warp_images[warp_index], (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_warp, (0, 0))
            
            # Update and draw more space particles during longer teleport
            if len(space_particles) < 200 and random.random() < 0.1:
                space_particles.append(SpaceParticle(SCREEN_WIDTH, SCREEN_HEIGHT))
                
            for particle in space_particles:
                particle.update(16)
                particle.draw(screen)
        
            pygame.display.flip()
            continue  # Skip the rest of the loop
        
        if teleport_active:
            screen.fill(BLACK)  # Clear screen for teleport effect
            draw_space_teleport(screen)

        # Check if player is near victory portal
        if current_area == "Boss_room":
            player_image = player.current_image
            player_width = player_image.get_width()
            player_height = player_image.get_height()
            
            player_rect = pygame.Rect(player.x - player_width/2, player.y - player_height, player_width, player_height)
            portal_rect = pygame.Rect(portal_victory["x"] - 50, portal_victory["y"] - 50, 100, 100)
            
            if player_rect.colliderect(portal_rect):
                victory_activated = True


        if victory_activated:
            show_victory_screen()

        
        pygame.display.flip()
        clock.tick(60)
    
    else:
        show_game_over_screen()
        continue
            
pygame.quit()
sys.exit()


