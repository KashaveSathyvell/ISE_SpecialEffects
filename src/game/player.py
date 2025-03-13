import pygame
import os
import sys

STANDARD_HEIGHT = 75

class Character:
    def __init__(self, x, y, character_type, height, max_health=100):
        self.z_index = 0
        self.x, self.y = x, y  # x is center, y is bottom
        self.character_type = character_type
        self.height = height
        self.direction = 'right'
        self.speed = 5

        # States
        self.moving = self.jumping = self.attacking = self.dead = False
        self.shielding = False
        self.shield_frame_locked = False  # New variable to track if shield frame is locked
        self.hurt = False  # Add hurt state

        # Animation settings
        self.frame_counts = {}
        self.animation_speeds = {
            'idle': 100, 'move': 80, 'attack': 50,
            'ultimate': 40, 'death': 120, 'jump': 70,
            'shield': 60, 'hurt': 60  # Add hurt animation speed
        }
        self.frame_index = 0
        self.action = 'idle'
        self.last_update = pygame.time.get_ticks()

        # Health system
        self.max_health = self.health = max_health
        self.damage_amount = 10
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000

        # Hit effect variables
        self.hit_effect = False
        self.hit_effect_timer = 0
        self.hit_effect_duration = 500
        self.hit_visible = True

        # Hurt animation timer
        self.hurt_timer = 0
        self.hurt_duration = 500

        # Ultimate attack system
        self.ultimate_ready = False
        self.ultimate_cooldown = 5000
        self.ultimate_last_used = 0
        self.ultimate_charge = 0
        self.ultimate_damage = 30
        self.using_ultimate = False

        # Animation storage
        self.animations = {}
        self.masks = {}
        self.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{character_type}"))

        # Initial setup
        self.current_image = self.get_frame('idle_right', 0)
        self.rect = self.current_image.get_rect()
        self.rect.midbottom = (x, y)
        self.hitbox = self.rect.inflate(-20, -20)
        self.hitbox.midbottom = self.rect.midbottom
        self.current_mask = self.get_mask('idle_right', 0)

    def set_frame_count(self, action, count):
        self.frame_counts[action] = count

    def set_animation_speed(self, action, speed_ms):
        self.animation_speeds[action] = speed_ms

    def load_animations(self, folder_path):
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Character folder {folder_path} not found.")

        for action, count in self.frame_counts.items():
            strip_path = os.path.join(folder_path, f"{action}.png")

            if os.path.exists(strip_path):
                strip_img = pygame.image.load(strip_path).convert_alpha()
                frame_width = strip_img.get_width() // count

                right_frames, right_masks = [], []

                for i in range(count):
                    frame_rect = pygame.Rect(i * frame_width, 0, frame_width, strip_img.get_height())
                    frame = strip_img.subsurface(frame_rect)

                    aspect_ratio = frame.get_width() / frame.get_height()
                    scaling_factor = 1.5

                    # Scale the image before storing
                    scaled_width = int(self.height * aspect_ratio * scaling_factor)
                    scaled_height = int(self.height * scaling_factor)
                    scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))

                    right_frames.append(scaled_frame)
                    right_masks.append(pygame.mask.from_surface(scaled_frame))

                self.animations[f'{action}_right'] = right_frames
                self.masks[f'{action}_right'] = right_masks

                # Flipped versions for left direction
                left_frames = [pygame.transform.flip(frame, True, False) for frame in right_frames]
                left_masks = [pygame.mask.from_surface(frame) for frame in left_frames]

                self.animations[f'{action}_left'] = left_frames
                self.masks[f'{action}_left'] = left_masks

    def get_frame(self, animation_key, index):
        if animation_key in self.animations and len(self.animations[animation_key]) > 0:
            safe_index = min(index, len(self.animations[animation_key]) - 1)
            return self.animations[animation_key][safe_index]
        elif 'idle_right' in self.animations and len(self.animations['idle_right']) > 0:
            return self.animations['idle_right'][0]
        else:
            # Create placeholder
            placeholder = pygame.Surface((50, self.height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))
            return placeholder

    def get_mask(self, animation_key, index):
        if animation_key in self.masks and len(self.masks[animation_key]) > 0:
            safe_index = min(index, len(self.masks[animation_key]) - 1)
            return self.masks[animation_key][safe_index]
        elif 'idle_right' in self.masks and len(self.masks['idle_right']) > 0:
            return self.masks['idle_right'][0]
        else:
            # Create placeholder mask
            placeholder = pygame.Surface((50, self.height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))
            return pygame.mask.from_surface(placeholder)

    def update(self):
        current_time = pygame.time.get_ticks()

        # Update invincibility and hit effect
        if self.invincible and current_time - self.invincible_timer > self.invincible_duration:
            self.invincible = False

        if self.hit_effect and current_time - self.hit_effect_timer > self.hit_effect_duration:
            self.hit_effect = False
            self.hit_visible = True

        # Check if hurt animation should end
        if self.hurt and current_time - self.hurt_timer > self.hurt_duration:
            self.hurt = False

        # Check if health is depleted
        if self.health <= 0 and not self.dead:
            self.die()

        # Update ultimate charge
        if not self.ultimate_ready and not self.dead and not self.using_ultimate:
            time_since_used = current_time - self.ultimate_last_used
            self.ultimate_charge = min(100, time_since_used / self.ultimate_cooldown * 100)
            self.ultimate_ready = self.ultimate_charge >= 100

        # Set current action based on priority
        if self.dead:
            self.action = 'death'
        elif self.hurt:
            self.action = 'hurt'
        elif self.using_ultimate:
            self.action = 'ultimate'
        elif self.shielding:
            self.action = 'shield'
        elif self.attacking:
            self.action = 'attack'
        elif self.jumping:
            self.action = 'jump'  # Jump animation still plays, but movement isn't blocked
        elif self.moving:  # Allow movement while jumping
            self.action = 'move'
        else:
            self.action = 'idle'

        # Current animation key
        animation_key = f'{self.action}_{self.direction}'

        # Update frame based on animation speed
        current_animation_speed = self.animation_speeds.get(self.action, 100)
        if current_time - self.last_update > current_animation_speed:
            self.last_update = current_time

            # Only update frame_index if not shield_frame_locked
            if not (self.action == 'shield' and self.shield_frame_locked):
                self.frame_index += 1

            # Handle end of animation
            if animation_key in self.animations and self.frame_index >= len(self.animations[animation_key]):
                if self.action == 'death':
                    self.frame_index = len(self.animations[animation_key]) - 1  # Stay on last frame
                elif self.action == 'hurt':
                    # Complete the hurt animation and then reset the hurt state
                    self.hurt = False
                    self.frame_index = 0
                elif self.action == 'shield':
                    # Lock on the last frame while shielding
                    self.frame_index = len(self.animations[animation_key]) - 1
                    self.shield_frame_locked = True
                elif self.action in ['attack', 'ultimate', 'jump']:
                    if self.action == 'attack':
                        self.attacking = False
                    elif self.action == 'ultimate':
                        self.using_ultimate = False
                        self.ultimate_last_used = pygame.time.get_ticks()
                    elif self.action == 'jump':
                        self.jumping = False
                    self.frame_index = 0
                else:
                    self.frame_index = 0

        # Update image and collision data
        self.current_image = self.get_frame(animation_key, self.frame_index)
        self.current_mask = self.get_mask(animation_key, self.frame_index)
        self.rect = self.current_image.get_rect()
        self.rect.midbottom = (self.x, self.y)
        self.hitbox = self.rect.inflate(-20, -20)
        self.hitbox.midbottom = self.rect.midbottom

    def toggle_shield(self, active=None):
        if self.dead or self.attacking or self.using_ultimate:
            return False

        # Toggle or set specific state
        if active is None:
            active = not self.shielding

        # Reset shield animation if turning on shield
        if active and not self.shielding:
            self.frame_index = 0
            self.shield_frame_locked = False

        # Reset lock when turning off shield
        if not active:
            self.shield_frame_locked = False

        self.shielding = active
        return True

    def use_ultimate(self, enemies):
        if self.ultimate_ready and not self.dead and not self.attacking:
            self.using_ultimate = True
            self.ultimate_ready = False
            self.ultimate_charge = 0
            self.frame_index = 0
            
            # Check for enemy collisions
            for enemy in enemies:
                if self.check_collision(enemy):  # Sword hits enemy
                    enemy.take_damage(self.ultimate_damage)  
                    print(f"Hit enemy! Enemy health: {enemy.health}")
            
            return True
        return False

    def move(self, dx, dy):
        # Don't allow movement if dead
        if self.dead:
            return
            
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'

        self.moving = dx != 0 or dy != 0
        
        # Allow horizontal movement even while jumping
        if self.jumping:
            self.x += dx 
            self.y += dy
        else:
            self.x += dx
            self.y += dy
    
    def attack(self, enemies):
        if not self.attacking and not self.using_ultimate and not self.dead:
            self.attacking = True
            self.frame_index = 0  # Restart animation
    
            # Check for enemy collisions
            for enemy in enemies:
                if self.check_collision(enemy):  # Sword hits enemy
                    enemy.take_damage(self.damage_amount)  
                    print(f"Hit enemy! Enemy health: {enemy.health}")

    def jump(self):
        if not self.jumping and not self.dead:
            self.jumping = True
            self.frame_index = 0

    def die(self):
        if not self.dead:
            self.dead = True
            self.frame_index = 0
            print("Player died!")

    def reset(self):
        self.dead = False
        self.hurt = False
        self.attacking = self.using_ultimate = self.moving = self.jumping = False
        self.shielding = False
        self.shield_frame_locked = False
        self.frame_index = 0
        self.action = 'idle'
        self.health = self.max_health
        self.invincible = self.hit_effect = False
        self.ultimate_charge = 0
        self.ultimate_ready = False
        self.ultimate_last_used = pygame.time.get_ticks()
    
    def take_damage(self, amount):
        # Check if we can block with shield
        if self.shielding:
            self.hit_effect = True
            self.hit_effect_timer = pygame.time.get_ticks()
            self.hit_visible = False
            return False  # Damage was blocked

        # Check if we're already invincible
        current_time = pygame.time.get_ticks()
        if self.invincible or self.dead:
            return False
    
        # Apply damage
        self.health = max(0, self.health - amount)
        print(f"Player took {amount} damage! Remaining HP: {self.health}")
    
        # Activate hurt state and animation
        self.hurt = True
        self.hurt_timer = current_time
        self.frame_index = 0  # Restart hurt animation
    
        # Trigger invincibility and hit effect
        self.invincible = True
        self.invincible_timer = current_time
        self.hit_effect = True
        self.hit_effect_timer = current_time
        self.hit_visible = False
    
        # Check if we died
        if self.health <= 0:
            self.die()
        
        return True

    def draw(self, surface):
        if self.hit_effect and not self.hit_visible:
            # Draw white silhouette for hit effect
            mask_outline = self.current_mask.to_surface(setcolor=(255, 255, 255, 220), unsetcolor=(0, 0, 0, 0))
            surface.blit(mask_outline, self.rect)
        else:
            surface.blit(self.current_image, self.rect)

        # Draw small health bar
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        bar_width, bar_height = 40, 5
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 10

        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))

        # Health fill (green)
        if self.health > 0:
            fill = (self.health / self.max_health) * bar_width
            pygame.draw.rect(surface, (0, 255, 0), (x, y, int(fill), bar_height))

        # Border
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)

    def draw_main_health_bar(self, surface, x, y, width=200, height=20):
        # Background
        pygame.draw.rect(surface, (100, 0, 0), (x, y, width, height))

        # Health fill
        if self.health > 0:
            fill = (self.health / self.max_health) * width
            pygame.draw.rect(surface, (0, 200, 0), (x, y, int(fill), height))

        # Border and text
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{self.health}/{self.max_health} HP", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width//2, y + height//2))
        surface.blit(text, text_rect)

    def draw_ultimate_bar(self, surface, x, y, width=200, height=10):
        # Background
        pygame.draw.rect(surface, (50, 50, 100), (x, y, width, height))

        # Charge fill
        if self.ultimate_charge > 0:
            fill = (self.ultimate_charge / 100) * width
            color = (100, 100, 255) if not self.ultimate_ready else (200, 200, 255)
            pygame.draw.rect(surface, color, (x, y, int(fill), height))

        # Ready indicator
        border_color = (255, 255, 100) if self.ultimate_ready else (0, 0, 0)
        border_width = 2 if self.ultimate_ready else 1
        pygame.draw.rect(surface, border_color, (x, y, width, height), border_width)

        # Ready text
        if self.ultimate_ready:
            font = pygame.font.SysFont(None, 18)
            text = font.render("Ultimate Ready (X)", True, (255, 255, 100))
            surface.blit(text, (x + width + 5, y))

    def check_collision(self, enemy):
        # Get offset for mask-based collision
        offset = (enemy.rect.x - self.rect.x, enemy.rect.y - self.rect.y)
    
        # Check if attack animation overlaps with enemy's mask
        return self.current_mask.overlap(enemy.mask, offset) is not None

    def can_deal_damage(self):
        return (self.attacking or self.using_ultimate) and not self.dead

    def get_damage_amount(self):
        return self.ultimate_damage if self.using_ultimate else self.damage_amount


