# '''import pygame
# import sys

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

# MAP_WIDTH = 1600   # The total width of your dungeon map
# MAP_HEIGHT = 1600  # The total height of your dungeon map

# # Player settings (in base coordinates)
# player_pos = [150, 800]  # Starting position
# player_radius = 10
# player_speed = 3

# # Base hallway path coordinates (in base coordinates)
# # Format: [start_x, start_y, end_x, end_y, width]
# # Static dungeon layout with fixed hallways and rooms
# base_hallway = [
#     # Main entrance corridor
#     [100, 800, 300, 800, 120],
    
#     # Entrance Chamber
#     [300, 700, 300, 900, 200],
#     [300, 700, 500, 700, 200],
#     [300, 900, 500, 900, 200],
#     [500, 700, 500, 900, 200],
    
#     # North passage from entrance
#     [400, 700, 400, 500, 100],
    
#     # Torture Chamber (north of entrance)
#     [300, 400, 300, 500, 160],
#     [300, 400, 500, 400, 160],
#     [500, 400, 500, 500, 160],
#     [300, 500, 500, 500, 160],
    
#     # Prison Cells (west of torture chamber)
#     [200, 350, 300, 350, 80],
#     [200, 350, 200, 450, 80],
#     [200, 450, 300, 450, 80],
    
#     # East passage from entrance chamber
#     [500, 800, 700, 800, 100],
    
#     # Grand Hall (large central chamber)
#     [700, 600, 700, 1000, 300],
#     [700, 600, 1100, 600, 300],
#     [700, 1000, 1100, 1000, 300],
#     [1100, 600, 1100, 1000, 300],
    
#     # North corridor from Grand Hall
#     [900, 600, 900, 400, 100],
    
#     # Library (north of Grand Hall)
#     [750, 300, 750, 400, 180],
#     [750, 300, 1050, 300, 180],
#     [1050, 300, 1050, 400, 180],
#     [750, 400, 1050, 400, 180],
    
#     # Study alcoves in Library
#     [800, 300, 800, 250, 60],
#     [900, 300, 900, 250, 60],
#     [1000, 300, 1000, 250, 60],
    
#     # Secret passage from Library
#     [850, 300, 850, 200, 40],
    
#     # Hidden Treasury
#     [750, 150, 750, 200, 120],
#     [750, 150, 950, 150, 120],
#     [950, 150, 950, 200, 120],
#     [750, 200, 950, 200, 120],
    
#     # East path from Grand Hall
#     [1100, 800, 1300, 800, 100],
    
#     # Dining Hall
#     [1300, 700, 1300, 900, 180],
#     [1300, 700, 1500, 700, 180],
#     [1300, 900, 1500, 900, 180],
#     [1500, 700, 1500, 900, 180],
    
#     # Kitchen (north of Dining Hall)
#     [1400, 700, 1400, 600, 80],
#     [1350, 600, 1450, 600, 100],
#     [1350, 550, 1350, 600, 100],
#     [1450, 550, 1450, 600, 100],
#     [1350, 550, 1450, 550, 100],
    
#     # South passage from Grand Hall
#     [900, 1000, 900, 1200, 100],
    
#     # Throne Room (elaborate southern chamber)
#     [750, 1200, 750, 1400, 250],
#     [750, 1200, 1050, 1200, 250],
#     [750, 1400, 1050, 1400, 250],
#     [1050, 1200, 1050, 1400, 250],
    
#     # Throne platform (raised area in center)
#     [850, 1300, 950, 1300, 100],
#     [850, 1300, 850, 1350, 100],
#     [950, 1300, 950, 1350, 100],
#     [850, 1350, 950, 1350, 100],
    
#     # Secret passage behind throne
#     [900, 1350, 900, 1450, 40],
    
#     # Final Treasure Vault
#     [800, 1450, 800, 1550, 150],
#     [800, 1450, 1000, 1450, 150],
#     [800, 1550, 1000, 1550, 150],
#     [1000, 1450, 1000, 1550, 150],
    
#     # Eastern Wing - side halls and chambers
#     [1200, 600, 1200, 400, 80],
#     [1200, 400, 1350, 400, 80],
#     [1200, 350, 1350, 350, 80],
#     [1200, 450, 1350, 450, 80],
    
#     # Western annex from entrance
#     [300, 800, 300, 1000, 80],
#     [200, 1000, 400, 1000, 80],
#     [200, 950, 200, 1050, 80],
#     [400, 950, 400, 1050, 80],
    
