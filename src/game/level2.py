# import pygame
# import sys
# import os

# # Initialize Pygame
# pygame.init()

# # Base resolution (game logic uses these coordinates)
# BASE_WIDTH = 800
# BASE_HEIGHT = 500

# # Current screen resolution (starts at base resolution)
# SCREEN_WIDTH = BASE_WIDTH
# SCREEN_HEIGHT = BASE_HEIGHT
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
# pygame.display.set_caption("Dungeon Hallway")

# # Colors
# GREEN = (32, 96, 32)
# BLACK = (13, 27, 10)
# WHITE = (255, 255, 255)
# PLAYER_COLOR = (74, 128, 245)

# # Player settings (in base coordinates)
# player_pos = [120, 250]  # Starting position
# player_radius = 10
# player_speed = 3

# base_hallway = [
#     # === ENTRANCE ZONE ===
#     # Grand entrance to level 2 with wider corridors
#     [100, 250, 900, 250, 400],  # Significantly longer entrance hallway
    
#     # === WESTERN WING ===
#     # Western corridor with narrowing path (trap area)
#     [100, 250, 100, 800, 150],  # Extended vertical western corridor
#     # Western treasure room access
#     [100, 800, 400, 800, 100],  # Longer approach to treasure
#     # Mini-boss chamber approach
#     [400, 800, 400, 1200, 120],  # Longer corridor to mini-boss
#     # Mini-boss circular chamber (coordinates form entrance)
#     [200, 1200, 600, 1200, 200],  # Larger mini-boss chamber
    
#     # === CENTRAL PATHWAYS ===
#     # Main hallway from entrance becoming narrower
#     [900, 250, 1600, 250, 180],  # Much longer main hallway
#     # Central vertical shaft with obstacles
#     [500, 250, 500, 1400, 130],  # Extended vertical central shaft
#     # Lower central horizontal connector
#     [500, 1400, 1000, 1400, 130],  # Longer lower connector
#     # Water room entrance corridor
#     [1000, 1400, 1000, 1800, 150],  # Extended approach to water room
#     # Water room west side
#     [700, 1800, 1000, 1800, 200],  # Wider water room
#     # Water room east side
#     [1000, 1800, 1300, 1800, 200],  # Wider water room
    
#     # === EASTERN COMPLEX ===
#     # Upper eastern corridor (guarded)
#     [1600, 250, 2400, 250, 160],  # Much longer eastern corridor
#     # Eastern vertical descent
#     [2400, 250, 2400, 900, 140],  # Longer vertical descent
#     # Eastern middle chamber approach
#     [2000, 900, 2400, 900, 140],  # Longer approach
#     # Eastern lower chamber 
#     [2400, 900, 2800, 900, 180],  # Extended lower chamber
#     # Secret passage entrance (hidden - narrower)
#     [2800, 900, 3200, 900, 80],  # Longer secret passage
#     # Secret passage turn
#     [3200, 900, 3200, 600, 80],  # Extended vertical secret passage
#     # Secret passage to treasure
#     [3200, 600, 3600, 600, 80],  # Longer passage to treasure
    
#     # === PRINCESS TOWER PATH ===
#     # Princess tower approach
#     [2400, 250, 2400, -200, 120],  # Longer approach to princess tower
#     # Princess chamber
#     [2300, -200, 2500, -200, 160],  # Princess chamber slightly larger
    
#     # === LOWER LABYRINTH ===
#     # Branching path to labyrinth
#     [900, 250, 900, 950, 150],  # Longer branch to labyrinth
#     # Labyrinth upper corridor
#     [900, 950, 1700, 950, 120],  # Much longer labyrinth corridor
#     # Labyrinth vertical corridor 1
#     [1200, 950, 1200, 1250, 120],  # Extended vertical segment
#     # Labyrinth vertical corridor 2
#     [1700, 950, 1700, 1400, 120],  # Longer vertical corridor
#     # Labyrinth lower connector
#     [1200, 1250, 1700, 1250, 120],  # Longer connector
#     # Trap room entrance
#     [1700, 1250, 2000, 1250, 100],  # Extended trap room entrance
    