class CharacterManager:
    def __init__(self, standard_height=STANDARD_HEIGHT):
        self.characters = {}
        self.standard_height = standard_height

    def add_character(self, character_id, x, y, character_type, height=None):
        character = Character(x, y, character_type, height or self.standard_height)
        self.characters[character_id] = character
        return character

    def set_frame_counts(self, character_id, frame_counts):
        character = self.get_character(character_id)
        if character:
            for action, count in frame_counts.items():
                character.set_frame_count(action, count)
            character.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{character.character_type}"))

    def set_animation_speeds(self, character_id, speed_dict):
        character = self.get_character(character_id)
        if character:
            for action, speed in speed_dict.items():
                character.set_animation_speed(action, speed)

    def configure_ultimate(self, character_id, cooldown=5000, damage=30):
        character = self.get_character(character_id)
        if character:
            character.ultimate_cooldown = cooldown
            character.ultimate_damage = damage

    def update_all(self):
        for character in self.characters.values():
            character.update()

    def draw_all(self, surface):
        # Sort characters by z-index for proper depth
        for character in sorted(self.characters.values(), key=lambda c: c.z_index):
            character.draw(surface)

    def draw_controlled_ui(self, surface, controlled_id, x=20, y=20):
        if controlled_id in self.characters:
            char = self.characters[controlled_id]
            char.draw_main_health_bar(surface, x, y, 200, 20)
            char.draw_ultimate_bar(surface, x, y + 25, 200, 10)

    def get_character(self, character_id):
        return self.characters.get(character_id)

    def check_all_collisions(self):
        collisions = []
        combat_results = []
        char_ids = list(self.characters.keys())

        for i in range(len(char_ids)):
            for j in range(i + 1, len(char_ids)):
                char1_id, char2_id = char_ids[i], char_ids[j]
                char1, char2 = self.characters[char1_id], self.characters[char2_id]

                if char1.check_collision(char2):
                    collisions.append((char1_id, char2_id))

                    # Check char1 damaging char2
                    if char1.can_deal_damage():
                        damage = char1.get_damage_amount()
                        if char2.take_damage(damage):
                            combat_results.append((char1_id, char2_id, damage))

                    # Check char2 damaging char1
                    if char2.can_deal_damage():
                        damage = char2.get_damage_amount()
                        if char1.take_damage(damage):
                            combat_results.append((char2_id, char1_id, damage))

        return collisions, combat_results



