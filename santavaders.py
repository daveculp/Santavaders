import pygame
import math
import time
import random
import datetime
import glob 
import os
import getpass
import sys



#***********************************************************************
#*                       FUNCTIONS AREA                                *
#***********************************************************************
def play_next_song():
    #if pygame.mixer.music.get_busy() == False:
    song = random.choice(song_list)
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(0)
    print ("Playing: +",song)
        
def stereo_pan(x_pos):
    """Adjust the left and right volume based upon scren ccordinates """
    right_volume = float(x_pos) / SCREEN_WIDTH
    left_volume = 1.0 - right_volume
    if game_data["game_sound_state"] == True:
        return (left_volume, right_volume)
    else:
        return(0, 0)

def play_sound(sound, x_pos):
    """Play passed in sound object on new channel"""
    channel = sound.play()
    if channel is not None:
        left, right = stereo_pan(x_pos)
        channel.set_volume(left, right)

def scale_image_by(image, scale_factor_x, scale_factor_y):
    height = image.get_height() * scale_factor_y
    width = image.get_width() * scale_factor_x
    return pygame.transform.scale(image, (width, height))
    
def load_image(filename, scale_factor_x, scale_factor_y):
    image = pygame.image.load(filename).convert_alpha()
    return scale_image_by(image, scale_factor_x, scale_factor_y)
    

def display_pause_screen():
    """Render the pause screen and wait for user input."""
    global game_state
    pause_text = font.render("PAUSED", True, (255, 0, 0))  # Red text
    pause_shadow = font.render("PAUSED", True, (0, 128, 0))  # Green shadow
    instructions_text = font.render("Press P to Resume or Q to Quit", True, (255, 0, 0))
    instructions_shadow = font.render("Press P to Resume or Q to Quit", True, (0, 128, 0))

    # Blit the shadow (slightly offset) and the text
    screen.blit(pause_shadow, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2 + 5, SCREEN_HEIGHT // 3 + 5))
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 3))

    screen.blit(instructions_shadow, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2 + 5, SCREEN_HEIGHT // 2 + 5))
    screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()

    # Wait for player input to resume or quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_data["game_state"] = GAME_STATE_QUIT
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Resume game
                    game_data["game_state"] = GAME_STATE_RUNNING
                    waiting = False
                if event.key == pygame.K_q:  # Quit game
                    game_data["game_state"] = GAME_STATE_QUIT
                    waiting = False
        

def display_title_screen():
    global game_state
    #pygame.mixer.music.play(0)
    screen.blit(title_screen_image, (0, 0))
    pygame.display.flip()
    waiting = True
    while waiting:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        if keys[pygame.K_SPACE]:
            waiting = False  # Exit the loop and start the game
            game_data["game_state"] = GAME_STATE_RUNNING
            reset_game(True)
        if keys[pygame.K_ESCAPE]:
            waiting = False
            game_data["game_state"] = GAME_STATE_QUIT

def reset_game(load_next_level):
    
    global game_data
    print("Resetting game!!")
    # Reset the game data dictionary back to original
    game_data = dict(default_game_data)
    if load_next_level:
        start_next_level()

# ***********************************************************************
# *                       HIGH SCORES MANAGEMENT                       *
# ***********************************************************************

HIGH_SCORES_FILE = "highscores.txt"

def load_high_scores():
    """Load high scores from a file."""
    high_scores = []
    try:
        with open(HIGH_SCORES_FILE, "r") as file:
            for line in file:
                name, score = line.strip().split(",")
                high_scores.append((name, int(score)))
    except FileNotFoundError:
        print(f"High scores file '{HIGH_SCORES_FILE}' not found. Starting fresh.")
        high_scores = [("None", 0) for _ in range(10)]  # Default scores
    return high_scores

def save_high_scores(high_scores):
    """Save high scores to a file."""
    with open(HIGH_SCORES_FILE, "w") as file:
        for name, score in high_scores:
            file.write(f"{name},{score}\n")

def update_high_scores(player_name, player_score, high_scores):
    """Update the high scores with the player's score if it qualifies."""
    high_scores.append((player_name, player_score))
    high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)[:10]
    return high_scores

def display_high_scores(high_scores, player_name=None, player_score=None):
    """Display the high scores on the game over screen."""
    y_start = SCREEN_HEIGHT // 14+50*(SCALE_FACTOR)  # Starting y-coordinate
      # Get height of the font and add padding

    for i, (name, score) in enumerate(high_scores):
        if name == player_name and score == player_score:
            color = (0, 255, 0)  # Highlight in green for the current player
        else:
            color = (255, 0, 0)  # Default red color

        score_text = font.render(f"{i + 1}. {name}: {score}", True, color)
        score_text = scale_image_by(score_text,.75, .75)
        #score_text= pygame.transform.scale_by(score_text, .75)
        line_height = score_text.get_height()
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_start + i * line_height))

# ***********************************************************************
# *                     GAME OVER SCREEN                     *
# ***********************************************************************