#     # === ADDITIONAL MAZE-LIKE PATHS ===
#     # Extra maze section 1
#     [1200, 1250, 1200, 1600, 120],  # New vertical section
#     # Extra maze section 2 
#     [1200, 1600, 1700, 1600, 120],  # New horizontal section
#     # Extra maze section 3
#     [1700, 1600, 1700, 1900, 120],  # New vertical section
#     # Extra maze connection
#     [1400, 1250, 1400, 1600, 100],  # Connector between maze sections
    
#     # === BOSS ARENA ACCESS ===
#     # Pre-boss corridor 1
#     [1700, 1400, 2200, 1400, 180],  # Extended approach
#     # Pre-boss corridor 2 
#     [2200, 1400, 2200, 1900, 180],  # Longer descent to boss
#     # Boss arena approach corridor
#     [2200, 1900, 2600, 1900, 200],  # Final lengthy approach to boss
#     # Boss arena entrance (widens significantly)
#     [2600, 1900, 2600, 2200, 250],  # Extended entrance to boss arena
    
#     # === BOSS ARENA ===
#     # Boss arena west wall
#     [2400, 2200, 2600, 2200, 350],  # Widened boss arena
#     # Boss arena east wall
#     [2600, 2200, 2800, 2200, 350],  # Widened boss arena
#     # Boss arena south wall
#     [2600, 2400, 2600, 2200, 350],  # Deepened boss arena
#     # Boss throne area (small platform within arena)
#     [2650, 2300, 2750, 2300, 80],  # Boss position
    
#     # === ESCAPE ROUTE ===
#     # Post-boss secret passage (revealed after boss defeat)
#     [2800, 2200, 3200, 2200, 150],  # Longer escape route
#     # Escape route vertical path
#     [3200, 2200, 3200, 1400, 150],  # Extended vertical escape
#     # Final corridor to freedom
#     [3200, 1400, 3800, 1400, 200],  # Much longer final corridor
# ]


# # Special room markers (used to place enemies, treasures, etc.)
# special_rooms = {
#     # [x, y, width, height, type]
#     "mini_boss": [200, 1150, 400, 200, "combat"],
#     "water_puzzle": [700, 1750, 600, 200, "puzzle"],
#     "treasure_room": [3400, 550, 300, 200, "treasure"],
#     "princess_chamber": [2250, -250, 350, 200, "rescue"],
#     "trap_room": [1800, 1200, 300, 200, "traps"],
#     "boss_arena": [2400, 2200, 400, 350, "boss_fight"],
#     "secret_cache": [1400, 1500, 150, 150, "hidden_treasure"],
#     "ambush_point": [1500, 250, 200, 180, "combat"],
#     "poison_corridor": [900, 600, 150, 350, "hazard"],
#     "healing_shrine": [2100, 900, 150, 150, "healing"],
#     "weapon_upgrade": [800, 1250, 150, 150, "upgrade"],
# }

# def load_image(filename, scale=1.0):
#     try:
#         image = pygame.image.load(os.path.join('src', 'assets', 'images', 'backgrounds', filename))
#         if scale != 1.0:
#             new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
#             image = pygame.transform.scale(image, new_size)
#         return image
#     except pygame.error as e:
#         print(f"Error loading image {filename}: {e}")
#         # Create a purple/black checkered surface as a placeholder
#         surf = pygame.Surface((64, 64))
#         surf.fill((100, 0, 100))
#         pygame.draw.rect(surf, (0, 0, 0), (0, 0, 32, 32))
#         pygame.draw.rect(surf, (0, 0, 0), (32, 32, 32, 32))
#         return surf

# # Load tileset images (add after pygame init)
# floor_img = load_image("Level2Background.jpg")
# wall_img = load_image("Level2Background.jpg")



# # Movement effects (stored in base coordinates)
# class MovementEffect:
#     def __init__(self, pos_x, pos_y):
#         self.pos = [pos_x, pos_y]
#         self.radius = 3  # base radius
#         self.alpha = 200  # starting opacity
#         self.color = (100, 150, 255, self.alpha)
    
#     def update(self):
#         self.radius += 0.5
#         self.alpha -= 10
#         self.color = (100, 150, 255, self.alpha)
#         return self.alpha > 0
        
#     def draw(self, screen, scale_x, scale_y, camera_x, camera_y):
#         scaled_radius = int(self.radius * scale_x)
#         scaled_pos = (int(self.pos[0] * scale_x) - camera_x, int(self.pos[1] * scale_y) - camera_y)
#         s = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
#         pygame.draw.circle(s, self.color, (scaled_radius, scaled_radius), scaled_radius)
#         screen.blit(s, (scaled_pos[0] - scaled_radius, scaled_pos[1] - scaled_radius))