#     # Catacombs
#     [500, 1100, 600, 1100, 60],
#     [600, 1100, 600, 1200, 60],
#     [600, 1200, 700, 1200, 60],
#     [700, 1200, 700, 1100, 60],
#     [700, 1100, 750, 1100, 60],
    
#     # Underground River path
#     [1200, 1000, 1200, 1200, 140],
#     [1100, 1200, 1300, 1200, 140],
#     [1300, 900, 1300, 1200, 140],
    
#     # Bridge over underground river
#     [1225, 1100, 1275, 1100, 40],
# ]

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
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
#         if start_y == end_y:
#             if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and start_y - half_width <= pos_y <= start_y + half_width:
#                 return True
#         elif start_x == end_x:
#             if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and start_x - half_width <= pos_x <= start_x + half_width:
#                 return True
#     return False

# def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
#     """ Draw the hallway based on scaled coordinates. """
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
        
#         if start_y == end_y:  # Horizontal segment
#             rect_x = min(start_x, end_x) * scale_x - camera_x
#             rect_y = (start_y - half_width) * scale_y - camera_y
#             rect_width = abs(end_x - start_x) * scale_x
#             rect_height = width * scale_y
#             pygame.draw.rect(screen, GREEN, (rect_x, rect_y, rect_width, rect_height))
#         else:  # Vertical segment
#             rect_x = (start_x - half_width) * scale_x - camera_x
#             rect_y = min(start_y, end_y) * scale_y - camera_y
#             rect_width = width * scale_x
#             rect_height = abs(end_y - start_y) * scale_y
#             pygame.draw.rect(screen, GREEN, (rect_x, rect_y, rect_width, rect_height))

# clock = pygame.time.Clock()
# movement_effects = []
# step_counter = 0
# running = True

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.VIDEORESIZE:
#             # Update the current screen resolution and window
#             SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
#             screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
#     # Calculate scaling factors based on the current resolution relative to the base resolution
#     scale_x = SCREEN_WIDTH / BASE_WIDTH
#     scale_y = SCREEN_HEIGHT / BASE_HEIGHT

#     keys = pygame.key.get_pressed()
#     original_pos = player_pos.copy()
    
#     # Handle player movement (in base coordinates)
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
    
#     # Compute the player's scaled position
#     scaled_player_x = int(player_pos[0] * scale_x)
#     scaled_player_y = int(player_pos[1] * scale_y)
    
#     # Compute the camera offset so that the player remains centered
#     camera_x = scaled_player_x - SCREEN_WIDTH // 2
#     camera_y = scaled_player_y - SCREEN_HEIGHT // 2
    
#     # Apply camera boundaries to prevent seeing beyond map edges
#     camera_x = max(0, min(camera_x, int(MAP_WIDTH * scale_x) - SCREEN_WIDTH))
#     camera_y = max(0, min(camera_y, int(MAP_HEIGHT * scale_y) - SCREEN_HEIGHT))
    
#     # Update movement effects and remove faded ones
#     movement_effects = [effect for effect in movement_effects if effect.update()]
    
#     screen.fill(BLACK)
    
#     # Draw the hallway, movement effects, and player using scaled coordinates
#     draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
#     for effect in movement_effects:
#         effect.draw(screen, scale_x, scale_y, camera_x, camera_y)
    
#     pygame.draw.circle(screen, PLAYER_COLOR, (scaled_player_x - camera_x, scaled_player_y - camera_y), int(player_radius * scale_x))
#     pygame.draw.circle(screen, WHITE, (scaled_player_x - camera_x, scaled_player_y - camera_y), int(player_radius * scale_x), 2)
    
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
# sys.exit()'''



# import pygame
# import sys
# import math

# # Initialize Pygame
# pygame.init()

# # Base resolution (game logic uses these coordinates)
# BASE_WIDTH = 800
# BASE_HEIGHT = 500

# # Current screen resolution (starts at base resolution)
# SCREEN_WIDTH = BASE_WIDTH
# SCREEN_HEIGHT = BASE_HEIGHT
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
# pygame.display.set_caption("Dungeon Map Layout with Images")

# # Fallback colors (if needed)
# BLACK = (10, 10, 12)
# WHITE = (255, 255, 255)

# # ------------------------------------------------------------------------------
# # 1. Load Images from the assets folder
# # ------------------------------------------------------------------------------