def game_over():
    global game_data
    player_name = getpass.getuser()  # Retrieve player username
    high_scores = load_high_scores()  # Load current high scores

    # Update the high scores with the player's score
    player_score = game_data["player_score"]
    updated_high_scores = update_high_scores(player_name, player_score, high_scores)
    save_high_scores(updated_high_scores)  # Save the updated high scores

    # Initial display of the last game scene with GAME OVER text
    large_font = pygame.font.Font(font_path, 200)  # Set the font size to double the original
    game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))  # Red text
    game_over_shadow = large_font.render("GAME OVER", True, (0, 255, 0))  # Green shadow
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    shadow_rect = game_over_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 10))  # Slight offset for shadow

    end_game_time = pygame.time.get_ticks() + 4000  # 4 seconds display

    while pygame.time.get_ticks() < end_game_time:
        screen.blit(game_over_shadow, shadow_rect)  # First the shadow
        screen.blit(game_over_text, text_rect)  # Then the text
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                sys.exit()
    # After 4 seconds, proceed to standard game over screen


    # Wait for user input
    waiting = True
    
    while waiting:
        screen.fill((0, 0, 0))  # Clear the screen
        for snowflake in snowflakes:
            snowflake["y"] += snowflake["speed"]*SCALE_FACTOR
            if snowflake["y"] > SCREEN_HEIGHT:
                snowflake["y"] = 0
                snowflake["x"] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(screen, (255, 255, 255), (int(snowflake["x"]), int(snowflake["y"])), snowflake["size"])

        # Redisplay game over message and other info with shadow\
        game_over_shadow = font.render("GAME OVER", True, (0, 255, 0))  # Green shadow
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))  # Red text
        screen.blit(game_over_shadow, (SCREEN_WIDTH // 2 - game_over_shadow.get_width() // 2 + 5, 10))  # Shadow offset
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 5))  # Main text
        
        display_high_scores(updated_high_scores, player_name, player_score)
        
        instructions_text = font.render("Press Q to Quit or SPACE to Restart", True, (255, 255, 255))
        y_offset = instructions_text.get_height()
        screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT - y_offset))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_data["game_state"] = GAME_STATE_QUIT
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    game_data["game_state"] = GAME_STATE_QUIT
                    waiting = False
                if event.key == pygame.K_SPACE:
                    waiting = False
                    #reset_game(False)
                    game_data["game_state"] = GAME_STATE_TITLE
                    pygame.time.wait(500)
        clock.tick(60)



def draw_scene():
    global invaders, star_rect, santa_sleigh_rect, bag_rect
    global player_rect, present_list, fireplaces, game_data 
    # Fill the background with black
    screen.fill((0, 0, 0))

# Draw snowflakes
    for snowflake in snowflakes:
        pygame.draw.circle(screen, (255, 255, 255), (int(snowflake["x"]), int(snowflake["y"])), snowflake["size"])

    #draw the player
    player_rect = screen.blit(current_player_image, (player_rect.x, player_rect.y))
    
    #draw the star missile if it is active
    if game_data["star_active"]:
        star_rect = screen.blit(star_image, star_rect)
        
    #draw santa sleigh at the top if active
    if game_data["santa_sleigh_active"]:
        santa_sleigh_rect = screen.blit(santa_sleigh_image, santa_sleigh_rect)
    
    #draw santas guided bag missile if active
    if game_data["guided_bag_active"]:
        bag_rect = screen.blit(bag_image, bag_rect)
        
    #draw the santa heads
    for row in range(5):
        for col in range(11):
            if invaders[row][col]["active"]:
                x = invaders_pos[0] + (col*invader_width) + (invader_width//2)*col 
                y = invaders_pos[1] + (row*invader_height ) + (invader_height//2) * row
                invaders[row][col]["rect"] = screen.blit(invader_image, [x, y] )

    #draw the santa heads exploding 
    for row in range(5):
        for col in range(11):
            if invaders[row][col]["exploding"]:
                if time.time() - invaders[row][col]["explode_time"]< EXPLOSION_FRAME_DURATION:
                    break
                frame = invaders[row][col]["explode_frame"]
                x_pos = invaders_pos[0] + (col*invader_width) + (invader_width//2)*col 
                y_pos = invaders_pos[1] + (row*invader_height ) + (invader_height//2) * row
                invaders[row][col]["rect"] = screen.blit(explosion_graphics[frame], [x_pos, y_pos] )
                frame = frame + 1
                if frame == len(explosion_graphics):
                    invaders[row][col]["exploding"] = False
                invaders[row][col]["explode_frame"] = frame
                invaders[row][col]["explode_time"] = time.time()
             
    #draw presents if there are active presents in the list
    if present_list:
        for p, present in enumerate(present_list):
            present_list[p] = screen.blit(present_image, present )
            #pygame.draw.rect (screen, (0,255,0), present,  2)

    #draw fireplaces using the eroded masks
    if game_data["fireplaces_active"]:
        for fireplace in fireplaces:
            if fireplace["active"]:
            # Create a surface where the mask is rendered
                mask_surface = fireplace["mask"].to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255))
                # Create a new surface for the filtered fireplace
                filtered_surface = pygame.Surface(fireplace["surface"].get_size(), pygame.SRCALPHA)
                filtered_surface.blit(fireplace_image, (0, 0))  # Copy original fireplace image
                filtered_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)  # Apply the mask

                # Blit the filtered surface to the screen
                screen.blit(filtered_surface, (fireplace["x"], fireplace["y"]))

    # draw explosions if there are any in the list
    if explosion_list:
        for explosion in explosion_list:
            image_num = explosion["frame"]
            image = explosion_graphics[image_num]
            rect = explosion["rect"]
            screen.blit(image, rect)
            
        
    # Render the score text with a shadow effect
    player_score = game_data["player_score"]
    score_text = font.render(f"Score: {player_score}", True, (255, 0, 0))  # White text
    shadow_text = font.render(f"Score: {player_score}", True, (0, 128, 0))  # Green shadow
    
    #shrink the score text by 75%
    #score_text = pygame.transform.scale_by(score_text, (.75, .75)) 
    #shadow_text = pygame.transform.scale_by(shadow_text, (.75, .75)) 
    score_text = scale_image_by(score_text, .75, .75)
    shadow_text = scale_image_by(shadow_text, .75, .75)
    # Calculate text width and positions
    text_width = score_text.get_width()
    x_position = SCREEN_WIDTH - text_width - (20*SCALE_FACTOR)
    y_position = 50 * SCALE_FACTOR
    
    # Draw shadow slightly offset
    screen.blit(shadow_text, (x_position + 5, y_position + 5))
    # Draw the main text
    screen.blit(score_text, (x_position, y_position))

    # Render the level text with a shadow effect
    current_level = game_data["current_level"]+1
    level_text = font.render(f"Level: {current_level}", True, (255, 0, 0))  # White text
    shadow_text = font.render(f"Level: {current_level}", True, (0, 128, 0))  # Green shadow
    
    #level_text = pygame.transform.scale_by(level_text, (.75, .75)) 
    #shadow_text = pygame.transform.scale_by(shadow_text, (.75, .75))
    level_text = scale_image_by(level_text, .75, .75)
    shadow_text = scale_image_by(shadow_text, .75, .75) 
    # Calculate text width and positions
    text_width = level_text.get_width()
    x_position = 20
    y_position = 50
    # Draw shadow slightly offset
    screen.blit(shadow_text, (x_position + 5, y_position + 5))
    # Draw the main text
    screen.blit(level_text, (x_position, y_position))
    #draw FPSscreen.blit(playerimage, playerpos)
    if game_data["show_fps"]:
        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("coral"))
        screen.blit(fps_text, (10,SCREEN_HEIGHT-fps_text.get_height()))
        

        