# import pygame
# import os
# import sys

# STANDARD_HEIGHT = 75

# class Character:
#     def __init__(self, x, y, character_type, height, max_health=100):
#         self.z_index = 0
#         self.x, self.y = x, y  # x is center, y is bottom
#         self.character_type = character_type
#         self.height = height
#         self.direction = 'right'
#         self.speed = 5

#         # States
#         self.moving = self.jumping = self.attacking = self.dead = False
#         self.shielding = False
#         self.shield_frame_locked = False  # New variable to track if shield frame is locked

#         # Animation settings
#         self.frame_counts = {}
#         self.animation_speeds = {
#             'idle': 100, 'move': 80, 'attack': 50,
#             'ultimate': 40, 'death': 120, 'jump': 70,
#             'shield': 60
#         }
#         self.frame_index = 0
#         self.action = 'idle'
#         self.last_update = pygame.time.get_ticks()

#         # Health system
#         self.max_health = self.health = max_health
#         self.damage_amount = 10
#         self.invincible = False
#         self.invincible_timer = 0
#         self.invincible_duration = 1000

#         # Hit effect variables
#         self.hit_effect = False
#         self.hit_effect_timer = 0
#         self.hit_effect_duration = 500
#         self.hit_visible = True

#         # Ultimate attack system
#         self.ultimate_ready = False
#         self.ultimate_cooldown = 5000
#         self.ultimate_last_used = 0
#         self.ultimate_charge = 0
#         self.ultimate_damage = 30
#         self.using_ultimate = False

