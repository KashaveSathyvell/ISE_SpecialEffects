    # # Draw special rooms.
    # for room_name, (room_x, room_y, room_width, room_height, room_type) in special_rooms.items():
    #     area_match = False
    #     if current_area == "boss_arena" and "boss" in room_name:
    #         area_match = True
    #     elif current_area == "eastern_complex" and "treasure" in room_name:
    #         area_match = True
    #     elif current_area == "western_wing" and "mini_boss" in room_name:
    #         area_match = True
    #     elif current_area == "central_pathways" and "water" in room_name:
    #         area_match = True
    #     elif current_area == "lower_labyrinth" and ("trap" in room_name or "secret" in room_name):
    #         area_match = True
    #     if area_match:
    #         scaled_room_x = room_x * scale_x - camera_x
    #         scaled_room_y = room_y * scale_y - camera_y
    #         scaled_room_width = room_width * scale_x
    #         scaled_room_height = room_height * scale_y
    #         if room_type == "combat":
    #             color = (255, 50, 50, 100)
    #         elif room_type == "puzzle":
    #             color = (50, 255, 255, 100)
    #         elif room_type == "treasure":
    #             color = (255, 255, 50, 100)
    #         elif room_type == "rescue":
    #             color = (255, 100, 255, 100)
    #         elif room_type == "traps":
    #             color = (255, 150, 0, 100)
    #         elif room_type == "boss_fight":
    #             color = (200, 0, 0, 150)
    #         else:
    #             color = (150, 150, 150, 100)
    #         s = pygame.Surface((scaled_room_width, scaled_room_height), pygame.SRCALPHA)
    #         s.fill(color)
    #         screen.blit(s, (scaled_room_x, scaled_room_y))