# try: #ISE_SpecialEffects\src\assets\images\backgrounds\floor.png
#     wall_img = pygame.image.load("src/assets/images/backgrounds/walls/wall1.png").convert_alpha()
#     floor_img = pygame.image.load("src/assets/images/backgrounds/floor.png").convert_alpha()
#     #player_img = pygame.image.load("assets/images/background/player.png").convert_alpha()
#     #miniboss_img = pygame.image.load("assets/images/miniboss.png").convert_alpha()
#     gate_img = pygame.image.load("src/assets/images/backgrounds/gate.png").convert_alpha()
# except Exception as e:
#     print("Error loading images. Make sure your assets folder contains the required images.")
#     sys.exit()

# # ------------------------------------------------------------------------------
# # 2. Define Game Variables and Map Data
# # ------------------------------------------------------------------------------

# MAP_WIDTH = 1600   # Total width of the dungeon map (base coordinates)
# MAP_HEIGHT = 1600  # Total height of the dungeon map (base coordinates)

# # Player settings (in base coordinates)
# player_pos = [150, 800]  # Starting position
# player_radius = 10       # Used for collision checks
# player_speed = 3

# # Level and miniboss state variables
# level = 1
# miniboss_alive = True
# miniboss = {
#     "pos": [900, 1350],  # Position near the secret passage in the Throne Room
#     "radius": 20
# }

# # Base hallway/room layout (each segment: [start_x, start_y, end_x, end_y, width])
# base_hallway = [
#     [100, 800, 300, 800, 120],
#     [300, 700, 300, 900, 200],
#     [300, 700, 500, 700, 200],
#     [300, 900, 500, 900, 200],
#     [500, 700, 500, 900, 200],
#     [400, 700, 400, 500, 100],
#     [300, 400, 300, 500, 160],
#     [300, 400, 500, 400, 160],
#     [500, 400, 500, 500, 160],
#     [300, 500, 500, 500, 160],
#     [200, 350, 300, 350, 80],
#     [200, 350, 200, 450, 80],
#     [200, 450, 300, 450, 80],
#     [500, 800, 700, 800, 100],
#     [700, 600, 700, 1000, 300],
#     [700, 600, 1100, 600, 300],
#     [700, 1000, 1100, 1000, 300],
#     [1100, 600, 1100, 1000, 300],
#     [900, 600, 900, 400, 100],
#     [750, 300, 750, 400, 180],
#     [750, 300, 1050, 300, 180],
#     [1050, 300, 1050, 400, 180],
#     [750, 400, 1050, 400, 180],
#     [800, 300, 800, 250, 60],
#     [900, 300, 900, 250, 60],
#     [1000, 300, 1000, 250, 60],
#     [850, 300, 850, 200, 40],
#     [750, 150, 750, 200, 120],
#     [750, 150, 950, 150, 120],
#     [950, 150, 950, 200, 120],
#     [750, 200, 950, 200, 120],
#     [1100, 800, 1300, 800, 100],
#     [1300, 700, 1300, 900, 180],
#     [1300, 700, 1500, 700, 180],
#     [1300, 900, 1500, 900, 180],
#     [1500, 700, 1500, 900, 180],
#     [1400, 700, 1400, 600, 80],
#     [1350, 600, 1450, 600, 100],
#     [1350, 550, 1350, 600, 100],
#     [1450, 550, 1450, 600, 100],
#     [1350, 550, 1450, 550, 100],
#     [900, 1000, 900, 1200, 100],
#     [750, 1200, 750, 1400, 250],
#     [750, 1200, 1050, 1200, 250],
#     [750, 1400, 1050, 1400, 250],
#     [1050, 1200, 1050, 1400, 250],
#     [850, 1300, 950, 1300, 100],
#     [850, 1300, 850, 1350, 100],
#     [950, 1300, 950, 1350, 100],
#     [850, 1350, 950, 1350, 100],
#     [900, 1350, 900, 1450, 40],  # Secret passage (gate) behind the throne
#     [800, 1450, 800, 1550, 150],
#     [800, 1450, 1000, 1450, 150],
#     [800, 1550, 1000, 1550, 150],
#     [1000, 1450, 1000, 1550, 150],
#     [1200, 600, 1200, 400, 80],
#     [1200, 400, 1350, 400, 80],
#     [1200, 350, 1350, 350, 80],
#     [1200, 450, 1350, 450, 80],
#     [300, 800, 300, 1000, 80],
#     [200, 1000, 400, 1000, 80],
#     [200, 950, 200, 1050, 80],
#     [400, 950, 400, 1050, 80],
#     [500, 1100, 600, 1100, 60],
#     [600, 1100, 600, 1200, 60],
#     [600, 1200, 700, 1200, 60],
#     [700, 1200, 700, 1100, 60],
#     [700, 1100, 750, 1100, 60],
#     [1200, 1000, 1200, 1200, 140],
#     [1100, 1200, 1300, 1200, 140],
#     [1300, 900, 1300, 1200, 140],
#     [1225, 1100, 1275, 1100, 40],
# ]