#         # Animation storage
#         self.animations = {}
#         self.masks = {}
#         # self.load_animations(f'../assets/images/player/Knight/{character_type}')
#         self.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{character_type}"))


#         # Initial setup
#         self.current_image = self.get_frame('idle_right', 0)
#         self.rect = self.current_image.get_rect()
#         self.rect.midbottom = (x, y)
#         self.hitbox = self.rect.inflate(-20, -20)
#         self.hitbox.midbottom = self.rect.midbottom
#         self.current_mask = self.get_mask('idle_right', 0)

#     def set_frame_count(self, action, count):
#         self.frame_counts[action] = count

#     def set_animation_speed(self, action, speed_ms):
#         self.animation_speeds[action] = speed_ms

#     def load_animations(self, folder_path):
#         if not os.path.exists(folder_path):
#             raise FileNotFoundError(f"Character folder {folder_path} not found.")

#         for action, count in self.frame_counts.items():
#             strip_path = os.path.join(folder_path, f"{action}.png")

#             if os.path.exists(strip_path):
#                 strip_img = pygame.image.load(strip_path).convert_alpha()
#                 frame_width = strip_img.get_width() // count

#                 right_frames, right_masks = [], []

#                 for i in range(count):
#                     frame_rect = pygame.Rect(i * frame_width, 0, frame_width, strip_img.get_height())
#                     frame = strip_img.subsurface(frame_rect)

#                     aspect_ratio = frame.get_width() / frame.get_height()
#                     scaling_factor = 1.5

#                     # Scale the image before storing
#                     scaled_width = int(self.height * aspect_ratio * scaling_factor)
#                     scaled_height = int(self.height * scaling_factor)
#                     scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))

#                     right_frames.append(scaled_frame)
#                     right_masks.append(pygame.mask.from_surface(scaled_frame))

#                 self.animations[f'{action}_right'] = right_frames
#                 self.masks[f'{action}_right'] = right_masks

#                 # Flipped versions for left direction
#                 left_frames = [pygame.transform.flip(frame, True, False) for frame in right_frames]
#                 left_masks = [pygame.mask.from_surface(frame) for frame in left_frames]

#                 self.animations[f'{action}_left'] = left_frames
#                 self.masks[f'{action}_left'] = left_masks

#     def get_frame(self, animation_key, index):
#         if animation_key in self.animations and len(self.animations[animation_key]) > 0:
#             safe_index = min(index, len(self.animations[animation_key]) - 1)
#             return self.animations[animation_key][safe_index]
#         elif 'idle_right' in self.animations and len(self.animations['idle_right']) > 0:
#             return self.animations['idle_right'][0]
#         else:
#             # Create placeholder
#             placeholder = pygame.Surface((50, self.height), pygame.SRCALPHA)
#             placeholder.fill((255, 0, 255))
#             return placeholder

#     def get_mask(self, animation_key, index):
#         if animation_key in self.masks and len(self.masks[animation_key]) > 0:
#             safe_index = min(index, len(self.masks[animation_key]) - 1)
#             return self.masks[animation_key][safe_index]
#         elif 'idle_right' in self.masks and len(self.masks['idle_right']) > 0:
#             return self.masks['idle_right'][0]
#         else:
#             # Create placeholder mask
#             placeholder = pygame.Surface((50, self.height), pygame.SRCALPHA)
#             placeholder.fill((255, 0, 255))
#             return pygame.mask.from_surface(placeholder)