# def is_in_hallway(pos_x, pos_y):
#     """ Check if a position is inside the hallway. """
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
#         if start_y == end_y:  # Horizontal segment
#             if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and (start_y - half_width) <= pos_y <= (start_y + half_width):
#                 return True
#         elif start_x == end_x:  # Vertical segment
#             if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and (start_x - half_width) <= pos_x <= (start_x + half_width):
#                 return True
#     return False


# def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
#     """ Draw the hallway by filling each segment's entire rectangle with a floor image. """
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
        
#         # Calculate the rectangle for this hallway segment in base coordinates
#         if start_y == end_y:  # Horizontal segment
#             rect_x = min(start_x, end_x)
#             rect_y = start_y - half_width
#             rect_width = abs(end_x - start_x)
#             rect_height = width
#         else:  # Vertical segment
#             rect_x = start_x - half_width
#             rect_y = min(start_y, end_y)
#             rect_width = width
#             rect_height = abs(end_y - start_y)
        
#         # Convert the rectangle to screen coordinates using scale and camera offset
#         scaled_rect_x = rect_x * scale_x - camera_x
#         scaled_rect_y = rect_y * scale_y - camera_y
#         scaled_rect_width = rect_width * scale_x
#         scaled_rect_height = rect_height * scale_y
        
#         # Scale the floor image to fill the entire rectangle
#         scaled_floor = pygame.transform.scale(
#             floor_img,
#             (int(scaled_rect_width), int(scaled_rect_height))
#         )
#         screen.blit(scaled_floor, (scaled_rect_x, scaled_rect_y))
        
#         # Optionally, you can still draw walls around the edges if desired.
#         wall_thickness = 8  # in base coordinates
#         # For horizontal segments: draw top and bottom walls
#         if start_y == end_y:
#             # Top wall
#             top_wall = pygame.transform.scale(
#                 wall_img,
#                 (int(scaled_rect_width), int(wall_thickness * scale_y))
#             )
#             screen.blit(top_wall, (scaled_rect_x, scaled_rect_y))
#             # Bottom wall
#             bottom_wall = pygame.transform.scale(
#                 wall_img,
#                 (int(scaled_rect_width), int(wall_thickness * scale_y))
#             )
#             screen.blit(bottom_wall, (scaled_rect_x, scaled_rect_y + scaled_rect_height - wall_thickness * scale_y))
#         else:
#             # For vertical segments: draw left and right walls
#             left_wall = pygame.transform.scale(
#                 wall_img,
#                 (int(wall_thickness * scale_x), int(scaled_rect_height))
#             )
#             screen.blit(left_wall, (scaled_rect_x, scaled_rect_y))
#             right_wall = pygame.transform.scale(
#                 wall_img,
#                 (int(wall_thickness * scale_x), int(scaled_rect_height))
#             )
#             screen.blit(right_wall, (scaled_rect_x + scaled_rect_width - wall_thickness * scale_x, scaled_rect_y))


# clock = pygame.time.Clock()
# movement_effects = []
# step_counter = 0
# running = True

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.VIDEORESIZE:
#             SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
#             screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
#     scale_x = SCREEN_WIDTH / BASE_WIDTH
#     scale_y = SCREEN_HEIGHT / BASE_HEIGHT
    
#     keys = pygame.key.get_pressed()
#     original_pos = player_pos.copy()
    
#     if keys[pygame.K_LEFT]:
#         player_pos[0] -= player_speed
#     if keys[pygame.K_RIGHT]:
#         player_pos[0] += player_speed
#     if keys[pygame.K_UP]:
#         player_pos[1] -= player_speed
#     if keys[pygame.K_DOWN]:
#         player_pos[1] += player_speed
    
#     # Collision checking against the base hallway coordinates
#     if not is_in_hallway(player_pos[0], player_pos[1]):
#         player_pos = original_pos
#     else:
#         step_counter += 1
#         if step_counter % 10 == 0:
#             movement_effects.append(MovementEffect(player_pos[0], player_pos[1]))
    
#     # First scale the player position
#     scaled_player_x = int(player_pos[0] * scale_x)
#     scaled_player_y = int(player_pos[1] * scale_y)
    