# # Room information for displaying room names
# room_areas = [
#     {"name": "Entrance", "x": 300, "y": 800, "radius": 150},
#     {"name": "Torture Chamber", "x": 400, "y": 450, "radius": 100},
#     {"name": "Prison Cells", "x": 220, "y": 400, "radius": 80},
#     {"name": "Grand Hall", "x": 900, "y": 800, "radius": 200},
#     {"name": "Library", "x": 900, "y": 350, "radius": 150},
#     {"name": "Treasury", "x": 850, "y": 175, "radius": 80},
#     {"name": "Dining Hall", "x": 1400, "y": 800, "radius": 150},
#     {"name": "Kitchen", "x": 1400, "y": 570, "radius": 80},
#     {"name": "Throne Room", "x": 900, "y": 1300, "radius": 180},
#     {"name": "Treasure Vault", "x": 900, "y": 1500, "radius": 120},
#     {"name": "Catacombs", "x": 650, "y": 1150, "radius": 80},
#     {"name": "Underground River", "x": 1200, "y": 1100, "radius": 100}
# ]

# # ------------------------------------------------------------------------------
# # 3. Define Helper and Drawing Functions
# # ------------------------------------------------------------------------------

# def is_in_hallway(pos_x, pos_y):
#     """Check if the given position (in base coordinates) is within any hallway segment."""
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
#         if start_y == end_y:  # Horizontal segment
#             if min(start_x, end_x) <= pos_x <= max(start_x, end_x) and start_y - half_width <= pos_y <= start_y + half_width:
#                 return True
#         elif start_x == end_x:  # Vertical segment
#             if min(start_y, end_y) <= pos_y <= max(start_y, end_y) and start_x - half_width <= pos_x <= start_x + half_width:
#                 return True
#     return False

# def draw_hallway(screen, scale_x, scale_y, camera_x, camera_y):
#     """Draws the dungeon's floors and walls using image textures."""
#     # Draw floor segments using the floor image
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2

#         if start_y == end_y:  # Horizontal segment
#             rect_x = int(min(start_x, end_x) * scale_x) - camera_x
#             rect_y = int((start_y - half_width) * scale_y) - camera_y
#             rect_width = int(abs(end_x - start_x) * scale_x)
#             rect_height = int(width * scale_y)
#         else:  # Vertical segment
#             rect_x = int((start_x - half_width) * scale_x) - camera_x
#             rect_y = int(min(start_y, end_y) * scale_y) - camera_y
#             rect_width = int(width * scale_x)
#             rect_height = int(abs(end_y - start_y) * scale_y)

#         floor_tile = pygame.transform.scale(floor_img, (rect_width, rect_height))
#         screen.blit(floor_tile, (rect_x, rect_y))

#     # # Draw walls using the wall image
#     # for segment in base_hallway:
#     #     start_x, start_y, end_x, end_y, width = segment
#     #     half_width = width / 2
#     #     wall_thickness = max(6, int(width / 10)) * scale_x

#     #     if start_y == end_y:  # Horizontal segment walls
#     #         # Top wall
#     #         rect_x = int(min(start_x, end_x) * scale_x) - camera_x
#     #         rect_y = int((start_y - half_width) * scale_y) - camera_y - int(wall_thickness)
#     #         rect_width = int(abs(end_x - start_x) * scale_x)
#     #         rect_height = int(wall_thickness)
#     #         wall_tile = pygame.transform.scale(wall_img, (rect_width, rect_height))
#     #         screen.blit(wall_tile, (rect_x, rect_y))
#     #         # Bottom wall
#     #         rect_y = int((start_y + half_width) * scale_y) - camera_y
#     #         wall_tile = pygame.transform.scale(wall_img, (rect_width, int(wall_thickness)))
#     #         screen.blit(wall_tile, (rect_x, rect_y))
#     #     else:  # Vertical segment walls
#     #         # Left wall
#     #         rect_x = int((start_x - half_width) * scale_x) - camera_x - int(wall_thickness)
#     #         rect_y = int(min(start_y, end_y) * scale_y) - camera_y
#     #         rect_width = int(wall_thickness)
#     #         rect_height = int(abs(end_y - start_y) * scale_y)
#     #         wall_tile = pygame.transform.scale(wall_img, (rect_width, rect_height))
#     #         screen.blit(wall_tile, (rect_x, rect_y))
#     #         # Right wall
#     #         rect_x = int((start_x + half_width) * scale_x) - camera_x
#     #         wall_tile = pygame.transform.scale(wall_img, (int(wall_thickness), rect_height))
#     #         screen.blit(wall_tile, (rect_x, rect_y))