#     def update(self):
#         current_time = pygame.time.get_ticks()

#         # Update invincibility and hit effect
#         if self.invincible and current_time - self.invincible_timer > self.invincible_duration:
#             self.invincible = False

#         if self.hit_effect and current_time - self.hit_effect_timer > self.hit_effect_duration:
#             self.hit_effect = False
#             self.hit_visible = True

#         # Check if health is depleted
#         if self.health <= 0 and not self.dead:
#             self.die()

#         # Update ultimate charge
#         if not self.ultimate_ready and not self.dead and not self.using_ultimate:
#             time_since_used = current_time - self.ultimate_last_used
#             self.ultimate_charge = min(100, time_since_used / self.ultimate_cooldown * 100)
#             self.ultimate_ready = self.ultimate_charge >= 100

#         # Set current action based on priority
#         if self.dead:
#             self.action = 'death'
#         elif self.using_ultimate:
#             self.action = 'ultimate'
#         elif self.shielding:
#             self.action = 'shield'
#         elif self.attacking:
#             self.action = 'attack'
#         elif self.jumping:
#             self.action = 'jump'  # Jump animation still plays, but movement isn't blocked
#         elif self.moving:  # Allow movement while jumping
#             self.action = 'move'

#         else:
#             self.action = 'idle'

#         # Current animation key
#         animation_key = f'{self.action}_{self.direction}'

#         # Update frame based on animation speed
#         current_animation_speed = self.animation_speeds.get(self.action, 100)
#         if current_time - self.last_update > current_animation_speed:
#             self.last_update = current_time

#             # Only update frame_index if not shield_frame_locked
#             if not (self.action == 'shield' and self.shield_frame_locked):
#                 self.frame_index += 1

#             # Handle end of animation
#             if animation_key in self.animations and self.frame_index >= len(self.animations[animation_key]):
#                 if self.action == 'death':
#                     self.frame_index = len(self.animations[animation_key]) - 1  # Stay on last frame
#                 elif self.action == "hurt":
#                     if pygame.time.get_ticks() - self.hurt_timer > 300:  # Hurt animation lasts 300ms
#                         self.action = "idle"  # Return to idle after animation
#                 elif self.action == 'shield':
#                     # Lock on the last frame while shielding
#                     self.frame_index = len(self.animations[animation_key]) - 1
#                     self.shield_frame_locked = True
#                 elif self.action in ['attack', 'ultimate', 'jump']:
#                     if self.action == 'attack':
#                         self.attacking = False
#                     elif self.action == 'ultimate':
#                         self.using_ultimate = False
#                         self.ultimate_last_used = pygame.time.get_ticks()
#                     elif self.action == 'jump':
#                         self.jumping = False
#                     self.frame_index = 0
#                 else:
#                     self.frame_index = 0

#         # Update image and collision data
#         self.current_image = self.get_frame(animation_key, self.frame_index)
#         self.current_mask = self.get_mask(animation_key, self.frame_index)
#         self.rect = self.current_image.get_rect()
#         self.rect.midbottom = (self.x, self.y)
#         self.hitbox = self.rect.inflate(-20, -20)
#         self.hitbox.midbottom = self.rect.midbottom

#     def toggle_shield(self, active=None):
#         if self.dead or self.attacking or self.using_ultimate:
#             return False

#         # Toggle or set specific state
#         if active is None:
#             active = not self.shielding

#         # Reset shield animation if turning on shield
#         if active and not self.shielding:
#             self.frame_index = 0
#             self.shield_frame_locked = False

#         # Reset lock when turning off shield
#         if not active:
#             self.shield_frame_locked = False

#         self.shielding = active
#         return True

#     def use_ultimate(self):
#         if self.ultimate_ready and not self.dead and not self.attacking:
#             self.using_ultimate = True
#             self.ultimate_ready = False
#             self.ultimate_charge = 0
#             self.frame_index = 0
#             return True
#         return False

#     def move(self, dx, dy):
#         if dx > 0:
#             self.direction = 'right'
#         elif dx < 0:
#             self.direction = 'left'

#         self.moving = dx != 0 or dy != 0
        
#          # Allow horizontal movement even while jumping
#         if self.jumping:
#             self.x += dx 
#             self.y += dy
#         else:
#             self.x += dx
#             self.y += dy
    
#     def attack(self, enemies):
#         if not self.attacking and not self.using_ultimate and not self.dead:
#             self.attacking = True
#             self.frame_index = 0  # Restart animation
    
#             # Check for enemy collisions
#             for enemy in enemies:
#                 if self.check_collision(enemy):  # Sword hits enemy
#                     enemy.take_damage(self.damage_amount)  
#                     print(f"Hit enemy! Enemy health: {enemy.health}")

#     def jump(self):
#         if not self.jumping and not self.dead:
#             self.jumping = True
#             self.frame_index = 0

