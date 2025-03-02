_player(screen, scaled_player_x, scaled_player_y, camera_x, camera_y, scale_x):
#     """Draw the player sprite instead of a circle."""
#     size = int(player_radius * 4 * scale_x)  # Adjust size multiplier as needed
#     player_img_scaled = pygame.transform.scale(player_img, (size, size))
#     screen.blit(player_img_scaled, (scaled_player_x - camera_x - size // 2, 
#                                     scaled_player_y - camera_y