# def get_current_room(player_pos):
#     """Return the name of the room the player is currently in, based on distance to room centers."""
#     for room in room_areas:
#         dist = math.sqrt((player_pos[0] - room["x"])**2 + (player_pos[1] - room["y"])**2)
#         if dist < room["radius"]:
#             return room["name"]
#     return "Hallway"

# def draw_minimap(screen, player_pos, scale_x, scale_y):
#     """Draws a simple minimap in the corner."""
#     minimap_size = 200
#     minimap_scale = 0.1
#     minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
#     minimap_surface.fill((0, 0, 0, 150))
    
#     for segment in base_hallway:
#         start_x, start_y, end_x, end_y, width = segment
#         half_width = width / 2
        
#         if start_y == end_y:
#             rect_x = (min(start_x, end_x) - 800) * minimap_scale + minimap_size / 2
#             rect_y = (start_y - 800) * minimap_scale + minimap_size / 2
#             rect_width = abs(end_x - start_x) * minimap_scale
#             rect_height = width * minimap_scale
#             pygame.draw.rect(minimap_surface, (180, 170, 155), (rect_x, rect_y, rect_width, rect_height))
#         else:
#             rect_x = (start_x - half_width - 800) * minimap_scale + minimap_size / 2
#             rect_y = (min(start_y, end_y) - 800) * minimap_scale + minimap_size / 2
#             rect_width = width * minimap_scale
#             rect_height = abs(end_y - start_y) * minimap_scale
#             pygame.draw.rect(minimap_surface, (180, 170, 155), (rect_x, rect_y, rect_width, rect_height))
    
#     player_x = (player_pos[0] - 800) * minimap_scale + minimap_size / 2
#     player_y = (player_pos[1] - 800) * minimap_scale + minimap_size / 2
#     pygame.draw.circle(minimap_surface, WHITE, (player_x, player_y), 3)
#     pygame.draw.rect(minimap_surface, WHITE, (0, 0, minimap_size, minimap_size), 2)
    
#     screen.blit(minimap_surface, (20, 20))

# # def draw_miniboss(screen, scale_x, scale_y, camera_x, camera_y):
# #     """Draw the miniboss using its image, if it is still alive."""
# #     if miniboss_alive:
# #         boss_x = int(miniboss["pos"][0] * scale_x) - camera_x
# #         boss_y = int(miniboss["pos"][1] * scale_y) - camera_y
# #         boss_diameter = int(miniboss["radius"] * 2 * scale_x)
# #         boss_img_scaled = pygame.transform.scale(miniboss_img, (boss_diameter, boss_diameter))
# #         # Center the image on the boss position
# #         screen.blit(boss_img_scaled, (boss_x - boss_diameter // 2, boss_y - boss_diameter // 2))

# def draw_gate(screen, scale_x, scale_y, camera_x, camera_y):
#     """Draw the gate (secret passage) using its image.
#        If the miniboss is still alive, overlay a dark tint to indicate it is closed."""
#     # Gate region (base coordinates)
#     gate_x = 880
#     gate_y = 1350
#     gate_w = 40
#     gate_h = 100
#     rect_x = int(gate_x * scale_x) - camera_x
#     rect_y = int(gate_y * scale_y) - camera_y
#     rect_w = int(gate_w * scale_x)
#     rect_h = int(gate_h * scale_y)
    
#     gate_img_scaled = pygame.transform.scale(gate_img, (rect_w, rect_h))
    
#     if miniboss_alive:
#         # Draw gate with a dark overlay if closed
#         screen.blit(gate_img_scaled, (rect_x, rect_y))
#         dark_overlay = pygame.Surface((rect_w, rect_h))
#         dark_overlay.fill((80, 80, 80))
#         dark_overlay.set_alpha(150)
#         screen.blit(dark_overlay, (rect_x, rect_y))
#     else:
#         # Gate open
#         screen.blit(gate_img_scaled, (rect_x, rect_y))