#     # Calculate camera position to center the player
#     camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
#     camera_y = scaled_player_y - (SCREEN_HEIGHT // 2)
    
#     # Update movement effects and remove faded ones
#     movement_effects = [effect for effect in movement_effects if effect.update()]
    
#     screen.fill(BLACK)
    
#     # Draw the hallway, movement effects, and player using scaled coordinates
#     draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
#     for effect in movement_effects:
#         effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
#     # Draw player at the center of the screen
#     pygame.draw.circle(screen, PLAYER_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x))
#     pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x), 2)
    
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
# sys.exit()



import pygame
import sys
import os

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
    # === ENTRANCE ZONE ===
    # Grand entrance to level 2 with wider corridors
    [100, 250, 900, 250, 400, "entrance_hall"],  
    
    # === WESTERN WING ===
    # Western corridor with narrowing path (trap area)
    [100, 250, 100, 800, 150, "western_corridor"],  
    # Western treasure room access
    [100, 800, 400, 800, 100, "treasure_approach"],  
    # Mini-boss chamber approach
    [400, 800, 400, 1200, 120, "miniboss_approach"],  
    # Mini-boss circular chamber (coordinates form entrance)
    [200, 1200, 600, 1200, 200, "miniboss_chamber"],  
    
    # === CENTRAL PATHWAYS ===
    # Main hallway from entrance becoming narrower
    [900, 250, 1600, 250, 180, "main_hallway"],  
    # Central vertical shaft with obstacles
    [500, 250, 500, 1400, 130, "central_shaft"],  
    # Lower central horizontal connector
    [500, 1400, 1000, 1400, 130, "lower_connector"],  
    # Water room entrance corridor
    [1000, 1400, 1000, 1800, 150, "water_entrance"],  
    # Water room west side
    [700, 1800, 1000, 1800, 200, "water_room_west"],  
    # Water room east side
    [1000, 1800, 1300, 1800, 200, "water_room_east"],  
    
    # === EASTERN COMPLEX ===
    # Upper eastern corridor (guarded)
    [1600, 250, 2400, 250, 160, "eastern_corridor"],  
    # Eastern vertical descent
    [2400, 250, 2400, 900, 140, "eastern_descent"],  
    # Eastern middle chamber approach
    [2000, 900, 2400, 900, 140, "middle_approach"],  
    # Eastern lower chamber 
    [2400, 900, 2800, 900, 180, "lower_chamber"],  
    # Secret passage entrance (hidden - narrower)
    [2800, 900, 3200, 900, 80, "secret_passage"],  
    # Secret passage turn
    [3200, 900, 3200, 600, 80, "secret_turn"],  
    # Secret passage to treasure
    [3200, 600, 3600, 600, 80, "secret_treasure"],  
    
    # === PRINCESS TOWER PATH ===
    # Princess tower approach
    [2400, 250, 2400, -200, 120, "princess_approach"],  
    # Princess chamber
    [2300, -200, 2500, -200, 160, "princess_chamber"],  
    
    # === LOWER LABYRINTH ===
    # Branching path to labyrinth
    [900, 250, 900, 950, 150, "labyrinth_branch"],  
    # Labyrinth upper corridor
    [900, 950, 1700, 950, 120, "labyrinth_upper"],  
    # Labyrinth vertical corridor 1
    [1200, 950, 1200, 1250, 120, "labyrinth_vert1"],  
    # Labyrinth vertical corridor 2
    [1700, 950, 1700, 1400, 120, "labyrinth_vert2"],  
    # Labyrinth lower connector
    [1200, 1250, 1700, 1250, 120, "labyrinth_lower"],  
    # Trap room entrance
    [1700, 1250, 2000, 1250, 100, "trap_entrance"],  
    
    # === ADDITIONAL MAZE-LIKE PATHS ===
    # Extra maze section 1
    [1200, 1250, 1200, 1600, 120, "maze_section1"],  
    # Extra maze section 2 
    [1200, 1600, 1700, 1600, 120, "maze_section2"],  
    # Extra maze section 3
    [1700, 1600, 1700, 1900, 120, "maze_section3"],  
    # Extra maze connection
    [1400, 1250, 1400, 1600, 100, "maze_connection"],  
    
    # === BOSS ARENA ACCESS ===
    # Pre-boss corridor 1
    [1700, 1400, 2200, 1400, 180, "preboss_corridor1"],  
    # Pre-boss corridor 2 
    [2200, 1400, 2200, 1900, 180, "preboss_corridor2"],  
    # Boss arena approach corridor
    [2200, 1900, 2600, 1900, 200, "boss_approach"],  
    # Boss arena entrance (widens significantly)
    [2600, 1900, 2600, 2200, 250, "boss_entrance"],  
    
    # === BOSS ARENA ===
    # Boss arena west wall
    [2400, 2200, 2600, 2200, 350, "boss_arena_west"],  
    # Boss arena east wall
    [2600, 2200, 2800, 2200, 350, "boss_arena_east"],  
    # Boss arena south wall
    [2600, 2400, 2600, 2200, 350, "boss_arena_south"],  
    # Boss throne area (small platform within arena)
    [2650, 2300, 2750, 2300, 80, "boss_throne"],  
    
    # === ESCAPE ROUTE ===
    # Post-boss secret passage (revealed after boss defeat)
    [2800, 2200, 3200, 2200, 150, "escape_passage"],  
    # Escape route vertical path
    [3200, 2200, 3200, 1400, 150, "escape_vertical"],  
    # Final corridor to freedom
    [3200, 1400, 3800, 1400, 200, "final_corridor"],  
]

