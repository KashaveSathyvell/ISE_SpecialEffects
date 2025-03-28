def show_victory_screen():
    font = pygame.font.SysFont('Arial', 48)
    victory_text = font.render("Princess Rescued!!", True, (255, 255, 0))

    # Use the first frame of the princess' idle animation
    princess_img = princess.images[0]  # Adjust if needed
    player_img = player.current_image  # Assuming this is the correct player sprite

    # Scale images
    princess_scaled = pygame.transform.scale(princess_img, (100, 150))
    player_scaled = pygame.transform.scale(player_img, (300, 230))

    while True:
        switch_music(victory)
        screen.fill((0, 0, 0))  # Black background
        screen.blit(victory_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
        screen.blit(player_scaled, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))
        screen.blit(princess_scaled, (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