#     def die(self):
#         if not self.dead:
#             self.dead = True
#             self.frame_index = 0

#     def reset(self):
#         self.dead = False
#         self.attacking = self.using_ultimate = self.moving = self.jumping = False
#         self.shielding = False
#         self.shield_frame_locked = False
#         self.frame_index = 0
#         self.action = 'idle'
#         self.health = self.max_health
#         self.invincible = self.hit_effect = False
#         self.ultimate_charge = 0
#         self.ultimate_ready = False
#         self.ultimate_last_used = pygame.time.get_ticks()
    
    
#     def take_damage(self, amount):
#         current_time = pygame.time.get_ticks()
    
#         # Add invincibility cooldown (e.g., 500ms)
#         if self.invincible and current_time - self.invincible_timer < 500:
#             return  
    
#         self.health -= amount
#         self.invincible = True
#         self.invincible_timer = current_time  
    
#         # Switch to hurt animation
#         self.action = "hurt"
#         self.frame_index = 0  # Restart animation
#         self.hurt_timer = current_time  # Track when the hurt animation started
    
#         print(f"Player took {amount} damage! Remaining HP: {self.health}")
    
#         if self.health <= 0:
#             self.die()
        
        

#     def draw(self, surface):
#         if self.hit_effect and not self.hit_visible:
#             # Draw white silhouette for hit effect
#             mask_outline = self.current_mask.to_surface(setcolor=(255, 255, 255, 220), unsetcolor=(0, 0, 0, 0))
#             surface.blit(mask_outline, self.rect)
#         else:
#             surface.blit(self.current_image, self.rect)

#         # Draw small health bar
#         self.draw_health_bar(surface)

#     def draw_health_bar(self, surface):
#         bar_width, bar_height = 40, 5
#         x = self.rect.centerx - bar_width // 2
#         y = self.rect.top - 10

#         # Background (red)
#         pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))

#         # Health fill (green)
#         if self.health > 0:
#             fill = (self.health / self.max_health) * bar_width
#             pygame.draw.rect(surface, (0, 255, 0), (x, y, int(fill), bar_height))

#         # Border
#         pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)

#     def draw_main_health_bar(self, surface, x, y, width=200, height=20):
#         # Background
#         pygame.draw.rect(surface, (100, 0, 0), (x, y, width, height))

#         # Health fill
#         if self.health > 0:
#             fill = (self.health / self.max_health) * width
#             pygame.draw.rect(surface, (0, 200, 0), (x, y, int(fill), height))

#         # Border and text
#         pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)
#         font = pygame.font.SysFont(None, 24)
#         text = font.render(f"{self.health}/{self.max_health} HP", True, (255, 255, 255))
#         text_rect = text.get_rect(center=(x + width//2, y + height//2))
#         surface.blit(text, text_rect)

#     def draw_ultimate_bar(self, surface, x, y, width=200, height=10):
#         # Background
#         pygame.draw.rect(surface, (50, 50, 100), (x, y, width, height))

#         # Charge fill
#         if self.ultimate_charge > 0:
#             fill = (self.ultimate_charge / 100) * width
#             color = (100, 100, 255) if not self.ultimate_ready else (200, 200, 255)
#             pygame.draw.rect(surface, color, (x, y, int(fill), height))

#         # Ready indicator
#         border_color = (255, 255, 100) if self.ultimate_ready else (0, 0, 0)
#         border_width = 2 if self.ultimate_ready else 1
#         pygame.draw.rect(surface, border_color, (x, y, width, height), border_width)

#         # Ready text
#         if self.ultimate_ready:
#             font = pygame.font.SysFont(None, 18)
#             text = font.render("Ultimate Ready (E)", True, (255, 255, 100))
#             surface.blit(text, (x + width + 5, y))

    
#     def check_collision(self, enemy):
#         # Get offset for mask-based collision
#         offset = (enemy.rect.x - self.rect.x, enemy.rect.y - self.rect.y)
    
#         # Check if attack animation overlaps with enemy’s mask
#         return self.current_mask.overlap(enemy.mask, offset) is not None


#     def can_deal_damage(self):
#         return (self.attacking or self.using_ultimate) and not self.dead

#     def get_damage_amount(self):
#         return self.ultimate_damage if self.using_ultimate else self.damage_amount


# class CharacterManager:
#     def __init__(self, standard_height=STANDARD_HEIGHT):
#         self.characters = {}
#         self.standard_height = standard_height

#     def add_character(self, character_id, x, y, character_type, height=None):
#         character = Character(x, y, character_type, height or self.standard_height)
#         self.characters[character_id] = character
#         return character

#     def set_frame_counts(self, character_id, frame_counts):
#         character = self.get_character(character_id)
#         if character:
#             for action, count in frame_counts.items():
#                 character.set_frame_count(action, count)
#             # character.load_animations(f'assets/{character.character_type}')
#             character.load_animations(os.path.join(os.path.dirname(__file__), f"../assets/images/player/{character.character_type}"))

#     def set_animation_speeds(self, character_id, speed_dict):
#         character = self.get_character(character_id)
#         if character:
#             for action, speed in speed_dict.items():
#                 character.set_animation_speed(action, speed)

