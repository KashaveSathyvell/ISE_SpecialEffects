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
def load_animation(base_filename, file_type, num_frames, scale=1.0, flip=False, underscore = True):
    """Loads multiple frames for an animation sequence with optional flipping."""
    if underscore:
        return [load_image(f"{base_filename}_{i+1}.{file_type}", scale, flip) for i in range(num_frames)]
    else:
        return [load_image(f"{base_filename}{i+1}.{file_type}", scale, flip) for i in range(num_frames)]
    
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
    def __init__(self, x, y, animations, is_in_hallway_func, health=70):
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
            
            elif self.state == "hurt":
                if self.current_frame < len(self.animations["hurt"]) - 1:
                    self.current_frame += 1
                else:
                    self.state = self.previous_state if hasattr(self, "previous_state") else "idle"
                    self.current_frame = 0
                    self.hurt_recovery_timer = 300


            
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
        if self.state not in ["hurt", "death"]:
            self.current_frame = 0
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.show_healthbar = True
            
            if self.health <= 0:
                self.state = "death"
            else:
                self.previous_state = self.state  # Store the previous state before hurt
                self.state = "hurt"
            
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
            return
        
    def get_damage(self):
        """Return the damage this enemy deals"""
        return self.damage


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


# Golem Class
class Golem(Enemy):
    def __init__(self, x, y, is_in_hallway_func, health=120):
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
            
        # Update timers
        self.frame_timer += dt
        
        # ANIMATION FRAME HANDLING - Handle priority animations first
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
                    # Restore previous state after hurt animation
                    self.state = self.previous_state if hasattr(self, "previous_state") else "idle"
                    self.current_frame = 0
                    self.hurt_recovery_timer = 300  # Add a brief recovery period
            
            # For other animations, call the parent class update
            else:
                # Call the parent update method for basic behavior
                super().update(dt, player)
                return
                
            # Update enemy sprite image and mask
            if self.state in self.animations:
                self.image = self.animations[self.state][self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)
            
            # If enemy is in hurt or death state, don't process movement or AI
            if self.state in ["hurt", "death"]:
                return
        
        # Only handle special golem behavior if we're not in a priority animation
        if self.state not in ["hurt", "death"]:
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
                    
    def take_damage(self, amount):
        if self.state not in ["hurt", "death"]:
            self.current_frame = 0
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.show_healthbar = True
            
            if self.health <= 0:
                self.state = "death"
            else:
                self.previous_state = self.state  # Store the previous state before hurt
                self.state = "hurt"
            
            self.image = self.animations[self.state][self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)
        
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