# Special room markers (used to place enemies, treasures, etc.)
special_rooms = {
    # [x, y, width, height, type]
    "mini_boss": [200, 1150, 400, 200, "combat"],
    "water_puzzle": [700, 1750, 600, 200, "puzzle"],
    "treasure_room": [3400, 550, 300, 200, "treasure"],
    "princess_chamber": [2250, -250, 350, 200, "rescue"],
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
        # Create a purple/black checkered surface as a placeholder
        surf = pygame.Surface((64, 64))
        surf.fill((100, 0, 100))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, 32, 32))
        pygame.draw.rect(surf, (0, 0, 0), (32, 32, 32, 32))
        return surf

# Define default image for fallback
lavaCave_Entrance = load_image("Level2Background.jpg")
default_hallway_img = load_image("lvl2_CrystalCave.jpg")

# Dictionary to store hallway images by key
hallway_images = {
    # Load all unique hallway images 
    # Using the default image for all segments for now
    # You can replace these with your actual unique images
    "entrance_hall": lavaCave_Entrance,
    "western_corridor": default_hallway_img,
    "treasure_approach": default_hallway_img,
    "miniboss_approach": load_image("lvl2_MiniBossBG.jpg"),
    "miniboss_chamber": load_image("lvl2_MiniBoss2.jpg"),
    "main_hallway": default_hallway_img,
    "central_shaft": default_hallway_img,
    "lower_connector": default_hallway_img,
    "water_entrance": default_hallway_img,
    "water_room_west": default_hallway_img,
    "water_room_east": default_hallway_img,
    "eastern_corridor": default_hallway_img,
    "eastern_descent": default_hallway_img,
    "middle_approach": default_hallway_img,
    "lower_chamber": default_hallway_img,
    "secret_passage": default_hallway_img,
    "secret_turn": default_hallway_img,
    "secret_treasure": default_hallway_img,
    "princess_approach": default_hallway_img,
    "princess_chamber": load_image("lvl2_PrincessCage.jpg"),
    "labyrinth_branch": default_hallway_img,
    "labyrinth_upper": default_hallway_img,
    "labyrinth_vert1": default_hallway_img,
    "labyrinth_vert2": default_hallway_img,
    "labyrinth_lower": default_hallway_img,
    "trap_entrance": default_hallway_img,
    "maze_section1": default_hallway_img,
    "maze_section2": default_hallway_img,
    "maze_section3": default_hallway_img,
    "maze_connection": default_hallway_img,
    "preboss_corridor1": default_hallway_img,
    "preboss_corridor2": default_hallway_img,
    "boss_approach": default_hallway_img,
    "boss_entrance": load_image("lvl2_BossEntrance.jpg"),
    "boss_arena_west": default_hallway_img,
    "boss_arena_east": default_hallway_img,
    "boss_arena_south": default_hallway_img,
    "boss_throne": default_hallway_img,
    "escape_passage": default_hallway_img,
    "escape_vertical": default_hallway_img,
    "final_corridor": default_hallway_img,
}

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
        scaled_radius = int(self.radius * scale_x)
        scaled_pos = (int(self.pos[0] * scale_x) - camera_x, int(self.pos[1] * scale_y) - camera_y)
        s = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (scaled_radius, scaled_radius), scaled_radius)
        screen.blit(s, (scaled_pos[0] - scaled_radius, scaled_pos[1] - scaled_radius))

