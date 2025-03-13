
class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Character Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width, self.height = width, height

        # Game objects
        self.character_manager = CharacterManager()
        self.bg_color = (50, 50, 50)
        self.font = pygame.font.SysFont(None, 24)

        # Game state
        self.controlled_character_id = "player"
        self.show_collision_info = True
        self.collisions = []
        self.combat_messages = []
        self.message_duration = 2000

        # Setup characters
        self.setup_characters()

    def setup_characters(self):
        # Add player character
        self.player = self.character_manager.add_character(
            "player", self.width // 2, self.height // 2, "Knight")
        self.player.z_index = sys.maxsize

        frame_counts = {
            'idle': 15, 'move': 8, 'attack': 22,
            'ultimate': 22, 'death': 15, 'jump': 14,
            'shield': 7
        }

        # Configure player animations
        self.character_manager.set_frame_counts("player", frame_counts)

        # Configure animation speeds
        self.character_manager.set_animation_speeds("player", {
            'idle': 100, 'move': 80, 'attack': 100,
            'ultimate': 50, 'death': 120, 'jump': 70,
            'shield': 50
        })

        # Configure ultimate attack
        self.character_manager.configure_ultimate("player", cooldown=5000, damage=30)

        # Set custom damage for player
        self.player.damage_amount = 15

        # Add enemy for testing
        self.character_manager.add_character(
            "enemy", self.width // 2 + 100, self.height // 2, "Knight")

        # Configure enemy animations
        self.character_manager.set_frame_counts("enemy", frame_counts)

        # Configure enemy ultimate
        self.character_manager.configure_ultimate("enemy", cooldown=7000, damage=20)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Key press events
            if event.type == pygame.KEYDOWN:
                controlled_char = self.character_manager.get_character(self.controlled_character_id)
                if controlled_char:
                    if event.key == pygame.K_q:  # Regular attack
                        controlled_char.attack()
                    elif event.key == pygame.K_e:  # Ultimate attack
                        if controlled_char.use_ultimate():
                            self.combat_messages.append((
                                f"{self.controlled_character_id} used ultimate attack!",
                                pygame.time.get_ticks()
                            ))
                    elif event.key == pygame.K_f:  # Shield key
                        controlled_char.toggle_shield(True)
                    elif event.key == pygame.K_SPACE:
                        controlled_char.jump()
                    elif event.key == pygame.K_r:
                        controlled_char.reset()
                    elif event.key == pygame.K_x:
                        controlled_char.die()
                    elif event.key == pygame.K_TAB:
                        # Switch controlled character
                        char_ids = list(self.character_manager.characters.keys())
                        current_idx = char_ids.index(self.controlled_character_id)
                        next_idx = (current_idx + 1) % len(char_ids)
                        self.controlled_character_id = char_ids[next_idx]
                    elif event.key == pygame.K_c:
                        # Toggle collision info
                        self.show_collision_info = not self.show_collision_info
                    elif event.key == pygame.K_h:
                        # Self-damage for testing
                        controlled_char.take_damage(10)
            if event.type == pygame.KEYUP:
                controlled_char = self.character_manager.get_character(self.controlled_character_id)
                if controlled_char and event.key == pygame.K_f:  # Shield key released
                    controlled_char.toggle_shield(False)

    def update(self):
        current_time = pygame.time.get_ticks()

        # Handle movement
        keys = pygame.key.get_pressed()
        controlled_char = self.character_manager.get_character(self.controlled_character_id)

        if controlled_char and not controlled_char.dead:
            dx, dy = 0, 0

            if keys[pygame.K_a]: dx = -controlled_char.speed  # Left
            if keys[pygame.K_d]: dx = controlled_char.speed   # Right
            if keys[pygame.K_w]: dy = -controlled_char.speed  # Up
            if keys[pygame.K_s]: dy = controlled_char.speed   # Down

            # Move character with bounds
            controlled_char.move(dx, dy)
            controlled_char.x = max(0, min(controlled_char.x, self.width))
            controlled_char.y = max(50, min(controlled_char.y, self.height))

        # Update all characters
        self.character_manager.update_all()

        # Check for collisions and combat
        self.collisions, new_combat_results = self.character_manager.check_all_collisions()

        # Add new combat messages
        for attacker, defender, damage in new_combat_results:
            char = self.character_manager.get_character(attacker)
            is_ultimate = char and char.using_ultimate

            message = f"{attacker} hit {defender} for {damage} damage!"
            if is_ultimate:
                message = f"ULTIMATE: {message}"

            self.combat_messages.append((message, current_time))

        # Update combat message timers
        self.combat_messages = [(msg, time) for msg, time in self.combat_messages
                               if current_time - time < self.message_duration]

    def render(self):
        # Clear screen
        self.screen.fill(self.bg_color)

        # Draw characters
        self.character_manager.draw_all(self.screen)

        # Draw controlled character UI
        self.character_manager.draw_controlled_ui(self.screen, self.controlled_character_id, 20, 20)

        # Display which character is being controlled
        text = self.font.render(f"Controlling: {self.controlled_character_id} (TAB to switch)", True, (255, 255, 255))
        self.screen.blit(text, (20, 60))

        # Display controls
        controls = [
            "Controls:", "WASD: Move", "SPACE: Jump",
            "Q: Attack", "E: Ultimate", "F: Shield", "X: Die",
            "R: Reset", "H: Test damage"
        ]
        for i, line in enumerate(controls):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (10, 90 + i * 20))

        # Display collision info
        y_offset = self.height - 30
        if self.show_collision_info and self.collisions:
            collision_text = "Collisions: " + ", ".join([f"{c1} & {c2}" for c1, c2 in self.collisions])
            text = self.font.render(collision_text, True, (255, 200, 100))
            self.screen.blit(text, (10, y_offset - 20))

        # Display combat messages
        for i, (message, _) in enumerate(reversed(self.combat_messages)):
            text = self.font.render(message, True, (255, 100, 100))
            self.screen.blit(text, (10, y_offset - (i+1) * 20))

        # Display character health (except for controlled character)
        for i, (char_id, character) in enumerate(self.character_manager.characters.items()):
            if char_id != self.controlled_character_id:
                health_text = f"{char_id}: {character.health}/{character.max_health} HP"
                color = (100, 255, 100) if character.health > 30 else (255, 100, 100)
                text = self.font.render(health_text, True, color)
                self.screen.blit(text, (self.width - 200, 30 + i * 20))

        # Update display
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