#     def configure_ultimate(self, character_id, cooldown=5000, damage=30):
#         character = self.get_character(character_id)
#         if character:
#             character.ultimate_cooldown = cooldown
#             character.ultimate_damage = damage

#     def update_all(self):
#         for character in self.characters.values():
#             character.update()

#     def draw_all(self, surface):
#         # Sort characters by z-index for proper depth
#         for character in sorted(self.characters.values(), key=lambda c: c.z_index):
#             character.draw(surface)

#     def draw_controlled_ui(self, surface, controlled_id, x=20, y=20):
#         if controlled_id in self.characters:
#             char = self.characters[controlled_id]
#             char.draw_main_health_bar(surface, x, y, 200, 20)
#             char.draw_ultimate_bar(surface, x, y + 25, 200, 10)

#     def get_character(self, character_id):
#         return self.characters.get(character_id)

#     def check_all_collisions(self):
#         collisions = []
#         combat_results = []
#         char_ids = list(self.characters.keys())

#         for i in range(len(char_ids)):
#             for j in range(i + 1, len(char_ids)):
#                 char1_id, char2_id = char_ids[i], char_ids[j]
#                 char1, char2 = self.characters[char1_id], self.characters[char2_id]

#                 if char1.check_collision(char2):
#                     collisions.append((char1_id, char2_id))

#                     # Check char1 damaging char2
#                     if char1.can_deal_damage():
#                         damage = char1.get_damage_amount()
#                         if char2.take_damage(damage):
#                             combat_results.append((char1_id, char2_id, damage))

#                     # Check char2 damaging char1
#                     if char2.can_deal_damage():
#                         damage = char2.get_damage_amount()
#                         if char1.take_damage(damage):
#                             combat_results.append((char2_id, char1_id, damage))

#         return collisions, combat_results

#     def take_damage(self, amount):
#         self.health -= amount
#         if self.health < 0:
#             self.health = 0
#             self.state = "death"
#             self.is_dead = True
#         else:
#             # Briefly change to hurt animation
#             self.state = "hurt"
#             self.current_frame = 0

#     def take_damage(self, amount):
#         if self.shielding:
#             self.hit_effect = True
#             self.hit_effect_timer = pygame.time.get_ticks()
#             self.hit_visible = False
#             return False  # Damage was blocked

#         if not self.invincible and not self.dead:
#             self.health -= amount
#             print(f"Player took {amount} damage! Health now: {self.health}/{self.max_health}")

#             # Trigger invincibility and hit effect
#             self.invincible = True
#             self.invincible_timer = pygame.time.get_ticks()
#             self.hit_effect = True
#             self.hit_effect_timer = pygame.time.get_ticks()
#             self.hit_visible = False

#             if self.health <= 0:
#                 self.health = 0
#                 self.die()

#             return True
#         return False



# class Game:
#     def __init__(self, width=800, height=600):
#         pygame.init()
#         self.screen = pygame.display.set_mode((width, height))
#         pygame.display.set_caption("Character Demo")
#         self.clock = pygame.time.Clock()
#         self.running = True
#         self.width, self.height = width, height

#         # Game objects
#         self.character_manager = CharacterManager()
#         self.bg_color = (50, 50, 50)
#         self.font = pygame.font.SysFont(None, 24)

#         # Game state
#         self.controlled_character_id = "player"
#         self.show_collision_info = True
#         self.collisions = []
#         self.combat_messages = []
#         self.message_duration = 2000

#         # Setup characters
#         self.setup_characters()

#     def setup_characters(self):
#         # Add player character
#         self.player = self.character_manager.add_character(
#             "player", self.width // 2, self.height // 2, "Knight")
#         self.player.z_index = sys.maxsize

#         frame_counts = {
#             'idle': 15, 'move': 8, 'attack': 22,
#             'ultimate': 22, 'death': 15, 'jump': 14,
#             'shield': 7
#         }

#         # Configure player animations
#         self.character_manager.set_frame_counts("player", frame_counts)

#         # Configure animation speeds
#         self.character_manager.set_animation_speeds("player", {
#             'idle': 100, 'move': 80, 'attack': 100,
#             'ultimate': 50, 'death': 120, 'jump': 70,
#             'shield': 50
#         })

#         # Configure ultimate attack
#         self.character_manager.configure_ultimate("player", cooldown=5000, damage=30)

#         # Set custom damage for player
#         self.player.damage_amount = 15

#         # Add enemy for testing
#         self.character_manager.add_character(
#             "enemy", self.width // 2 + 100, self.height // 2, "Knight")

#         # Configure enemy animations
#         self.character_manager.set_frame_counts("enemy", frame_counts)

#         # Configure enemy ultimate
#         self.character_manager.configure_ultimate("enemy", cooldown=7000, damage=20)

#     def handle_events(self):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 self.running = False