def is_in_hallway(pos_x, pos_y):
    """ Check if a position is inside the hallway. """
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, _ = segment  # Added _ to ignore image_key
        half_width = width / 2
        if start_y == end_y:  # Horizontal segment
            if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and (start_y - half_width) <= pos_y <= (start_y + half_width):
                return True
        elif start_x == end_x:  # Vertical segment
            if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and (start_x - half_width) <= pos_x <= (start_x + half_width):
                return True
    return False

def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
    """ Draw the hallway using unique images for each segment. """
    for segment in base_hallway:
        start_x, start_y, end_x, end_y, width, image_key = segment
        half_width = width / 2
        
        # Get the image for this hallway segment
        hallway_image = hallway_images.get(image_key, default_hallway_img)
        
        # Calculate the rectangle for this hallway segment in base coordinates
        if start_y == end_y:  # Horizontal segment
            rect_x = min(start_x, end_x)
            rect_y = start_y - half_width
            rect_width = abs(end_x - start_x)
            rect_height = width
        else:  # Vertical segment
            rect_x = start_x - half_width
            rect_y = min(start_y, end_y)
            rect_width = width
            rect_height = abs(end_y - start_y)
        
        # Convert the rectangle to screen coordinates using scale and camera offset
        scaled_rect_x = rect_x * scale_x - camera_x
        scaled_rect_y = rect_y * scale_y - camera_y
        scaled_rect_width = rect_width * scale_x
        scaled_rect_height = rect_height * scale_y
        
        # Scale the hallway image to fill the entire rectangle
        scaled_hallway = pygame.transform.scale(
            hallway_image,
            (int(scaled_rect_width), int(scaled_rect_height))
        )
        screen.blit(scaled_hallway, (scaled_rect_x, scaled_rect_y))
        
        # Optional: Draw wall edges for clarity
        wall_thickness = 8  # in base coordinates
        if start_y == end_y:  # Horizontal segment
            # Top wall edge
            pygame.draw.line(
                screen, 
                WHITE, 
                (scaled_rect_x, scaled_rect_y), 
                (scaled_rect_x + scaled_rect_width, scaled_rect_y), 
                2
            )
            # Bottom wall edge
            pygame.draw.line(
                screen, 
                WHITE, 
                (scaled_rect_x, scaled_rect_y + scaled_rect_height), 
                (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 
                2
            )
        else:  # Vertical segment
            # Left wall edge
            pygame.draw.line(
                screen, 
                WHITE, 
                (scaled_rect_x, scaled_rect_y), 
                (scaled_rect_x, scaled_rect_y + scaled_rect_height), 
                2
            )
            # Right wall edge
            pygame.draw.line(
                screen, 
                WHITE, 
                (scaled_rect_x + scaled_rect_width, scaled_rect_y), 
                (scaled_rect_x + scaled_rect_width, scaled_rect_y + scaled_rect_height), 
                2
            )

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
    
    # Collision checking against the base hallway coordinates
    if not is_in_hallway(player_pos[0], player_pos[1]):
        player_pos = original_pos
    else:
        step_counter += 1
        if step_counter % 10 == 0:
            movement_effects.append(MovementEffect(player_pos[0], player_pos[1]))
    
    # First scale the player position
    scaled_player_x = int(player_pos[0] * scale_x)
    scaled_player_y = int(player_pos[1] * scale_y)
    
    # Calculate camera position to center the player
    camera_x = scaled_player_x - (SCREEN_WIDTH // 2)
    camera_y = scaled_player_y - (SCREEN_HEIGHT // 2)
    
    # Update movement effects and remove faded ones
    movement_effects = [effect for effect in movement_effects if effect.update()]
    
    screen.fill(BLACK)
    
    # Draw the hallway, movement effects, and player using scaled coordinates
    draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
    for effect in movement_effects:
        effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
    # Draw player at the center of the screen
    pygame.draw.circle(screen, PLAYER_COLOR, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x))
    pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), int(player_radius * scale_x), 2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()