class Boss2(Enemy):
    def __init__(self, x, y, is_in_hallway_func, health=30):
        # Load animations specifically for Boss2
        animations = {
            "idle": load_animation("enemies/level2/boss_idle", "png", 3, 1.0),
            "walk_left": load_animation("enemies/level2/boss_walk", "png", 6, 1.0, flip=True),
            "walk_right": load_animation("enemies/level2/boss_walk", "png", 6, 1.0),
            
            # Basic attack with directional versions
            "att1_left": load_animation("enemies/level2/boss_att", "png", 7, 1.0, flip=True),
            "att1_right": load_animation("enemies/level2/boss_att", "png", 7, 1.0),
            
            # Special ice attack with directional versions
            "ice_att_left": load_animation("enemies/level2/boss_IceAtt", "png", 5, 1.0, flip=True),
            "ice_att_right": load_animation("enemies/level2/boss_IceAtt", "png", 5, 1.0),
            
            # Special lightning attack with directional versions
            "lightning_att_left": load_animation("enemies/level2/boss_lightningAtt", "png", 5, 1.0, flip=True),
            "lightning_att_right": load_animation("enemies/level2/boss_lightningAtt", "png", 5, 1.0),
            
            # Angry state (might be used when health below certain threshold)
            "angry_left": load_animation("enemies/level2/boss_angry", "png", 5, 1.0, flip=True),
            "angry_right": load_animation("enemies/level2/boss_angry", "png", 5, 1.0),
            
            # Death animation
            "death": load_animation("enemies/level2/boss_death", "png", 6, 1.0),
            
            # Since there's no explicit hurt animation, we'll reuse the angry animation for hurt
            "hurt": load_animation("enemies/level2/boss_angry", "png", 5, 1.0),
        }
        
        # Projectile animations for special attacks
        self.projectile_animations = {
            "ice_projectile": load_animation("enemies/level2/boss_IceAtt_att", "png", 6, 1.0, False, False),
            "lightning_projectile": load_animation("enemies/level2/boss_lightningAtt_att", "png", 10, 1.0, False, False)
        }
        
        # Initialize parent class with boss-specific parameters
        super().__init__(x, y, animations, is_in_hallway_func, health)
        
        # Boss-specific attributes
        self.speed = 1.5  # movement speed
        self.damage = 35  # Higher damage
        self.detection_radius = 500  # Larger detection radius
        self.attack_radius = 100  # Larger attack radius
        self.attack_cooldown = 2000  # Longer cooldown between attacks
        
        # Special attack attributes
        self.special_attack_cooldown = 8000  # Time between special attacks (ms)
        self.special_attack_timer = 0  # Current special attack cooldown timer
        self.is_charging_special = False  # Wether boss is preparing a special attack
        self.projectiles = []  # List to store active projectiles
        
        # Projectile range limits
        self.projectile_max_distance = 300  # Maximum distance projectiles can travel
        self.ranged_attack_min_distance = 100  # Minimum distance for ranged attacks
        self.ranged_attack_max_distance = 200  # Preferred distance for ranged attacks
        
        # Boss phases
        self.max_health = health
        self.last_health_threshold = health  # Store last health checkpoint for anger transition
        self.is_invincible = False  # Boss is not invincible by default
        self.dead = False

        self.phase = 1  # Boss starts in phase 1
        self.phase_threshold = 0.5  # Boss enters phase 2 at 50% health
        self.is_angry = False  # Track if boss is in angry state
        self.angry_timer = 0  # Timer for angry state
        self.angry_duration = 3000  # Duration of angry state in ms
    
    def update(self, dt, player=None):
        """Update boss state, animations, movement, and attacks."""
        
        # Update special attack cooldown
        if self.special_attack_timer > 0:
            self.special_attack_timer -= dt
    
        # Handle angry state timer
        if self.angry_timer > 0:
            self.angry_timer -= dt
            if self.angry_timer <= 0:
                self.is_angry = False
                self.is_invincible = False  # Boss is vulnerable again
                self.speed /= 1.3  # Reset speed
                self.damage /= 1.5  # Reset damage
                self.attack_cooldown /= 0.8  # Reset attack cooldown
                self.special_attack_cooldown /= 0.7  # Reset special cooldown
                self.attack_timer = 0  
                self.is_attacking = False
                
                # Ensure boss resumes proper behavior
                if player is not None:
                    dist_to_player = math.sqrt((self.rect.centerx - player.x) ** 2 + (self.rect.centery - player.y) ** 2)
    
                    # Resume attack if player is still in range
                    if dist_to_player <= self.attack_radius:
                        attack_dir = "_right" if player.x > self.rect.centerx else "_left"
                        self.state = f"att1{attack_dir}"
                        self.is_attacking = True
                        self.attack_timer = self.attack_cooldown
                    elif dist_to_player <= self.detection_radius:
                        self.is_chasing = True
                        self.state = f"walk_{self.direction}"
                    else:
                        self.state = "idle"
        
        # Check for phase change
        current_health_percentage = self.health / self.max_health
        if current_health_percentage <= self.phase_threshold and self.phase == 1:
            self.phase = 2  # Fixed bug: was calling update_projectiles instead of setting phase
    
        # Update projectiles
        self.update_projectiles(dt, player)
    
        # Update frame timer for animations
        self.frame_timer += dt
    
        # Handle animations
        if self.frame_timer > self.frame_delay:
            self.frame_timer = 0
    
            # Death animation
            if self.state == "death":
                if self.current_frame < len(self.animations["death"]) - 1:
                    self.current_frame += 1
                else:
                    self.kill()
                    self.dead = True
                    return
    
            # Hurt animation
            elif self.state == "hurt":
                if self.current_frame < len(self.animations["hurt"]) - 1:
                    self.current_frame += 1
                else:
                    self.state = f"angry_{self.direction}" if self.is_angry else "idle"
                    self.current_frame = 0
                    self.hurt_recovery_timer = 300
    
            # Special attack animations
            elif self.state.startswith("ice_att") or self.state.startswith("lightning_att"):
                if self.current_frame < len(self.animations[self.state]) - 1:
                    self.current_frame += 1
                else:
                    self.fire_projectile(self.state, player)
                    self.current_frame = 0
                    self.is_attacking = False
                    self.is_charging_special = False
                    self.state = f"angry_{self.direction}" if self.is_angry else (
                        f"walk_{self.direction}" if self.is_chasing else "idle"
                    )
    
            # Regular attack animations
            elif self.state.startswith("att"):
                if self.current_frame < len(self.animations[self.state]) - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
                    self.is_attacking = False
                    self.state = f"angry_{self.direction}" if self.is_angry else (
                        f"walk_{self.direction}" if self.is_chasing else "idle"
                    )
    
            # Angry animation
            elif self.state.startswith("angry"):
                if self.current_frame < len(self.animations[self.state]) - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
                    if not self.is_angry:
                        self.is_invincible = False  # End invincibility
                        self.state = f"walk_{self.direction}" if self.is_chasing else "idle"
    
            # Normal movement animations
            else:
                if self.state in self.animations:
                    self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
    
            # Update sprite image and mask
            if self.state in self.animations:
                self.image = self.animations[self.state][self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)
    
        # Stop movement and AI if boss is in hurt or death state
        if self.state in ["hurt", "death"]:
            return
    
        # Handle hurt recovery timer
        if hasattr(self, "hurt_recovery_timer") and self.hurt_recovery_timer > 0:
            self.hurt_recovery_timer -= dt
            return
    
        # Player detection and AI
        if player is not None:
            dist_to_player = math.sqrt((self.rect.centerx - player.x) ** 2 + (self.rect.centery - player.y) ** 2)
    
            # Detect player and set chase state
            if dist_to_player <= self.detection_radius:
                self.is_chasing = True
    
                # Update movement direction
                if not self.is_attacking and not self.is_charging_special:
                    if player.x < self.rect.centerx:
                        self.direction = "left"
                        self.state = f"angry_left" if self.is_angry else "walk_left"
                    else:
                        self.direction = "right"
                        self.state = f"angry_right" if self.is_angry else "walk_right"
    
                # Special attack decision - IMPROVED RANGED ATTACK LOGIC
                # Prefer ranged attacks when player is at medium distance
                if (
                    dist_to_player >= self.ranged_attack_min_distance
                    and dist_to_player <= self.ranged_attack_max_distance
                    and self.special_attack_timer <= 0
                    and not self.is_attacking
                    and not self.is_charging_special
                    and not self.is_angry
                ):
                    # Higher chance of ranged attack when player is at optimal distance
                    special_chance = 0.6 if self.phase == 2 else 0.4
                    if random.random() < special_chance:
                        self.perform_special_attack(player)
                        return
                # Lower chance of ranged attack at other distances within detection range
                elif (
                    dist_to_player > self.attack_radius
                    and self.special_attack_timer <= 0
                    and not self.is_attacking
                    and not self.is_charging_special
                    and not self.is_angry
                ):
                    special_chance = 0.3 if self.phase == 2 else 0.15
                    if random.random() < special_chance:
                        self.perform_special_attack(player)
                        return
    
                # Regular attack decision
                if (
                    dist_to_player <= self.attack_radius
                    and not self.is_attacking
                    and not self.is_charging_special
                    and (not self.is_angry or self.angry_timer <= 0)
                    and self.attack_timer <= 0
                ):
                    attack_dir = "_right" if player.x > self.rect.centerx else "_left"
                    self.state = f"att1{attack_dir}"
                    self.is_attacking = True
                    self.attack_timer = self.attack_cooldown
                    return
    
                # Movement towards player
                if not self.is_attacking and not self.is_charging_special:
                    dx = self.speed if player.x > (self.rect.centerx + 10) else -self.speed if player.x < (self.rect.centerx - 10) else 0
                    dy = self.speed if player.y > (self.rect.bottom + 30) else -self.speed if player.y < (self.rect.bottom + 30) else 0
    
                    # Normalize diagonal movement
                    if dx != 0 and dy != 0:
                        magnitude = math.sqrt(dx**2 + dy**2)
                        dx = (dx / magnitude) * self.speed
                        dy = (dy / magnitude) * self.speed
    
                    # Calculate new position
                    next_x = self.rect.x + dx
                    next_y = self.rect.y + dy
    
                    # Check if move is valid
                    if self.is_in_hallway(next_x, next_y):
                        self.rect.x = next_x
                        self.rect.y = next_y
            else:
                self.is_chasing = False
                if not self.is_attacking and not self.is_charging_special:
                    self.state = f"angry_right" if self.is_angry else "idle"
    
        # Update health bar visibility
        if self.health < self.max_health:
            self.show_healthbar = True

    
    def perform_special_attack(self, player):
        """Initiate a special attack based on phase and randomness"""
        self.is_charging_special = True
        self.special_attack_timer = self.special_attack_cooldown
        
        # Choose attack type based on phase
        if self.phase == 2:
            attack_types = ["ice", "lightning"]
            weights = [0.5, 0.5]  # Equal chance in phase 2
        else:
            attack_types = ["ice", "lightning"]
            weights = [0.7, 0.3]  # Ice more common in phase 1
            
        attack_type = random.choices(attack_types, weights=weights, k=1)[0]
        attack_dir = "_right" if player.x > self.rect.centerx else "_left"
        
        # Set appropriate attack state
        self.state = f"{attack_type}_att{attack_dir}"
        self.direction = "right" if player.x > self.rect.centerx else "left"
        self.current_frame = 0
    
    def fire_projectile(self, attack_state, player):
        """Create a projectile after special attack animation completes"""
        if "ice_att" in attack_state:
            projectile_type = "ice_projectile"
            speed = 5
            damage = 25
        elif "lightning_att" in attack_state:
            projectile_type = "lightning_projectile"
            speed = 8
            damage = 20
        else:
            return
        
        # Determine direction
        direction = 1 if "right" in attack_state else -1
        
        # Get initial frame for projectile
        initial_frame = self.projectile_animations[projectile_type][0]
        
        # Calculate target direction - aim at player with slight offset for challenge
        if player:
            # Calculate angle to player
            target_x = player.x
            target_y = player.y - 30  # Aim at player's upper body
            
            # Add slight randomness to aim
            target_x += random.randint(-20, 20)
            target_y += random.randint(-10, 10)
            
            # Calculate direction vector
            dx = target_x - (self.rect.centerx + (direction * 50))
            dy = target_y - (self.rect.centery - 30)
            
            # Normalize direction vector
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                dx = (dx / magnitude) * speed
                dy = (dy / magnitude) * speed
            else:
                dx = direction * speed
                dy = 0
        else:
            # Fallback to horizontal movement if no player
            dx = direction * speed
            dy = 0
        
        # Create projectile object with mask for precise collision
        projectile = {
            "type": projectile_type,
            "x": self.rect.centerx + (direction * 50),  # Start position offset from boss
            "y": self.rect.centery - 30,  # Adjust vertical position
            "dx": dx,
            "dy": dy,
            "start_x": self.rect.centerx + (direction * 50),  # Store starting position for distance calculation
            "start_y": self.rect.centery - 30,
            "frame": 0,
            "animation": self.projectile_animations[projectile_type],
            "damage": damage,
            "frame_timer": 0,
            "frame_delay": 120,
            "rect": pygame.Rect(self.rect.centerx + (direction * 50), self.rect.centery - 30, 
                               initial_frame.get_width(), initial_frame.get_height()),
            "mask": pygame.mask.from_surface(initial_frame)  # Add mask for precise collision
        }
        
        self.projectiles.append(projectile)
    
    def update_projectiles(self, dt, player=None):
        """Update all active projectiles with mask-based collision"""
        for i in range(len(self.projectiles) - 1, -1, -1):
            projectile = self.projectiles[i]
            
            # Update position
            projectile["x"] += projectile["dx"]
            projectile["y"] += projectile["dy"]
            projectile["rect"].x = projectile["x"]
            projectile["rect"].y = projectile["y"]
            
            # Update animation
            projectile["frame_timer"] += dt
            if projectile["frame_timer"] > projectile["frame_delay"]:
                projectile["frame_timer"] = 0
                
                
                if projectile["frame"] < len(projectile["animation"]) - 1:
                    projectile["frame"] += 1
                else:
                    
                    if projectile["type"] == "ice_projectile":
                        #frames 2-4 are the "traveling" ice animation
                        projectile["frame"] = 2 + (projectile["frame"] - 2) % 3
                    
                    elif projectile["type"] == "lightning_projectile":
                        #frames 3-7 are the "traveling" lightning animation
                        projectile["frame"] = 3 + (projectile["frame"] - 3) % 5
                
                # Update mask with new frame
                projectile["mask"] = pygame.mask.from_surface(projectile["animation"][projectile["frame"]])

            
            # Calculate traveled distance
            traveled_distance = math.sqrt(
                (projectile["x"] - projectile["start_x"])**2 + 
                (projectile["y"] - projectile["start_y"])**2
            )
            
            # Check if projectile has traveled its maximum distance
            if traveled_distance > self.projectile_max_distance:
                self.projectiles.pop(i)
                continue
            
            # Check if projectile is out of bounds
            if not self.is_in_hallway(projectile["x"], projectile["y"]):
                self.projectiles.pop(i)
                continue
            
            # Check if projectile hits player using mask collision if player has a mask
            if player:
                # If player is a sprite with a mask
                if hasattr(player, 'mask') and player.mask:
                    # Calculate offset between player and projectile
                    offset_x = projectile["rect"].x - player.rect.x
                    offset_y = projectile["rect"].y - player.rect.y
                    
                    # Check for mask collision
                    if player.mask.overlap(projectile["mask"], (offset_x, offset_y)):
                        print(f"Projectile hit player for {projectile['damage']} damage!")
                        # Apply damage to player
                        if hasattr(player, 'take_damage'):
                            player.take_damage(projectile['damage'])
                        self.projectiles.pop(i)
                        continue
                # Fallback to simple rect collision if player doesn't have a mask
                elif hasattr(player, 'rect') and projectile["rect"].colliderect(player.rect):
                    print(f"Projectile hit player for {projectile['damage']} damage!")
                    # Apply damage to player
                    if hasattr(player, 'take_damage'):
                        player.take_damage(projectile['damage'])
                    self.projectiles.pop(i)
                    continue
                # Fallback to point collision as last resort
                elif projectile["rect"].collidepoint(player.x, player.y - 30):
                    print(f"Projectile hit player for {projectile['damage']} damage!")
                    # Apply damage to player
                    if hasattr(player, 'take_damage'):
                        player.take_damage(projectile['damage'])
                    self.projectiles.pop(i)
                    continue
    
    def draw_projectiles(self, screen):
        """Draw all active projectiles"""
        for projectile in self.projectiles:
            frame = projectile["animation"][projectile["frame"]]
            screen.blit(frame, (projectile["x"], projectile["y"]))
    
    def become_angry(self):
        """Make the boss temporarily invincible and enter an angry state."""
        self.is_invincible = True  # Become invincible
        self.is_angry = True
        self.angry_timer = self.angry_duration
        
        # Set angry animation based on current direction
        self.state = f"angry_{self.direction}"
        self.current_frame = 0
    
        # Boost boss stats in angry state
        self.speed *= 1.3
        self.damage *= 1.5
        self.attack_cooldown *= 0.8  # Faster attacks
        self.special_attack_cooldown *= 0.7  # More frequent special attacks
        
        self.attack_timer = 0  
        self.is_attacking = False
        
        shake_intensity = 15
        shake_duration = 20
    
        print("Boss has entered ANGRY state and is INVINCIBLE!")

    
    def take_damage(self, amount):
        if self.state not in ["death"]:  # Can now take damage if not dead
            if not self.is_invincible:  # Only take damage if not invincible
                self.health -= amount
                self.show_healthbar = True
    
                # Check if boss should transition into angry state
                if self.last_health_threshold - self.health >= 50 and self.health != 0:
                    self.become_angry()
                    self.last_health_threshold = self.health  # Update last threshold
                    self.is_attacking = False
                    self.attack_timer = 0
                    self.is_charging_special = False
                    return  # Stop further damage processing
    
                # Handle death
                if self.health <= 0:
                    self.state = "death"
                else:
                    self.previous_state = self.state  # Store previous state
                    self.state = "hurt"
    
                # Update image and mask
                self.current_frame = 0
                self.image = self.animations[self.state][self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)

    
    def can_attack(self):
        """Check if the boss can currently attack"""
        regular_attack = (self.is_attacking and 
                        self.attack_timer > 0 and 
                        self.state.startswith("att") and
                        self.current_frame >= 3)  # Only deal damage on certain frames
        
        return regular_attack
    
    def get_damage(self):
        """Return damage based on attack type and phase"""
        base_damage = self.damage
        
        # Apply angry state bonus
        if self.is_angry:
            base_damage *= 1.5
            
        # Apply phase 2 bonus
        if self.phase == 2:
            base_damage *= 1.2
            
        return int(base_damage)
    
    def draw(self, screen):
        """Draw the boss and any projectiles"""
        # Draw the boss
        screen.blit(self.image, self.rect)
        
        # Draw health bar if needed
        if self.show_healthbar:
            self.draw_healthbar(screen)
        
        # Draw projectiles
        self.draw_projectiles(screen)
    
    def draw_healthbar(self, screen):
        """Draw a more elaborate boss health bar"""
        bar_width = 80
        bar_height = 8
        fill = (self.health / self.max_health) * bar_width
        
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, fill, bar_height)
        
        # Phase-dependent health bar color
        if self.phase == 2:
            bar_color = (255, 50, 50)  # Redder for phase 2
        else:
            bar_color = (0, 255, 0)  # Green for phase 1
        
        pygame.draw.rect(screen, (50, 50, 50), outline_rect)  # Dark outline
        pygame.draw.rect(screen, bar_color, fill_rect)  # Colored health
        
        
        