#             # Key press events
#             if event.type == pygame.KEYDOWN:
#                 controlled_char = self.character_manager.get_character(self.controlled_character_id)
#                 if controlled_char:
#                     if event.key == pygame.K_q:  # Regular attack
#                         controlled_char.attack()
#                     elif event.key == pygame.K_e:  # Ultimate attack
#                         if controlled_char.use_ultimate():
#                             self.combat_messages.append((
#                                 f"{self.controlled_character_id} used ultimate attack!",
#                                 pygame.time.get_ticks()
#                             ))
#                     elif event.key == pygame.K_f:  # Shield key
#                         controlled_char.toggle_shield(True)
#                     elif event.key == pygame.K_SPACE:
#                         controlled_char.jump()
#                     elif event.key == pygame.K_r:
#                         controlled_char.reset()
#                     elif event.key == pygame.K_x:
#                         controlled_char.die()
#                     elif event.key == pygame.K_TAB:
#                         # Switch controlled character
#                         char_ids = list(self.character_manager.characters.keys())
#                         current_idx = char_ids.index(self.controlled_character_id)
#                         next_idx = (current_idx + 1) % len(char_ids)
#                         self.controlled_character_id = char_ids[next_idx]
#                     elif event.key == pygame.K_c:
#                         # Toggle collision info
#                         self.show_collision_info = not self.show_collision_info
#                     elif event.key == pygame.K_h:
#                         # Self-damage for testing
#                         controlled_char.take_damage(10)
#             if event.type == pygame.KEYUP:
#                 controlled_char = self.character_manager.get_character(self.controlled_character_id)
#                 if controlled_char and event.key == pygame.K_f:  # Shield key released
#                     controlled_char.toggle_shield(False)

#     def update(self):
#         current_time = pygame.time.get_ticks()

#         # Handle movement
#         keys = pygame.key.get_pressed()
#         controlled_char = self.character_manager.get_character(self.controlled_character_id)

#         if controlled_char and not controlled_char.dead:
#             dx, dy = 0, 0

#             if keys[pygame.K_a]: dx = -controlled_char.speed  # Left
#             if keys[pygame.K_d]: dx = controlled_char.speed   # Right
#             if keys[pygame.K_w]: dy = -controlled_char.speed  # Up
#             if keys[pygame.K_s]: dy = controlled_char.speed   # Down

#             # Move character with bounds
#             controlled_char.move(dx, dy)
#             controlled_char.x = max(0, min(controlled_char.x, self.width))
#             controlled_char.y = max(50, min(controlled_char.y, self.height))

#         # Update all characters
#         self.character_manager.update_all()

#         # Check for collisions and combat
#         self.collisions, new_combat_results = self.character_manager.check_all_collisions()

#         # Add new combat messages
#         for attacker, defender, damage in new_combat_results:
#             char = self.character_manager.get_character(attacker)
#             is_ultimate = char and char.using_ultimate

#             message = f"{attacker} hit {defender} for {damage} damage!"
#             if is_ultimate:
#                 message = f"ULTIMATE: {message}"

#             self.combat_messages.append((message, current_time))

#         # Update combat message timers
#         self.combat_messages = [(msg, time) for msg, time in self.combat_messages
#                                if current_time - time < self.message_duration]

#     def render(self):
#         # Clear screen
#         self.screen.fill(self.bg_color)

#         # Draw characters
#         self.character_manager.draw_all(self.screen)

#         # Draw controlled character UI
#         self.character_manager.draw_controlled_ui(self.screen, self.controlled_character_id, 20, 20)

#         # Display which character is being controlled
#         text = self.font.render(f"Controlling: {self.controlled_character_id} (TAB to switch)", True, (255, 255, 255))
#         self.screen.blit(text, (20, 60))

#         # Display controls
#         controls = [
#             "Controls:", "WASD: Move", "SPACE: Jump",
#             "Q: Attack", "E: Ultimate", "F: Shield", "X: Die",
#             "R: Reset", "H: Test damage"
#         ]
#         for i, line in enumerate(controls):
#             text = self.font.render(line, True, (200, 200, 200))
#             self.screen.blit(text, (10, 90 + i * 20))

#         # Display collision info
#         y_offset = self.height - 30
#         if self.show_collision_info and self.collisions:
#             collision_text = "Collisions: " + ", ".join([f"{c1} & {c2}" for c1, c2 in self.collisions])
#             text = self.font.render(collision_text, True, (255, 200, 100))
#             self.screen.blit(text, (10, y_offset - 20))

#         # Display combat messages
#         for i, (message, _) in enumerate(reversed(self.combat_messages)):
#             text = self.font.render(message, True, (255, 100, 100))
#             self.screen.blit(text, (10, y_offset - (i+1) * 20))

#         # Display character health (except for controlled character)
#         for i, (char_id, character) in enumerate(self.character_manager.characters.items()):
#             if char_id != self.controlled_character_id:
#                 health_text = f"{char_id}: {character.health}/{character.max_health} HP"
#                 color = (100, 255, 100) if character.health > 30 else (255, 100, 100)
#                 text = self.font.render(health_text, True, color)
#                 self.screen.blit(text, (self.width - 200, 30 + i * 20))

#         # Update display
#         pygame.display.flip()

#     def run(self):
#         while self.running:
#             self.handle_events()
#             self.update()
#             self.render()
#             self.clock.tick(60)  # 60 FPS

#         pygame.quit()

# if __name__ == "__main__":
#     game = Game()
#     game.run()