def update():
    global star_rect, current_player_image, santa_sleigh_rect, snowflakes
    global present_list, santa_sleigh_sound, game_data, explosion_list
    global current_player_mask, invaders
   
    current_level = game_data["current_level"]

    #if santas sleigh is not active, check if it appears
    if not game_data["santa_sleigh_active"]:
        if pygame.time.get_ticks() - game_data["sleigh_time"] > 11000:
            if random.randint(0,100) < 2:
                game_data["santa_sleigh_active"] = True
                santa_sleigh_rect.x  = 0
                santa_sleigh_rect.y = 20*SCALE_FACTOR
                play_sound(santa_sleigh_sound,SCREEN_WIDTH/2)
    else: #if santa sleigh is on the screen, update it and check bounds
        santa_sleigh_rect.x += level_data[current_level]["santa_sleigh_speed"]*SCALE_FACTOR
        if santa_sleigh_rect.x > SCREEN_WIDTH:
            game_data["santa_sleigh_active"] = False
            santa_sleigh_sound.stop()
            game_data["sleigh_time"] = pygame.time.get_ticks()

    #update the direction and position of the guided bag/missile
    if game_data["guided_bag_active"]:
        # Calculate the horizontal distance between the missile and the player
        distance_x = player_rect.centerx - bag_rect.centerx
        # Calculate the scaled speed
        speed_x = distance_x * .1*SCALE_FACTOR
        # Ensure the speed does not exceed the maximum allowed speed
        max_speed = 15 * SCALE_FACTOR
        speed_x = max(-max_speed, min(max_speed, speed_x))
        bag_rect.y += game_data["guided_bag_speed"]
        bag_rect.x += speed_x
        if bag_rect.y > SCREEN_HEIGHT:
            game_data["guided_bag_active"] = False
            
    #spawn a guided bag if necessary
    if game_data["santa_sleigh_active"] and not game_data["guided_bag_active"]:
        if random.randint(0,500) < 1:
            bag_rect.x = santa_sleigh_rect.x
            bag_rect.y = santa_sleigh_rect.y
            game_data["guided_bag_active"] = True
    
    #update player star missile
    if game_data["star_active"]:
        star_rect.y -= game_data["star_speed"]*SCALE_FACTOR
        if star_rect.y <= 0:
            game_data["star_active"] = False
            current_player_image = player_image_star
            current_playher_mask = pygame.mask.from_surface(player_image_star)
    
    #update presents 
    present_list = [present for present in present_list if present.y <= SCREEN_HEIGHT]
    for present in present_list:
        present.y += level_data[current_level]["present_speed"]*SCALE_FACTOR

    #update the explosions in the explosion list
    for i in range(len(explosion_list) - 1, -1, -1):  # iterate in reverse using index
        explosion = explosion_list[i]
        if time.time() - explosion["time"] > EXPLOSION_FRAME_DURATION:
            explosion["frame"] += 1
            if explosion["frame"] == len(explosion_graphics):
                del explosion_list[i]  # delete by index
            else:
                explosion["time"] = time.time()
      
    #deativate fireplaces that receive too much damage
    for fireplace in fireplaces:
        if fireplace["num_hit"] > 12:
            fireplace["active"] = False
            
    # Generate a random Santa present shot
    active_invaders = [(row, col) for row in range(5) for col in range(11) if invaders[row][col]["active"]]
    if active_invaders and random.randint(0, 101) < level_data[current_level]["santa_shot_chance"]:
        row, col = random.choice(active_invaders)
        x = invaders[row][col]["rect"].centerx
        y = invaders[row][col]["rect"].centery
        width = present_image.get_width()
        height = present_image.get_height()
        rect = pygame.Rect(x, y, width, height)
        play_sound(santa_shoot_sound, rect.x)
        present_list.append(rect)
    
    # Check Santa head movement limits and reverse direction if necessary
    reverse_direction = False
    for row in range(len(invaders)):
        for col in range(len(invaders[row])):
            if invaders[row][col]["active"]:  # Check if Santa head is active
                invader_rect = invaders[row][col]["rect"] #get the rectangle at that position
                if invader_rect.x <= 0 or invader_rect.x + invader_width >= SCREEN_WIDTH:
                    reverse_direction = True
                    break
        if reverse_direction:
            break

    if reverse_direction:
        game_data["invaders_dir"] *= -1  # Reverse direction
        invaders_pos[1] += 25*SCALE_FACTOR  # Move Santa heads down
        
    #move the santa head position of the structure
    speed_add = game_data["invader_speed_add"]
    current_speed = level_data[current_level]["invader_speed"]
    invaders_pos[0] += (current_speed+speed_add) * game_data["invaders_dir"]*SCALE_FACTOR
        
    # Update snowflakes
    for snowflake in snowflakes:
        snowflake["y"] += snowflake["speed"]*SCALE_FACTOR  # Move snowflake down
        if snowflake["y"] > SCREEN_HEIGHT:  # If it goes off-screen
            snowflake["y"] = 0  # Reset to the top
            snowflake["x"] = random.randint(0, SCREEN_WIDTH)  # Random x position
            snowflake["size"] = random.randint(2, 5)  # Random size
            snowflake["speed"] = random.uniform(1, 3)  # Random speed
            
    # Check for lowest alien reaching fireplace or player Y-coordinate
    for row in range(4, -1, -1):  # Iterate rows in reverse (4 to 0)
        for col in range(11):
            if invaders[row][col]["active"]:  # Check if the alien is active
                alien_x = invaders_pos[0] + (col * invader_width) + (invader_width // 2) * col
                alien_y = invaders_pos[1] + (row * invader_height) + (invader_height // 2) * row
                alien_bottom = alien_y + invader_height

                if alien_bottom >= playerpos[1]:  # Game Over Condition
                    print("GAME OVER!!!")
                    game_data["is_game_over"] = True
                    return  # Exit immediately

                if game_data["fireplaces_active"] and alien_bottom >= fireplace_y:  # Fireplace Condition
                    game_data["fireplaces_active"] = False
                    return  # Exit immediately after deactivating fireplaces
    
def erode_fireplace(fireplace, center, radius):
    """
    Directly modify the fireplace mask by eroding bits in a circular area.
    :param fireplace: Dictionary containing fireplace data (surface, mask, position).
    :param center: (x, y) center of the erosion circle in world coordinates.
    :param radius: Radius of the erosion circle.
    """
    # Convert world coordinates to local mask coordinates
    local_center_x = center[0] - fireplace["x"]
    local_center_y = center[1] - fireplace["y"]

    # Iterate through the mask pixels within the erosion radius
    for y in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            if x ** 2 + y ** 2 <= radius ** 2:  # Check if the point is within the circle
                mask_x = local_center_x + x
                mask_y = local_center_y + y
                if 0 <= mask_x < fireplace["mask"].get_size()[0] and 0 <= mask_y < fireplace["mask"].get_size()[1]:
                    fireplace["mask"].set_at((mask_x, mask_y), 0)  # Turn the bit off

    """
    new_surface = pygame.Surface(fireplace["surface"].get_size(), pygame.SRCALPHA)
    new_surface.fill((0, 0, 0, 0))  # Fully transparent
    new_surface.blit(fireplace_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    fireplace["surface"] = fireplace["mask"].to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255))
    """

def detect_collisions():
    global santa_heads, current_player_image, present_list,game_data
    global current_player_mask, explosion_list
    current_level = game_data["current_level"]
    
    bag_mask = pygame.mask.from_surface(bag_image)
    
    #detect collsions between the guided missile/bag and the players star
    if game_data["guided_bag_active"] and game_data["star_active"]:
        if bag_rect.colliderect(star_rect):
            game_data["guided_bag_active"] = False
            game_data["star_active"] = False
            game_data["player_score"] += level_data[current_level]["guided_bag_points"]
            play_sound(bang_sound, bag_rect.x)
            rect = pygame.Rect(bag_rect.x,bag_rect.y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
            #spawn an explosion at this point
            current_player_image = player_image_star
            current_player_mask = pygame.mask.from_surface(player_image_star)
            explosion = { "frame":0,
                        "rect":rect,
                        "time": time.time()
                        }            
            explosion_list.append(explosion)
            
    #check between the guided missile/bag and the player:
    if game_data["guided_bag_active"]:
        offset = (bag_rect.x - player_rect.x, bag_rect.y - player_rect.y)
        if current_player_mask.overlap(bag_mask, offset):
            play_sound(bang_sound, player_rect.x)
            game_data["is_game_over"] = True
            pygame.time.wait(2000)
            return  # Exit the function immediately after ending the game
            
    #check collsions between the star and santa heads
    if game_data["star_active"]:
        for row in range(5):
            for col in range(11):
                if invaders[row][col]["active"]: #is there an active santa head here
                    invader_rect = invaders[row][col]["rect"]
                    if invader_rect.colliderect(star_rect):
                        game_data["invader_speed_add"] += .1
                        play_sound(bang_sound, invader_rect.x)
                        invaders[row][col]["active"] = False
                        invaders[row][col]["exploding"] = True
                        invaders[row][col]["explode_frame"] = 0
                        invaders[row][col]["explode_time"] = time.time()
                        game_data["star_active"] = False
                        current_player_image = player_image_star
                        current_player_mask = pygame.mask.from_surface(player_image_star)
                        game_data["player_score"] += level_data[current_level]["santa_head_points"]
                        break


    #deal only with active fireplaces                    
    active_fireplaces = [fireplace for fireplace in fireplaces if fireplace["active"]]
    
    #detect collisions between the star and fireplaces and erode the fireplaces
    if game_data["fireplaces_active"] and game_data["star_active"]:
        for fireplace in active_fireplaces:
            offset = (star_rect.x - fireplace["x"], star_rect.y - fireplace["y"])
            if fireplace["mask"].overlap(star_mask, offset):
                # Erode the fireplace
                current_player_image = player_image_star
                current_player_mask = pygame.mask.from_surface(player_image_star)
                center = (star_rect.centerx, star_rect.centery)
                erode_fireplace(fireplace, (star_rect.x, star_rect.y), explosion_graphics[0].get_width()//4)
                game_data["star_active"] = False
                x = star_rect.centerx - explosion_graphics[0].get_width()//2
                y = star_rect.centery - explosion_graphics[0].get_height()//2
                play_sound(bang_sound,x)
                rect = pygame.Rect(x,y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
                explosion = { "frame":0,
                            "rect":rect,
                            "time": time.time()
                            }            
                explosion_list.append(explosion)
                fireplace["num_hit"] += 1
                
    #now do the same check as above with the guideed santa bag/missile
    if game_data["fireplaces_active"] and game_data["guided_bag_active"]: 
        for fireplace in active_fireplaces:      
            offset = (bag_rect.x - fireplace["x"], bag_rect.y - fireplace["y"])
            if fireplace["mask"].overlap(bag_mask, offset):
                game_data["guided_bag_active"] = False
                # Play explosion sound and add visual feedback
                x = bag_rect.centerx - explosion_graphics[0].get_width() // 2
                y = bag_rect.centery - explosion_graphics[0].get_height() // 2
                play_sound(bang_sound, x)
                
                rect = pygame.Rect(
                    x, y, 
                    explosion_graphics[0].get_width(), 
                    explosion_graphics[0].get_height()
                )
                explosion = {
                    "frame": 0,
                    "rect": rect,
                    "time": time.time()
                }
                explosion_list.append(explosion)
                fireplace["num_hit"] += 1
                # Erode the fireplace where the present hit
                erode_fireplace(
                    fireplace, 
                    (bag_rect.centerx,bag_rect.centery), 
                    explosion_graphics[0].get_width() // 3
                )
                
    # Check collisions between a present and the player and fireplaces
    # Initialize a new list for remaining presents.  If a present is NOT
    #destroyed it gets added to this list
    
    remaining_presents = []

    for present in present_list:
        # Check collision with the player
        offset = (present.x - player_rect.x, present.y - player_rect.y)
        if current_player_mask.overlap(present_mask, offset):
            play_sound(bang_sound, player_rect.x)
            game_data["is_game_over"] = True
            pygame.time.wait(2000)
            return  # Exit the function immediately after ending the game
            
        # Check collision with presents and active fireplaces
        collided_with_fireplace = False
        if game_data["fireplaces_active"]:
            for fireplace in active_fireplaces:
                offset = (present.x - fireplace["x"], present.y - fireplace["y"])
                if fireplace["mask"].overlap(present_mask, offset):
                    collided_with_fireplace = True
                    
                    # Play explosion sound and add visual feedback
                    x = present.centerx - explosion_graphics[0].get_width() // 2
                    y = present.centery - explosion_graphics[0].get_height() // 2
                    play_sound(bang_sound, x)
                    
                    rect = pygame.Rect(
                        x, y, 
                        explosion_graphics[0].get_width(), 
                        explosion_graphics[0].get_height()
                    )
                    explosion = {
                        "frame": 0,
                        "rect": rect,
                        "time": time.time()
                    }
                    explosion_list.append(explosion)
                    fireplace["num_hit"] += 1
                    # Erode the fireplace where the present hit
                    erode_fireplace(
                        fireplace, 
                        (present.centerx, present.bottom), 
                        explosion_graphics[0].get_width() // 4
                    )
        # If the present didn't collide with anything, keep it in the list
        if not collided_with_fireplace:
            remaining_presents.append(present)

    # Update the present_list with the remaining presents
    present_list = remaining_presents

    remaining_presents = []
    collided_with_star = False
    #Now lets check between the star and the remaining presents.  I could
    #have done this in the loop above but it just got crazy.  This is easier to
    #read with only a minor performance hit
    if game_data["star_active"]:
        for present in present_list:
            collided_with_star = False
            if present.colliderect(star_rect):
                collided_with_star = True
                game_data["star_active"] = False
                # Play explosion sound and add visual feedback
                x = present.centerx - explosion_graphics[0].get_width() // 2
                y = present.centery - explosion_graphics[0].get_height() // 2
                play_sound(bang_sound, x)
                current_player_image = player_image_star
                current_player_mask = pygame.mask.from_surface(player_image_star)
                rect = pygame.Rect(
                    x, y, 
                    explosion_graphics[0].get_width(), 
                    explosion_graphics[0].get_height()
                )
                explosion = {
                    "frame": 0,
                    "rect": rect,
                    "time": time.time()
                }
                explosion_list.append(explosion)
            # If the present didn't collide with anything, keep it in the list
            if not collided_with_star:
                remaining_presents.append(present)
    
        present_list = remaining_presents
    
    
            
    #finally check collisions between the star and the sleigh at the top                       
    if game_data["santa_sleigh_active"] and game_data["star_active"]:
        if star_rect.colliderect(santa_sleigh_rect):
            game_data["player_score"] += level_data[current_level]["santa_sleigh_points"]
            game_data["santa_sleigh_active"] = False
            game_data["sleigh_time"] = pygame.time.get_ticks()
            game_data["star_active"] = False
            current_player_image = player_image_star
            current_player_mask = pygame.mask.from_surface(player_image_star)
            x = santa_sleigh_rect.x
            y = santa_sleigh_rect.y
            play_sound(bang_sound, x)
            rect = pygame.Rect(x,y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
            explosion = { "frame":0,
                            "rect":rect,
                            "time": time.time()
                            }            
            explosion_list.append(explosion)
    
        
def get_input():
    global current_player_image, star_active, star_rect, player_rect
    global playerpos, game_data, current_player_mask 
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= game_data["player_speed"]
        # Prevent moving off-screen
        if player_rect.x < 0:
            player_rect.x = 0

    # Move player right
    if keys[pygame.K_RIGHT]:
        player_rect.x += game_data["player_speed"]
        # Prevent moving off-screen
        if player_rect.x > SCREEN_WIDTH - player_width:
            player_rect.x = SCREEN_WIDTH - player_width
            
        # cheat code S destroys all invaders
    if keys[pygame.K_s]:
        for row in invaders:
            for invader in row:
                invader["active"] = False
        
            
    # PLayer fire shot
    if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
        if game_data["star_active"] == False:
            game_data["star_active"] = True
        current_player_image = player_image_nostar
        current_player_mask = pygame.mask.from_surface(player_image_nostar)
        play_sound(player_shoot_sound, playerpos[0])
        x = player_rect.centerx-15
        y = player_rect.y
        star_rect = pygame.Rect(x, y, star_width, star_height)
        game_data["star_active"] = True 

def check_game_end():
    global game_data
    if game_data["is_game_over"]:
        game_data["game_state"] = GAME_STATE_GAME_OVER
        game_data["game_over"] = True

def check_level_end():
    global current_level
    # Check if there are any active Santas
    has_active_invaders = any(invader["active"] for row in invaders for invader in row)
    
    if not has_active_invaders:
        # Trigger level completion or game state change
        pygame.time.wait(3000);
        start_next_level()

def start_next_level():
    global  current_player_image, current_player_mask, star_rect, invaders
    global invaders_pos, present_list, fireplaces, snowflakes
    global game_data, invader_image, invader_width, invader_height
     
    
    #assume we have not completed all levels and we will not load a
    #random enemy image
    random_image = False
    current_level = game_data["current_level"]
    game_data["invader_speed_add"] = 0

    #check if we have completed all known levels.  If so, load a random
    #enemy and use the last level data 
    if current_level < len(level_data)-1:
        current_level += 1
        game_data["current_level"] = current_level
    else:
        random_image = True # after level 5, just cycle through random images

    game_data["star_active"] = False

    #reset player images
    current_player_image = player_image_star
    current_player_mask = pygame.mask.from_surface(player_image_star)
    player_rect.x = SCREEN_WIDTH// 2 - player_width // 2
    player_rect.y = SCREEN_HEIGHT - player_height
    star_rect = star_image.get_rect()
    
    # Reset Santa sleigh
    game_data["santa_sleigh_active"] = False
    game_data["sleigh_time"] = pygame.time.get_ticks()
    
    # Reset Santa heads
    # Initialize santa_heads with dictionaries
    invaders = [
        [
        {"active": True, 
        "rect": invader_image.get_rect(),
        "exploding":False,
        "explode_frame": 0,
        "explode_time": 0} for _ in range(11)]
        for _ in range(5)
    ]
    if random_image:
        image_num = random.randint(0,len(level_data)-1)
    else:
        image_num = current_level
    #load the levels ebnemy image
    invader_image_file = level_data[image_num]["image_file"]
    invader_image = pygame.image.load(invader_image_file).convert_alpha()
    invader_image = scale_image_by(invader_image, SCALE_FACTOR, SCALE_FACTOR)
    invader_width, invader_height = invader_image.get_size()

    #reset the postion of the upper left of the enemty formation
    invaders_pos = [invader_x, 130+(game_data["current_level"]*20)*SCALE_FACTOR]
    game_data["invaders_dir"] = LEFT
    
    # Reset presents
    present_list = []
    
    # Reset fireplaces
    fireplaces = []
    for i in range (4):
        x = (gap_width * (i + 1)) + (fireplace_width * i)
        fireplace = {
            "active": True,
            "x": x,
            "y": fireplace_y,
            "num_hit": 0,
            "rect": fireplace_image.get_rect(),
            "surface": fireplace_image.copy(),
            "mask": pygame.mask.from_surface(fireplace_image),
        }
        fireplaces.append( fireplace )

    game_data["fireplaces_active"] = True
        
    game_data["guided_bag_active"] = False
    play_next_song()
        
        
    
#***********************************************************************
#*                       PYGAME INIT and setup                         *
#***********************************************************************
resolutions = [
    (1400, 1050,0.6836),
    (1600, 1200,0.78125),
    (1920, 1440,0.9375),
    (2048, 1536,1)
]

# Initialize Pygame and open a window to get screen info
pygame.init()
info = pygame.display.Info()  # Get current display info
screen_width = info.current_w
screen_height = info.current_h
max_resolution = (0, 0,0)
for width, height, scale in resolutions:
    if width <= screen_width and height <= screen_height:
        max_resolution = (width, height, scale)

#max_resolution = (1600, 1200,0.78125)
print("Best resolution for this screen:", max_resolution)
LEFT = -1
RIGHT = 1

SCREEN_WIDTH = max_resolution[0]
SCREEN_HEIGHT = max_resolution[1]
SCALE_FACTOR = max_resolution[2]

# Set up the drawing window
screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
pygame.display.set_caption("Santavaders")
#***********************************************************************
#*                       GAME STATE INFO                               *
#***********************************************************************
#constants to track game state

GAME_STATE_TITLE = 0
GAME_STATE_RUNNING = 1
GAME_STATE_END = 2
GAME_STATE_PAUSED = 3
GAME_STATE_QUIT = 4
GAME_STATE_GAME_OVER = 5
GAME_STATE_LEVEL_OVER = 6
EXPLOSION_FRAME_DURATION = 0.03



#***********************************************************************
#*                       level info                                     *
#***********************************************************************

level_data = [ { "image_file": "media/graphics/santa_saucer_smalll.png",
                "invader_speed": 2,
                "santa_sleigh_speed": 2,
                "santa_sleigh_points": 300,
                "santa_head_points": 10,
                "santa_shot_chance": 1,
                "guided_bag_points": 25,
                "present_speed": 6
                },
                
{ "image_file": "media/graphics/evil_gingerbreadman_small.png",
                "invader_speed": 3,
                "santa_sleigh_speed": 3,
                "santa_sleigh_points": 400,
                "santa_head_points": 15,
                "santa_shot_chance": 1,
                "guided_bag_points": 25,
                "present_speed": 7
                },
                
{ "image_file": "media/graphics/evil_candy_cane_small.png",
                "invader_speed": 4,
                "santa_sleigh_speed": 4,
                "santa_sleigh_points": 400,
                "santa_head_points": 15,
                "santa_shot_chance": 2,
                "guided_bag_points": 25,
                "present_speed": 7
                },
                
{ "image_file": "media/graphics/robotic_reindeer_small.png",
                "invader_speed": 6,
                "santa_sleigh_speed": 5,
                "santa_sleigh_points": 500,
                "santa_head_points": 20,
                "santa_shot_chance": 2,
                "guided_bag_points": 25,
                "present_speed": 8
                },
                
{ "image_file": "media/graphics/evil_snowman_small.png",
                "invader_speed": 8,
                "santa_sleigh_speed": 6,
                "santa_sleigh_points": 600,
                "santa_head_points": 25,
                "santa_shot_chance": 3,
                "guided_bag_points": 25,
                "present_speed": 10
                }
                ]
                
#***********************************************************************
#*                       General game info                             *
#***********************************************************************

#this keeps default game congig data
default_game_data = {   
                "game_state": GAME_STATE_RUNNING,
                "running": True,
                "player_score":0,
                "high_score":0,
                "current_level":-1, 
                "game_sound_state": True,
                "is_game_over": False,
                "fireplaces_active": True,
                "sleigh_time": 0,
                "santa_sleigh_active": False,       
                "invaders_dir": LEFT,
                "star_active": False,
                "star_speed": 15,
                "guided_bag_active": False,
                "guided_bag_speed": 8,
                "show_fps": False,
                "invader_speed_add": 0,
                "player_speed": 8
}
#we will operate on a copy of this dict and simply recopy the default 
#values when resetting the game.
game_data = dict(default_game_data)
game_data["game_state"] = GAME_STATE_TITLE #set initial game state

#***********************************************************************
#*                     SOUNDS AND MUSIC                                *
#***********************************************************************
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

santa_sleigh_sound = pygame.mixer.Sound("media/sounds/santa-claus-laughing.wav")
santa_sleigh_sound.set_volume(1)

player_shoot_sound = pygame.mixer.Sound("media/sounds/bell_shake.wav")
player_shoot_sound.set_volume(1)

santa_shoot_sound = pygame.mixer.Sound("media/sounds/santa_chuckle.wav")
santa_shoot_sound.set_volume(1)

bang_sound = pygame.mixer.Sound("media/sounds/bangMedium.wav")
bang_sound.set_volume(1)

song_list = glob.glob("./media/music/*.mp3")

pygame.mixer.music.set_volume(0.55)
pygame.mixer.set_num_channels(64)

END_MUSIC_EVENT = pygame.USEREVENT + 0   
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
pygame.mixer.music.set_endevent(END_MUSIC_EVENT)


#***********************************************************************
#*                       FONT SETUP                                    *
#***********************************************************************
# Load a custom Christmas-themed font
pygame.font.init()
font_path = "media/fonts/MountainsofChristmas-Bold.ttf"  # Replace with the path to your font file
font = pygame.font.Font(font_path, int(100*SCALE_FACTOR))  # Large font size for boldness

#***********************************************************************
#*                       TITLE IMAGES                                  *
#***********************************************************************
# Load the title screen image
title_screen_image = pygame.image.load("media/graphics/title_screen_alt.png").convert_alpha()
title_screen_image = pygame.transform.scale(title_screen_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


#***********************************************************************
#*                       PLAYER IMAGE AND SETUP                        *
#***********************************************************************

player_image_star = load_image("media/graphics/christmas_tree_star_small.png", SCALE_FACTOR, SCALE_FACTOR)
player_image_nostar = load_image("media/graphics/christmas_tree_no_star_small.png", SCALE_FACTOR, SCALE_FACTOR)
player_width, player_height = player_image_star.get_size()

player_rect = player_image_nostar.get_rect() 
current_player_mask = pygame.mask.from_surface(player_image_star)
current_player_image = player_image_star

#set inital postion and velocity
player_rect.x = SCREEN_WIDTH// 2 - player_width // 2
player_rect.y = SCREEN_HEIGHT - player_height
playerpos = [player_rect.x, player_rect.y]


#***********************************************************************
#*                       STAR/MISSILE SETUP                            *
#***********************************************************************

star_image = load_image("media/graphics/tree_star_small.png", SCALE_FACTOR, SCALE_FACTOR)
star_width, star_height = star_image.get_size()
star_rect = star_image.get_rect()
star_mask = pygame.mask.from_surface(star_image)

#***********************************************************************
#*                       SANTAS GUIDED MISSILE/BAG                     *
#***********************************************************************
bag_image = load_image("media/graphics/guided_bag_small.png", SCALE_FACTOR, SCALE_FACTOR)
bag_width, bag_height = bag_image.get_size()
bag_rect = star_image.get_rect()
bag_mask = pygame.mask.from_surface(bag_image)

#***********************************************************************
#*                       SANTA HEADS SETUP                             *
#***********************************************************************

invader_image_file = level_data[0]["image_file"]
invader_image = load_image(invader_image_file, SCALE_FACTOR, SCALE_FACTOR)
invader_width, invader_height = invader_image.get_size()

# Initialize santa_heads with dictionaries
invaders = [
    [
    {"active": True, 
    "rect": invader_image.get_rect(),
    "exploding":False,
    "explode_frame": 0,
    "explode_time": 0} for _ in range(11)]
    for _ in range(5)
]

invader_x = (SCREEN_WIDTH - ( (invader_width * 11*SCALE_FACTOR) + (invader_width//2 * 11*SCALE_FACTOR) ) )/2
invader_x = 0
invaders_pos = [invader_x, int(150*SCALE_FACTOR)]

#***********************************************************************
#*                       SANTA SLEIGH                                  *
#***********************************************************************
santa_sleigh_image = load_image("media/graphics/santa_sleigh_small.png", SCALE_FACTOR, SCALE_FACTOR)
santa_sleigh_rect = santa_sleigh_image.get_rect()

#***********************************************************************
#*                       SNOWFLAKES                                    *
#***********************************************************************

snowflakes = []  # List to hold snowflake properties
for _ in range(int(200*SCALE_FACTOR)):
    snowflakes.append({
        "x": random.randint(0, SCREEN_WIDTH),  # Random x position
        "y": random.randint(0, SCREEN_HEIGHT),  # Random y position
        "size": random.randint(2, 5),  # Random size
        "speed": random.uniform(1, 3)  # Random fall speed
    })

#***********************************************************************
#*                       FIREPLACE/SHIELDS SETUP                       *
#***********************************************************************
fireplace_image = load_image("media/graphics/fireplace_small.png", SCALE_FACTOR, SCALE_FACTOR)
fireplace_width, fireplace_height = fireplace_image.get_size()
fireplace_width, fireplace_height = fireplace_image.get_size()
fireplace_y = player_rect.y-fireplace_height-(50*SCALE_FACTOR) 

# Calculate the gap width
total_gap_space = SCREEN_WIDTH - (4 * fireplace_width)
gap_width = total_gap_space / (5*SCALE_FACTOR)


fireplaces = []
for i in range (4):
    x = (gap_width * (i + 1)) + (fireplace_width * i)
    fireplace = {
        "active": True,
        "x": x,
        "y": fireplace_y,
        "num_hit": 0,
        "rect": fireplace_image.get_rect(),
        "surface": fireplace_image.copy(),
        "mask": pygame.mask.from_surface(fireplace_image),
    }
    fireplaces.append( fireplace )


#***********************************************************************
#*                       PRESENT/ENEMY BULLETS SETUP                   *
#***********************************************************************
present_image = load_image("media/graphics/present_small.png", SCALE_FACTOR, SCALE_FACTOR)
present_mask = pygame.mask.from_surface(present_image)
present_width, present_height = present_image.get_size()
present_width, present_height = present_image.get_size()
present_list = []

#***********************************************************************
#*                       EXPLOSION GRAPHICS                            *
#***********************************************************************
explosion_graphics =[]
explosion_list = []
for i in range(7):
    filename = "media/graphics/explosion"+str(i+1)+".png"
    explosion =  load_image(filename, SCALE_FACTOR, SCALE_FACTOR)
    explosion_graphics.append(explosion)
              
#***********************************************************************
#*                       START GAME!!!                                 *
#***********************************************************************

#display_title_screen()
#time.sleep(.5)

#song = random.choice(song_list)
#pygame.mixer.music.load(song)
clock = pygame.time.Clock()
#pygame.mixer.music.play(0)
running = True
#game_data = dict(default_game_data)
game_data["game_state"] != GAME_STATE_TITLE
#reset_game(False)

while game_data["game_state"] != GAME_STATE_QUIT:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_data["game_state"] = GAME_STATE_QUIT
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_data["game_state"] = GAME_STATE_QUIT
            if event.key == pygame.K_p:
                game_data["game_state"] = GAME_STATE_PAUSED
            if event.key == pygame.K_f:
                game_data["show_fps"] = not game_data["show_fps"]
        if event.type == END_MUSIC_EVENT:
            play_next_song()
            
    if game_data["game_state"] == GAME_STATE_GAME_OVER:
        game_over()
    elif game_data["game_state"]  == GAME_STATE_PAUSED:
        display_pause_screen()
    elif game_data["game_state"]  == GAME_STATE_TITLE:
        display_title_screen()
    elif game_data["game_state"]  == GAME_STATE_RUNNING:
        get_input()
        update()
        detect_collisions()
        draw_scene()
        pygame.display.update()
        check_game_end()
        check_level_end()
        dt=clock.tick(60)

# Done! Time to quit.
print("Goodbye!!")
pygame.quit()
sys.exit()
