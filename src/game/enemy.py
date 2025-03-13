import pygame
import os
import math
import random

# Load Images Function
def load_image(filename, scale=1.0, flip=False):
    """Loads a single image with optional scaling and flipping."""
    try:
        filepath = os.path.join("src", "assets", "images", filename)
        image = pygame.image.load(filepath).convert_alpha()

        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)

        if flip:
            image = pygame.transform.flip(image, True, False)

        return image
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        placeholder = pygame.Surface((64, 64))
        placeholder.fill((100, 0, 100))
        return placeholder

# Load Animations Function
def load_animation(base_filename, file_type, num_frames, scale=1.0, flip=False):
    """Loads multiple frames for an animation sequence with optional flipping."""
    return [load_image(f"{base_filename}_{i+1}.{file_type}", scale, flip) for i in range(num_frames)]

# Load animations dynamically for all mobs
def load_mob_animations(mob_name, scale=0.6):
    return {
        "idle": load_animation(f"enemies/level1/{mob_name}_Idle", "png", 4, scale),
        "walk_left": load_animation(f"enemies/level1/{mob_name}_Walk", "png", 6, scale),
        "walk_right": load_animation(f"enemies/level1/{mob_name}_Walk", "png", 6, scale, flip=True),
        # Add directional attack animations
        "att1_left": load_animation(f"enemies/level1/{mob_name}_Att1", "png", 4, scale),
        "att1_right": load_animation(f"enemies/level1/{mob_name}_Att1", "png", 4, scale, flip=True),
        "att2_left": load_animation(f"enemies/level1/{mob_name}_Att2", "png", 4, scale),
        "att2_right": load_animation(f"enemies/level1/{mob_name}_Att2", "png", 4, scale, flip=True),
        "att3_left": load_animation(f"enemies/level1/{mob_name}_Att3", "png", 4, scale),
        "att3_right": load_animation(f"enemies/level1/{mob_name}_Att3", "png", 4, scale, flip=True),
        # Conditional for att4 with directional versions
        "att4_left": load_animation(f"enemies/level1/{mob_name}_Att4", "png", 4, scale) if "Att4" in mob_name else None,
        "att4_right": load_animation(f"enemies/level1/{mob_name}_Att4", "png", 4, scale, flip=True) if "Att4" in mob_name else None,
        # Keep normal hurt and death animations
        "hurt": load_animation(f"enemies/level1/{mob_name}_Hurt", "png", 4, scale),
        "death": load_animation(f"enemies/level1/{mob_name}_Death", "png", 4, scale),
    }

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, is_in_hallway_func, health=100):
        super().__init__()
        self.animations = animations
        self.is_in_hallway = is_in_hallway_func  # Store the function reference
        self.state = "idle"
        self.current_frame = 0
        self.image = self.animations[self.state][self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        

        self.frame_timer = 0
        self.frame_delay = 120  
        self.direction = "left"
        self.speed = 2
        self.move_timer = 0
        self.move_duration = 2000  
        self.idle_duration = 1000  
        self.is_moving = True

        self.health = health
        self.max_health = health
        self.show_healthbar = False
        
        # New attributes for player detection and attack
        self.detection_radius = 200  # Detection radius in pixels
        self.attack_radius = 50     # Distance at which enemy can attack
        self.is_chasing = False     # Track if enemy is chasing player
        self.attack_cooldown = 1000 # Milliseconds between attacks
        self.attack_timer = 0       # Current attack cooldown timer
        self.is_attacking = False   # Track if enemy is attacking
        self.damage = 10            # Damage to deal to player
        self.original_x = x         # Store original position for patrol behavior
        self.original_y = y


    def update(self, dt, player=None):
        """Updates the enemy state, animations, and movement within hallways."""
        # Update timers
        self.frame_timer += dt
        self.move_timer += dt
        
        # Update attack cooldown - IMPORTANT for continuous attacks
        if self.attack_timer > 0:
            self.attack_timer -= dt
            # Debug output for attack cooldown
            # print(f"Attack cooldown: {self.attack_timer}")
        
        # ANIMATION FRAME HANDLING
        if self.frame_timer > self.frame_delay:
            self.frame_timer = 0
            
            # Handle death animation (priority 1) - must complete fully
            if self.state == "death":
                if self.current_frame < len(self.animations["death"]) - 1:
                    self.current_frame += 1
                else:
                    self.kill()  # Remove the enemy when animation completes
                    return
            
            # Handle hurt animation (priority 2) - must complete fully
            elif self.state == "hurt":
                if self.current_frame < len(self.animations["hurt"]) - 1:
                    self.current_frame += 1
                else:
                    # Return to previous state after hurt animation completes
                    self.state = "idle"  # Default to idle
                    self.current_frame = 0
                    self.hurt_recovery_timer = 300  # Add a brief recovery period
            
            # Handle attack animations (priority 3)
            elif self.state.startswith("att"):
                if self.current_frame < len(self.animations[self.state]) - 1:
                    self.current_frame += 1
                else:
                    # FIXED: Reset from attack state properly
                    self.current_frame = 0
                    self.is_attacking = False  # No longer attacking
                    # Don't reset attack_timer here - it should count down independently
                    
                    # Return to appropriate movement state
                    if self.is_chasing:
                        self.state = f"walk_{self.direction}"
                    else:
                        self.state = "idle"
            
            # Handle normal animations (lowest priority)
            else:
                if self.state in self.animations:
                    self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            
            # Update enemy sprite image and mask
            if self.state in self.animations:
                self.image = self.animations[self.state][self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)
        
        # If enemy is in hurt or death state, don't process movement or AI
        if self.state in ["hurt", "death"]:
            return
        
        # If enemy has a hurt recovery timer, reduce it
        if hasattr(self, 'hurt_recovery_timer') and self.hurt_recovery_timer > 0:
            self.hurt_recovery_timer -= dt
            return
        
        # PLAYER DETECTION AND CHASING LOGIC
        if player is not None:
            # Calculate distance to player
            dist_to_player = math.sqrt((self.rect.centerx - player.x)**2 + 
                                       (self.rect.centery - player.y)**2)
        
            # Check if player is within detection radius
            if dist_to_player <= self.detection_radius:
                self.is_chasing = True
        
        
                player_rel_x = player.x - self.rect.centerx
                player_rel_y = player.y - (self.rect.bottom + 30)  # Same +30 offset as movement
                adjusted_dist = math.sqrt(player_rel_x**2 + player_rel_y**2)               
                
                # Only attack if not already attacking AND attack cooldown is complete
                if (adjusted_dist <= self.attack_radius and 
                    not self.is_attacking and 
                    self.attack_timer <= 0):
                    
                    # Choose random attack animation
                    attack_num = random.randint(1, 3)
                    attack_dir = "_right" if player.x > self.rect.centerx else "_left"
                    attack_state = f"att{attack_num}{attack_dir}"
                    
                    # Make sure animation exists
                    if attack_state in self.animations and self.animations[attack_state] is not None:
                        self.state = attack_state
                    else:
                        # Fallback to default attack animation
                        self.state = f"att1{attack_dir}"
                    
                    # Begin attack
                    self.direction = "right" if player.x > self.rect.centerx else "left"
                    self.current_frame = 0
                    self.is_attacking = True
                    self.attack_timer = self.attack_cooldown  # Set cooldown timer
                    # Debug output
                    # print(f"Enemy attacking! State: {self.state}, Cooldown: {self.attack_timer}")
                    
                    return  # Stop movement during attack initiation
                
                # MOVEMENT LOGIC - Update direction based on player position
                if not self.is_attacking:  # Only change direction if not attacking
                    if player.x < self.rect.centerx:
                        self.direction = "left"
                        self.state = "walk_left"
                    else:
                        self.direction = "right"
                        self.state = "walk_right"
                
                # Only move if not attacking
                if not self.is_attacking:
                    # Calculate movement towards player
                    dx = self.speed if player.x > (self.rect.centerx+10) else -self.speed if player.x < (self.rect.centerx-10) else 0
                    dy = self.speed if player.y > (self.rect.bottom+30) else -self.speed if player.y < (self.rect.bottom+30) else 0
        
                    # Normalize diagonal movement
                    if dx != 0 and dy != 0:
                        magnitude = math.sqrt(dx**2 + dy**2)
                        dx = (dx / magnitude) * self.speed
                        dy = (dy / magnitude) * self.speed
        
                    # Calculate the next position
                    next_x = self.rect.x + dx
                    next_y = self.rect.y + dy
        
                    # Check if next move is inside hallway bounds
                    if self.is_in_hallway(next_x, next_y):
                        self.rect.x = next_x
                        self.rect.y = next_y
            else:
                # Player out of detection range
                self.is_chasing = False
        
        # PATROL BEHAVIOR - Used when not chasing the player
        if not self.is_chasing:
            # Calculate the next position
            next_x = self.rect.x - self.speed if self.direction == "left" else self.rect.x + self.speed
            next_y = self.rect.y  
    
            # Check if next move is inside hallway bounds
            if self.is_moving and self.is_in_hallway(next_x, next_y):
                self.rect.x = next_x
                self.state = "walk_left" if self.direction == "left" else "walk_right"
            else:
                # Change direction if out of bounds
                self.direction = "right" if self.direction == "left" else "left"
                self.move_timer = 0  # Restart move duration
                self.state = "idle"
    
            if self.move_timer > self.move_duration:
                self.is_moving = False
                self.state = "idle"
                self.move_timer = 0
            elif self.move_timer > self.idle_duration:
                self.is_moving = True
                self.move_timer = 0
    
        # Always update health bar visibility
        if self.health < self.max_health:
            self.show_healthbar = True


    def take_damage(self, amount):
        # Only process damage if not already in hurt or death animation
        if self.state not in ["hurt", "hurt_still", "death"]:
            self.current_frame = 0
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.show_healthbar = True
            
            # Set appropriate animation state
            if self.health <= 0:
                self.state = "death"
            else:
                self.state = "hurt"
                
                
            # Immediately update the image
            self.image = self.animations[self.state][self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)


        

    def can_attack(self):
        """Check if the enemy can currently attack"""
        # Updated to check for both att_left and att_right patterns
        return (self.is_attacking and 
                self.attack_timer > 0 and 
                self.state.startswith("att") and
                self.current_frame >= 1)  # Only deal damage on certain frames
                
    # 2. Adjust the attack range and detection
        self.detection_radius = 200  # Detection radius in pixels
        self.attack_radius = 80     # Increased attack radius to make it easier to hit the player
        self.damage = 15            # Increased damage to make attacks more noticeable

        # 3. Update the update method to improve attack behavior
        if self.is_chasing and dist_to_player <= self.attack_radius and not self.is_attacking and self.attack_timer <= 0:

            # Choose a random attack animation (1-3)
            attack_num = random.randint(1, 3)
            
            # Set attack state based on player's position
            attack_dir = "_right" if player.x > self.rect.centerx else "_left"
            attack_anim = f"att{attack_num}{attack_dir}"
            
            # Make sure the animation exists
            if attack_anim in self.animations and self.animations[attack_anim] is not None:
                self.state = attack_anim
            else:
                # Fallback to att1 if specific attack not available
                self.state = f"att1{attack_dir}"
                
            self.current_frame = 0  # Reset animation frame
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            
            # Add debug print to confirm attack
            print(f"Enemy attacking player! Attack state: {self.state}")
            return
        
    def get_damage(self):
        """Return the damage this enemy deals"""
        return self.damage

    def draw_healthbar(self, screen):
        bar_width = 50
        bar_height = 5
        fill = (self.health / 100) * bar_width  # Scale health bar
    
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
    
        pygame.draw.rect(screen, (255, 0, 0), outline_rect)  # Red outline
        pygame.draw.rect(screen, (0, 255, 0), fill_rect)  # Green health




# Load Golem Animations
def load_golem_animations(scale=0.8, flip=False):
    return {
        "idle": load_animation("enemies/level2/Golem1_idle", "png", 6, scale, flip),
        "walk": load_animation("enemies/level2/Golem1_walk", "png", 8, scale, flip),
        "run_attack": load_animation("enemies/level2/Golem1_runatt", "png", 7, scale, flip),
        "attack1": load_animation("enemies/level2/golem1_att1", "png", 6, scale, flip),
        "attack2": load_animation("enemies/level2/golem1_att2", "png", 7, scale, flip),
        "attack3": load_animation("enemies/level2/golem1_att3", "png", 4, scale, flip),
        "hurt": load_animation("enemies/level2/golem1_hurt", "png", 4, scale, flip),
        "death": load_animation("enemies/level2/golem1_dead", "png", 6, scale, flip),
    }


# Add this to the enemy.py file

class Golem(Enemy):
    def __init__(self, x, y, is_in_hallway_func, health=200):
        # Load animations specifically for golem
        animations = {
            "idle": load_animation("enemies/level2/Golem1_idle", "png", 6, 0.8),
            "walk_left": load_animation("enemies/level2/Golem1_walk", "png", 8, 0.8, flip=True),
            "walk_right": load_animation("enemies/level2/Golem1_walk", "png", 8, 0.8),
            # Attack animations with directional versions
            "att1_left": load_animation("enemies/level2/golem1_att1", "png", 6, 0.8, flip=True),
            "att1_right": load_animation("enemies/level2/golem1_att1", "png", 6, 0.8),
            "att2_left": load_animation("enemies/level2/golem1_att2", "png", 7, 0.8, flip=True),
            "att2_right": load_animation("enemies/level2/golem1_att2", "png", 7, 0.8),
            "att3_left": load_animation("enemies/level2/golem1_att3", "png", 4, 0.8, flip=True),
            "att3_right": load_animation("enemies/level2/golem1_att3", "png", 4, 0.8),
            # Special run attack animation
            "runatt_left": load_animation("enemies/level2/Golem1_runatt", "png", 7, 0.8, flip=True),
            "runatt_right": load_animation("enemies/level2/Golem1_runatt", "png", 7, 0.8),
            # Hurt and death animations
            "hurt": load_animation("enemies/level2/golem1_hurt", "png", 4, 0.8),
            "death": load_animation("enemies/level2/golem1_dead", "png", 6, 0.8),
        }
        
        # Initialize parent class with golem-specific parameters
        super().__init__(x, y, animations, is_in_hallway_func, health)
        
        # Golem-specific attributes - higher damage, slower but with more health
        self.speed = 1.5  # Slower movement
        self.damage = 25  # Higher damage
        self.detection_radius = 250  # Larger detection radius
        self.attack_radius = 70  # Slightly larger attack radius
        self.attack_cooldown = 1500  # Longer cooldown between attacks
        self.charge_speed = 4  # Special charge attack speed
        self.is_charging = False
        self.charge_cooldown = 5000  # Time between charges (ms)
        self.charge_timer = 0
        
    def update(self, dt, player=None):
        # Update charge timer
        if self.charge_timer > 0:
            self.charge_timer -= dt
            
        # Call the parent update method for basic behavior
        super().update(dt, player)
        
        # Add golem-specific behavior for charging attack
        if player is not None and not self.is_attacking and self.state not in ["hurt", "death"]:
            dist_to_player = math.sqrt((self.rect.centerx - player.x)**2 + 
                                      (self.rect.centery - player.y)**2)
            
            # Check if we should initiate a charge attack
            if (dist_to_player <= self.detection_radius and 
                dist_to_player > self.attack_radius and 
                self.charge_timer <= 0 and
                not self.is_charging):
                
                # 20% chance to initiate charge when conditions are met
                if random.random() < 0.2:
                    self.is_charging = True
                    self.charge_timer = self.charge_cooldown
                    
                    # Set direction for charge attack
                    if player.x < self.rect.centerx:
                        self.direction = "left"
                        self.state = "runatt_left"
                    else:
                        self.direction = "right"
                        self.state = "runatt_right"
                    
                    self.current_frame = 0
                    
            # Handle charging movement
            if self.is_charging:
                # Move faster during charge
                charge_dx = self.charge_speed * (-1 if self.direction == "left" else 1)
                
                # Check if next position is valid
                next_x = self.rect.x + charge_dx
                
                if self.is_in_hallway(next_x, self.rect.y):
                    self.rect.x = next_x
                    
                    # Check if we've reached the player during charge
                    if (dist_to_player <= self.attack_radius):
                        # End charge with an attack
                        attack_dir = "_left" if self.direction == "left" else "_right"
                        self.state = f"att2{attack_dir}"  # Use stronger attack after charge
                        self.current_frame = 0
                        self.is_attacking = True
                        self.is_charging = False
                        self.attack_timer = self.attack_cooldown
                else:
                    # Hit a wall, end charge
                    self.is_charging = False
                    self.state = "idle"
                    
                # End charge after full animation cycle
                if self.current_frame >= len(self.animations[self.state]) - 1:
                    self.is_charging = False
                    
    def can_attack(self):
        """Check if the golem can currently attack including during charge"""
        regular_attack = super().can_attack()
        charge_attack = (self.is_charging and 
                        self.state.startswith("runatt") and 
                        self.current_frame >= 3)  # Only deal charge damage on certain frames
                        
        return regular_attack or charge_attack
        
    def get_damage(self):
        """Return damage based on attack type"""
        if self.state.startswith("runatt"):
            return self.damage * 1.5  # Charge attacks do more damage
        elif self.state.startswith("att2"):
            return self.damage * 1.2  # Heavy attack does more damage
        else:
            return self.damage