class Boss1(Enemy):
    def __init__(self, x, y, is_in_hallway_func, health=180):
        # Load animations specifically for Boss1
        animations = {
            # Default idle state (needed by parent class)
            "idle": load_animation("enemies/level1/Boss1_down_idle", "png", 4, 1.0),
            
            # Directional idle animations
            "idle_down": load_animation("enemies/level1/Boss1_down_idle", "png", 4, 1.0),
            "idle_left": load_animation("enemies/level1/Boss1_left_idle", "png", 4, 1.0),
            "idle_right": load_animation("enemies/level1/Boss1_right_idle", "png", 4, 1.0),
            "idle_up": load_animation("enemies/level1/Boss1_up_idle", "png", 4, 1.0),
            
            # Directional walking animations
            "walk_down": load_animation("enemies/level1/Boss1_down_walk", "png", 8, 1.0),
            "walk_left": load_animation("enemies/level1/Boss1_left_walk", "png", 8, 1.0),
            "walk_right": load_animation("enemies/level1/Boss1_right_walk", "png", 8, 1.0),
            "walk_up": load_animation("enemies/level1/Boss1_up_walk", "png", 8, 1.0),
            
            # Default walk state (needed by parent class)
            "walk_left": load_animation("enemies/level1/Boss1_left_walk", "png", 8, 1.0),
            "walk_right": load_animation("enemies/level1/Boss1_right_walk", "png", 8, 1.0),
            
            # Attack animation (only left direction is available, we'll flip for right)
            "att_left": load_animation("enemies/level1/Boss1_left_att", "png", 8, 1.0),
            "att_right": load_animation("enemies/level1/Boss1_left_att", "png", 8, 1.0, flip=True),
            
            # Hurt animation (only left direction is available, we'll reuse for all directions)
            "hurt": load_animation("enemies/level1/Boss1_left_hurt", "png", 4, 1.0),
            
            # Death animation (using down direction)
            "death": load_animation("enemies/level1/Boss1_down_death", "png", 8, 1.0),
        }
        
        # Initialize parent class with boss-specific parameters
        super().__init__(x, y, animations, is_in_hallway_func, health)
        
        # Boss-specific attributes
        self.speed = 1.5  # Moderate movement speed
        self.damage = 30  # High damage
        self.detection_radius = 250  # Large detection radius
        self.attack_radius = 80  # Standard attack radius
        self.attack_cooldown = 1800  # Cooldown between attacks (ms)
        
        # Boss phases
        self.max_health = health
        self.last_health_threshold = health  # Store last health checkpoint for phase transition
        self.phase = 1  # Boss starts in phase 1
        self.phase_threshold = 0.4  # Boss enters phase 2 at 40% health
        
        # Direction tracking (down, left, right, up)
        self.direction = "down"  # Default direction
        
        # State management
        self.is_attacking = False
        self.is_chasing = False
        self.show_healthbar = False
        self.dead = False
        
        # Override the default state set by parent
        self.state = "idle"
        
        # Phase 2 enhancements
        self.phase_boost_applied = False
        self.attack_pattern = "normal"  # Can be "normal" or "aggressive"
        
        # Hurt recovery
        self.hurt_recovery_timer = 0
        self.hurt_recovery_duration = 300  # ms
        
        # Quick attack sequence variables (for phase 2)
        self.quick_attack_count = 0
        self.max_quick_attacks = 3
        self.in_quick_attack_sequence = False
        
        # New: Store player reference for hurt recovery behavior
        self.current_player = None
        self.check_player_after_hurt = False
    
    def update(self, dt, player=None):
        """Update boss state, animations, movement, and attacks."""
        
        # Store player reference for hurt recovery
        if player is not None:
            self.current_player = player
        
        # Update frame timer for animations
        self.frame_timer += dt
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
        
        # Check for phase change
        current_health_percentage = self.health / self.max_health
        if current_health_percentage <= self.phase_threshold and self.phase == 1 and not self.phase_boost_applied:
            self.phase = 2
            self.phase_boost_applied = True
            self.apply_phase_two_boost()
        
        # Handle animations
        if self.frame_timer > self.frame_delay:
            self.frame_timer = 0
            
            # Death animation
            if self.state == "death":
                if self.current_frame < len(self.animations["death"]) - 1:
                    self.current_frame += 1
                else:
                    self.kill()
                    self.dead = True
                    return
            
            # Hurt animation
            elif self.state == "hurt":
                if self.current_frame < len(self.animations["hurt"]) - 1:
                    self.current_frame += 1
                else:
                    # After hurt animation completes, set flag to check for player and possibly attack
                    self.check_player_after_hurt = True
                    self.current_frame = 0
                    self.hurt_recovery_timer = 0  # Allow immediate action after hurt
            
            # Attack animations
            elif self.state.startswith("att"):
                if self.current_frame < len(self.animations[self.state]) - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
                    self.is_attacking = False
                    
                    # In phase 2, continue with quick attack sequence if needed
                    if self.phase == 2 and self.in_quick_attack_sequence and self.quick_attack_count < self.max_quick_attacks:
                        self.quick_attack_count += 1
                        self.is_attacking = True
                        # Keep the same attack direction
                        if player and player.x > self.rect.centerx:
                            self.state = "att_right"
                        else:
                            self.state = "att_left"
                    else:
                        self.in_quick_attack_sequence = False
                        self.quick_attack_count = 0
                        if self.is_chasing:
                            self.state = f"walk_{self.direction}" if self.direction in ["left", "right", "up", "down"] else "walk_left"
                        else:
                            self.state = "idle"
            
            # Normal movement animations
            else:
                if self.state in self.animations:
                    self.current_frame = (self.current_frame + 1) % len(self.animations[self.state])
            
            # Update sprite image and mask
            if self.state in self.animations:
                self.image = self.animations[self.state][self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)
        
        # Stop movement and AI if boss is in death state
        if self.state == "death":
            return
        
        # Check if we need to assess player position after hurt animation
        if self.check_player_after_hurt and self.current_player:
            player = self.current_player
            self.check_player_after_hurt = False
            
            # Calculate distance to player
            dist_to_player = math.sqrt((self.rect.centerx - player.x) ** 2 + (self.rect.centery - player.y) ** 2)
            
            if dist_to_player <= self.detection_radius:
                self.is_chasing = True
                self.update_direction(player)
                
                # If player is in attack range, attack immediately after being hurt
                if dist_to_player <= self.attack_radius and self.attack_timer <= 0:
                    self.perform_attack(player)
                else:
                    # If player is detected but not in attack range, chase
                    self.state = f"walk_{self.direction}" if self.direction in ["left", "right", "up", "down"] else "walk_left"
            else:
                # Player not in range, go back to idle
                self.is_chasing = False
                self.state = "idle"
            
            # Update image and mask to reflect new state
            self.image = self.animations[self.state][self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)
            return  # Skip the rest of the update for this frame
        
        # Handle hurt recovery timer (only applies if not checking for player)
        if self.hurt_recovery_timer > 0:
            self.hurt_recovery_timer -= dt
            return
        
        # Skip movement and AI if boss is still in hurt state
        if self.state == "hurt":
            return
        
        # Player detection and AI
        if player is not None:
            dist_to_player = math.sqrt((self.rect.centerx - player.x) ** 2 + (self.rect.centery - player.y) ** 2)
            
            # Detect player and set chase state
            if dist_to_player <= self.detection_radius:
                self.is_chasing = True
                
                # Update movement direction if not attacking
                if not self.is_attacking:
                    self.update_direction(player)
                    # Set appropriate walking animation based on direction
                    if not self.state.startswith("att"):
                        if self.direction in ["left", "right", "up", "down"]:
                            self.state = f"walk_{self.direction}"
                        else:
                            self.state = "walk_left"  # Default to walk_left if direction is invalid
                
                # Attack decision
                if (
                    dist_to_player <= self.attack_radius
                    and not self.is_attacking
                    and self.attack_timer <= 0
                ):
                    self.perform_attack(player)
                    return
                
                # Movement towards player
                if not self.is_attacking:
                    dx = self.speed if player.x > (self.rect.centerx + 10) else -self.speed if player.x < (self.rect.centerx - 10) else 0
                    dy = self.speed if player.y > (self.rect.bottom+10) else -self.speed if player.y < (self.rect.bottom+10) else 0
                    
                    # Normalize diagonal movement
                    if dx != 0 and dy != 0:
                        magnitude = math.sqrt(dx**2 + dy**2)
                        dx = (dx / magnitude) * self.speed
                        dy = (dy / magnitude) * self.speed
                    
                    # Calculate new position
                    next_x = self.rect.x + dx
                    next_y = self.rect.y + dy
                    
                    # Check if move is valid
                    if self.is_in_hallway(next_x, next_y):
                        self.rect.x = next_x
                        self.rect.y = next_y
            else:
                self.is_chasing = False
                if not self.is_attacking:
                    self.state = "idle"
        
        # Update health bar visibility
        if self.health < self.max_health:
            self.show_healthbar = True
    
    def update_direction(self, player):
        """Update boss direction based on player position."""
        dx = player.x - self.rect.centerx
        dy = player.y - self.rect.centery
        
        # Determine the predominant direction (4-way)
        if abs(dx) > abs(dy):
            # Moving horizontally
            self.direction = "right" if dx > 0 else "left"
        else:
            # Moving vertically
            self.direction = "down" if dy > 0 else "up"
    
    def perform_attack(self, player):
        """Initiate an attack based on player position."""
        self.is_attacking = True
        
        # Choose attack type based on phase and distance
        if self.phase == 2 and random.random() < 0.4:
            # Start quick attack sequence in phase 2
            self.in_quick_attack_sequence = True
            self.quick_attack_count = 1
        
        # Set attack direction based on player position
        if player.x > self.rect.centerx:
            self.state = "att_right"
        else:
            self.state = "att_left"
        
        # Reset attack animation
        self.current_frame = 0
        
        # Set cooldown
        self.attack_timer = self.attack_cooldown
    
    def apply_phase_two_boost(self):
        """Apply stat boosts for phase two."""
        self.speed *= 1.25
        self.damage *= 1.3
        self.attack_cooldown *= 0.8  # Faster attacks
        print("Boss has entered Phase 2 - Becoming more aggressive!")
    
    def take_damage(self, amount):
        """Handle boss taking damage."""
        if self.state not in ["death", "hurt"]:  # Only take damage if not already hurt or dead
            self.health -= amount
            self.show_healthbar = True
            
            # Handle death
            if self.health <= 0:
                self.health = 0
                self.state = "death"
                self.current_frame = 0
            else:
                # Enter hurt state
                self.previous_state = self.state  # Store previous state
                self.state = "hurt"
                self.current_frame = 0
            
            # Update image and mask
            self.image = self.animations[self.state][self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)
    
    def can_attack(self):
        """Check if the boss can currently attack"""
        regular_attack = (self.is_attacking and 
                         self.state.startswith("att") and
                         self.current_frame >= 4 and self.current_frame <= 6)  # Only deal damage on certain frames
        
        return regular_attack
    
    def get_damage(self):
        """Return damage based on attack type and phase"""
        base_damage = self.damage
        
        # Apply phase 2 bonus
        if self.phase == 2:
            base_damage *= 1.2
            
        # Apply quick attack sequence bonus
        if self.in_quick_attack_sequence:
            base_damage *= 0.8  # Slightly reduced damage for quick attacks
            
        return int(base_damage)
    
    def draw(self, screen):
        """Draw the boss and health bar if needed."""
        # Draw the boss
        screen.blit(self.image, self.rect)
        
        # Draw health bar if needed
        if self.show_healthbar:
            self.draw_healthbar(screen)
    
    def draw_healthbar(self, screen):
        """Draw a boss health bar."""
        bar_width = 80
        bar_height = 8
        fill = (self.health / self.max_health) * bar_width
        
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, fill, bar_height)
        
        # Phase-dependent health bar color
        if self.phase == 2:
            bar_color = (255, 0, 0)  # Red for phase 2
        else:
            bar_color = (0, 255, 0)  # Green for phase 1
        
        pygame.draw.rect(screen, (50, 50, 50), outline_rect)  # Dark outline
        pygame.draw.rect(screen, bar_color, fill_rect)  # Colored health