# def draw_player(screen, scaled_player_x, scaled_player_y, camera_x, camera_y, scale_x):
#     """Draw the player sprite instead of a circle."""
#     size = int(player_radius * 4 * scale_x)  # Adjust size multiplier as needed
#     # player_img_scaled = pygame.transform.scale(player_img, (size, size))
#     screen.blit(Green, (scaled_player_x - camera_x - size // 2, 
#                                     scaled_player_y - camera_y - size // 2))

# # ------------------------------------------------------------------------------
# # 4. Main Game Loop
# # ------------------------------------------------------------------------------

# clock = pygame.time.Clock()
# running = True

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.VIDEORESIZE:
#             SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
#             screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
#     # Calculate scaling factors based on current resolution relative to base resolution
#     scale_x = SCREEN_WIDTH / BASE_WIDTH
#     scale_y = SCREEN_HEIGHT / BASE_HEIGHT

#     keys = pygame.key.get_pressed()
#     original_pos = player_pos.copy()
    
#     if level == 1:
#         # Player movement (in base coordinates)
#         if keys[pygame.K_LEFT]:
#             player_pos[0] -= player_speed
#         if keys[pygame.K_RIGHT]:
#             player_pos[0] += player_speed
#         if keys[pygame.K_UP]:
#             player_pos[1] -= player_speed
#         if keys[pygame.K_DOWN]:
#             player_pos[1] += player_speed
        
#         # Check collision with hallways; if not in a hallway, revert to previous position
#         if not is_in_hallway(player_pos[0], player_pos[1]):
#             player_pos = original_pos
        
#         # Check collision with the miniboss (simple circular collision detection)
#         if miniboss_alive:
#             dx = player_pos[0] - miniboss["pos"][0]
#             dy = player_pos[1] - miniboss["pos"][1]
#             if math.sqrt(dx ** 2 + dy ** 2) < (player_radius + miniboss["radius"]):
#                 miniboss_alive = False  # Defeat the miniboss
        
#         # If miniboss is defeated, check if the player enters the gate region to transition to Level 2
#         if not miniboss_alive:
#             if 880 <= player_pos[0] <= 920 and 1350 <= player_pos[1] <= 1450:
#                 level = 2  # Transition to Level 2

#     # Clear screen
#     screen.fill(BLACK)
    
#     if level == 1:
#         # Compute scaled player position and camera offset (so the player remains centered)
#         scaled_player_x = int(player_pos[0] * scale_x)
#         scaled_player_y = int(player_pos[1] * scale_y)
#         camera_x = scaled_player_x - SCREEN_WIDTH // 2
#         camera_y = scaled_player_y - SCREEN_HEIGHT // 2
        
#         # Clamp camera offset to map boundaries
#         camera_x = max(0, min(camera_x, int(MAP_WIDTH * scale_x) - SCREEN_WIDTH))
#         camera_y = max(0, min(camera_y, int(MAP_HEIGHT * scale_y) - SCREEN_HEIGHT))
        
#         # Draw the dungeon elements
#         draw_hallway(screen, scale_x, scale_y, camera_x, camera_y)
#         draw_gate(screen, scale_x, scale_y, camera_x, camera_y)
#         # draw_miniboss(screen, scale_x, scale_y, camera_x, camera_y)
#         # draw_player(screen, scaled_player_x, scaled_player_y, camera_x, camera_y, scale_x)
        
#         current_room = get_current_room(player_pos)
#         font = pygame.font.SysFont(None, 24)
#         room_text = font.render(f"Location: {current_room}", True, WHITE)
#         screen.blit(room_text, (20, 230))
        
#         draw_minimap(screen, player_pos, scale_x, scale_y)
#         help_text = font.render("Arrow Keys: Move | Esc: Quit", True, WHITE)
#         screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, SCREEN_HEIGHT - 30))
    
#     else:
#         # Level 2 screen (simple transition)
#         screen.fill((0, 0, 50))
#         font = pygame.font.SysFont(None, 48)
#         level_text = font.render("Welcome to Level 2!", True, WHITE)
#         screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 
#                                  SCREEN_HEIGHT // 2 - level_text.get_height() // 2))
    
#     # Allow quitting with the Esc key
#     if keys[pygame.K_ESCAPE]:
#         running = False
    
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
# sys.exit()




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