import pygame
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

def play_next_song():
    if pygame.mixer.music.get_busy() == False:
        song = random.choice(song_list)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(0)
        print ("Playing: +",song)
        

def display_title_screen():
    global game_state
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
        if keys[pygame.K_ESCAPE]:
            waiting = False
            game_data["game_state"] = GAME_STATE_QUIT

def reset_game():
    global santa_heads, present_list, santa_heads_pos, snowflakes, fireplaces
    global star_rect,game_data, current_player_image, current_player_mask
    
    # Reset game state
    game_data = {   "game_state": GAME_STATE_RUNNING,
                "running": True,
                "player_score":0,
                "high_score":0,
                "current_level":1,
                "game_sound_state": True,
                "is_game_over": False,
                "santa_head_points": 10,
                "present_speed": 5,
                "fireplaces_active": True,
                "sleigh_time": 0,
                "santa_sleigh_speed": 3,
                "santa_sleigh_active": False,
                "santa_heads_speed": 2,
                "santa_sleigh_points": 300,
                "santa_heads_dir": LEFT,
                "star_active": False,
                "star_speed": 8
    }
   
    current_player_image = player_image_star
    current_player_mask = pygame.mask.from_surface(player_image_star)
    star_rect = star_image.get_rect()
    # Reset Santa sleigh
    game_data["sleigh_time"] = pygame.time.get_ticks()
    
    # Reset Santa heads
    # Initialize santa_heads with dictionaries
    santa_heads = [
        [
        {"active": True, 
        "rect": santa_image.get_rect(),
        "exploding":False,
        "explode_frame": 0,
        "explode_time": 0} for _ in range(11)]
        for _ in range(5)
    ]
        
    santa_heads_pos = [santa_x, 150]
    
    # Reset presents
    present_list = []
    
    # Reset fireplaces
    fireplaces = []
    
    for i in range (4):
        x = (gap_width * (i + 1)) + (fireplace_width * i)
        fireplace = { "x": x,
                        "y": fireplace_y,
                        "rect": fireplace_image.get_rect()
                    }
        fireplaces.append( fireplace )
    fireplaces_active = True
    # Reset snowflakes
    snowflakes = []
    for _ in range(200):
        snowflakes.append({
            "x": random.randint(0, SCREEN_WIDTH),
            "y": random.randint(0, SCREEN_HEIGHT),
            "size": random.randint(2, 5),
            "speed": random.uniform(1, 3),
        })


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
    y_start = SCREEN_HEIGHT // 14  # Starting y-coordinate
      # Get height of the font and add padding

    for i, (name, score) in enumerate(high_scores):
        if name == player_name and score == player_score:
            color = (0, 255, 0)  # Highlight in green for the current player
        else:
            color = (255, 0, 0)  # Default red color

        score_text = font.render(f"{i + 1}. {name}: {score}", True, color)
        score_text= pygame.transform.scale_by(score_text, .75)
        line_height = score_text.get_height()
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_start + i * line_height))

def get_os_username():
    """Retrieve the current OS user's username."""
    return getpass.getuser()

# ***********************************************************************
# *                     GAME OVER SCREEN                     *
# ***********************************************************************

def game_over():
    global game_data
    player_name = get_os_username()  # Retrieve player username
    high_scores = load_high_scores()  # Load current high scores

    # Update the high scores with the player's score
    player_score = game_data["player_score"]
    updated_high_scores = update_high_scores(player_name, player_score, high_scores)
    save_high_scores(updated_high_scores)  # Save the updated high scores

    # Initialize snowflake properties
    snowflakes = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(0, SCREEN_HEIGHT),
                   "size": random.randint(1, 3), "speed": random.uniform(1, 3)}
                  for _ in range(100)]  # Number of snowflakes

    # Wait for user input
    waiting = True
    start_time = pygame.time.get_ticks()
    while waiting:
        screen.fill((0, 0, 0))  # Clear the screen

        # Update and draw snowflakes
        for snowflake in snowflakes:
            snowflake["y"] += snowflake["speed"]  # Move snowflake down
            if snowflake["y"] > SCREEN_HEIGHT:  # Reset snowflake if it goes off-screen
                snowflake["y"] = 0
                snowflake["x"] = random.randint(0, SCREEN_WIDTH)
                snowflake["size"] = random.randint(2, 5)
                snowflake["speed"] = random.uniform(1, 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(snowflake["x"]), int(snowflake["y"])), snowflake["size"])

        # Game Over Text with green drop shadow
        game_over_shadow = font.render("GAME OVER", True, (0, 255, 0))  # Green shadow
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))  # Red text
        screen.blit(game_over_shadow, (SCREEN_WIDTH // 2 - game_over_shadow.get_width() // 2 + 5, 10))  # Shadow offset
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 5))  # Main text

        # High Scores List
        display_high_scores(updated_high_scores, player_name, player_score)

        # Instructions
        instructions_text = font.render("Press Q to Quit or SPACE to Restart", True, (255, 255, 255))
        y_offset = instructions_text.get_height()
        screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT - y_offset))

        pygame.display.flip()

        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_data["game_state"] = GAME_STATE_QUIT
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Quit
                    game_data["game_state"] = GAME_STATE_QUIT
                    waiting = False
                if event.key == pygame.K_ESCAPE:  # Quit
                    game_data["game_state"] = GAME_STATE_QUIT
                    waiting = False
                if event.key == pygame.K_SPACE and pygame.time.get_ticks()-start_time > 2000:  # Restart
                    waiting = False
                    reset_game()


def draw_scene(fps=False):
    global santa_heads, star_rect, santa_sleigh_rect
    global player_rect, present_list, fireplaces, game_data 
    # Fill the background with black
    screen.fill((0, 0, 0))

# Draw snowflakes
    for snowflake in snowflakes:
        pygame.draw.circle(screen, (255, 255, 255), (int(snowflake["x"]), int(snowflake["y"])), snowflake["size"])
        
    player_rect = screen.blit(current_player_image, playerpos)
    #pygame.draw.rect (screen, (0,255,0), player_rect,  2)
    if game_data["star_active"]:
        star_rect = screen.blit(star_image, star_pos)
        #pygame.draw.rect (screen, (0,255,0), star_rect,  2)

    if game_data["santa_sleigh_active"]:
        santa_sleigh_rect = screen.blit(santa_sleigh_image, santa_sleigh_pos)
        #pygame.draw.rect (screen, (0,255,0), santa_sleigh_rect,  2)
        
    #draw the santa heads
    for row in range(5):
        for col in range(11):
            if santa_heads[row][col]["active"]:
                x_pos = santa_heads_pos[0] + (col*santa_width) + (santa_width//2)*col 
                y_pos = santa_heads_pos[1] + (row*santa_height ) + (santa_height//2) * row
                santa_heads[row][col]["rect"] = screen.blit(santa_image, [x_pos, y_pos] )

    #draw the santa heads exploding 
    for row in range(5):
        for col in range(11):
            if santa_heads[row][col]["exploding"]:
                if time.time() - santa_heads[row][col]["explode_time"]< EXPLOSION_FRAME_DURATION:
                    break
                frame = santa_heads[row][col]["explode_frame"]
                x_pos = santa_heads_pos[0] + (col*santa_width) + (santa_width//2)*col 
                y_pos = santa_heads_pos[1] + (row*santa_height ) + (santa_height//2) * row
                santa_heads[row][col]["rect"] = screen.blit(explosion_graphics[frame], [x_pos, y_pos] )
                frame = frame + 1
                if frame == len(explosion_graphics):
                    #frame = 0
                    santa_heads[row][col]["exploding"] = False
                santa_heads[row][col]["explode_frame"] = frame
                santa_heads[row][col]["explode_time"] = time.time()
                

                    
    #draw presents
    if len(present_list) > 0:
        for p, present in enumerate(present_list):
            present_list[p] = screen.blit(present_image, present )
            #pygame.draw.rect (screen, (0,255,0), present,  2)
            
                
    #draw fireplaces
    if game_data["fireplaces_active"]:
        for i in range(4):
            fireplaces[i]["rect"] = screen.blit(fireplace_image, [ fireplaces[i]["x"], fireplaces[i]["y"] ] )
        
    # Render the score text with a shadow effect
    player_score = game_data["player_score"]
    score_text = font.render(f"Score: {player_score}", True, (255, 0, 0))  # White text
    shadow_text = font.render(f"Score: {player_score}", True, (0, 128, 0))  # Green shadow
    
    #shrink the score text by 75%
    score_text = pygame.transform.scale_by(score_text, (.75, .75)) 
    shadow_text = pygame.transform.scale_by(shadow_text, (.75, .75)) 
    # Calculate text width and positions
    text_width = score_text.get_width()
    x_position = SCREEN_WIDTH - text_width - 20
    y_position = 50
    # Draw shadow slightly offset
    screen.blit(shadow_text, (x_position + 5, y_position + 5))
    # Draw the main text
    screen.blit(score_text, (x_position, y_position))

    # Render the level text with a shadow effect
    current_level = game_data["current_level"]
    level_text = font.render(f"Level: {current_level}", True, (255, 0, 0))  # White text
    shadow_text = font.render(f"Level: {current_level}", True, (0, 128, 0))  # Green shadow
    
    level_text = pygame.transform.scale_by(level_text, (.75, .75)) 
    shadow_text = pygame.transform.scale_by(shadow_text, (.75, .75)) 
    # Calculate text width and positions
    text_width = level_text.get_width()
    x_position = 20
    y_position = 50
    # Draw shadow slightly offset
    screen.blit(shadow_text, (x_position + 5, y_position + 5))
    # Draw the main text
    screen.blit(level_text, (x_position, y_position))

    # draw other explosions
    for explosion in explosion_list:
        image_num = explosion["frame"]
        image = explosion_graphics[image_num]
        rect = explosion["rect"]
        screen.blit(image, rect)


    #draw FPSscreen.blit(playerimage, playerpos)
    if fps:
        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("coral"))
        screen.blit(fps_text, (10,SCREEN_HEIGHT-fps_text.get_height()))
        

        
def update():
    global star_pos, current_player_image, santa_sleigh_pos, snowflakes
    global present_list, santa_sleigh_sound, game_data, explosion_list
    global current_player_mask
      
    if not game_data["santa_sleigh_active"]:
        if pygame.time.get_ticks() - game_data["sleigh_time"] > 10000:
            if random.randint(1,101) < 2:
                game_data["santa_sleigh_active"] = True
                santa_sleigh_pos = [0,20]
                play_sound(santa_sleigh_sound,SCREEN_WIDTH/2)
                #santa_sleigh_sound.play()
    else:
        santa_sleigh_pos[0] += game_data["santa_sleigh_speed"]
        if santa_sleigh_pos[0] > SCREEN_WIDTH:
            game_data["santa_sleigh_active"] = False
            santa_sleigh_sound.stop()
            game_data["sleigh_time"] = pygame.time.get_ticks()
        
    if game_data["star_active"]:
        star_pos[1] -= game_data["star_speed"]
        if star_pos[1]<=0:
            game_data["star_active"] = False
            current_player_image = player_image_star
            current_playher_mask = pygame.mask.from_surface(player_image_star)
    
    #update presents 
    present_list = [present for present in present_list if present.y <= SCREEN_HEIGHT]
    for present in present_list:
        present.y += game_data["present_speed"]

    #update explosions
    for explosion in reversed(explosion_list):
        if time.time() - explosion["time"] > EXPLOSION_FRAME_DURATION:
            explosion["frame"] += 1
            if explosion["frame"] == len(explosion_graphics):
                explosion_list.remove(explosion)
                continue
            explosion["time"] = time.time()
                        
    # Generate a random Santa present
    active_santas = [(row, col) for row in range(5) for col in range(11) if santa_heads[row][col]["active"]]
    if active_santas and random.randint(0, 100) == 0:
        row, col = random.choice(active_santas)
        rect = santa_heads[row][col]["rect"]
        play_sound(santa_shoot_sound, rect.x)
        present_list.append(rect)
    
    # Check Santa head movement limits and reverse direction if necessary
    reverse_direction = False

    for row in range(len(santa_heads)):
        for col in range(len(santa_heads[row])):
            if santa_heads[row][col]["active"]:  # Check if Santa head is active
                santa_rect = santa_heads[row][col]["rect"]
                if santa_rect.x <= 5 or santa_rect.x + santa_width >= SCREEN_WIDTH:
                    reverse_direction = True
                    break
        if reverse_direction:
            break

    if reverse_direction:
        game_data["santa_heads_dir"] *= -1  # Reverse direction
        santa_heads_pos[1] += 15  # Move Santa heads down
        
    #move the santa head position
    santa_heads_pos[0] += game_data["santa_heads_speed"] * game_data["santa_heads_dir"]
        
    # Update snowflakes
    for snowflake in snowflakes:
        snowflake["y"] += snowflake["speed"]  # Move snowflake down
        if snowflake["y"] > SCREEN_HEIGHT:  # If it goes off-screen
            snowflake["y"] = 0  # Reset to the top
            snowflake["x"] = random.randint(0, SCREEN_WIDTH)  # Random x position
            snowflake["size"] = random.randint(2, 5)  # Random size
            snowflake["speed"] = random.uniform(1, 3)  # Random speed
            
    # Check for lowest alien reaching fireplace or player Y-coordinate
    for row in range(4, -1, -1):  # Iterate rows in reverse (4 to 0)
        for col in range(11):
            if santa_heads[row][col]["active"]:  # Check if the alien is active
                alien_x = santa_heads_pos[0] + (col * santa_width) + (santa_width // 2) * col
                alien_y = santa_heads_pos[1] + (row * santa_height) + (santa_height // 2) * row
                alien_bottom = alien_y + santa_height

                if alien_bottom >= playerpos[1]:  # Game Over Condition
                    print("GAME OVER!!!")
                    is_game_over = True
                    return  # Exit immediately

                if game_data["fireplaces_active"] and alien_bottom >= fireplace_y:  # Fireplace Condition
                    game_data["fireplaces_active"] = False
                    return  # Exit immediately after deactivating fireplaces
    
            
def detect_collisions():
    global santa_heads, current_player_image, present_list,game_data
    global current_player_mask, explosion_list
    
    #check collsions between the star and santa heads
    if game_data["star_active"]:
        for row in range(5):
            for col in range(11):
                if santa_heads[row][col]["active"]: #is there an active santa head here
                    santa_rect = santa_heads[row][col]["rect"]
                    if santa_rect.colliderect(star_rect):
                        game_data["santa_heads_speed"] += .1
                        play_sound(bang_sound, santa_rect.x)
                        santa_heads[row][col]["active"] = False
                        santa_heads[row][col]["exploding"] = True
                        santa_heads[row][col]["explode_frame"] = 0
                        santa_heads[row][col]["explode_time"] = time.time()
                        game_data["star_active"] = False
                        current_player_image = player_image_star
                        current_player_mask = pygame.mask.from_surface(player_image_star)
                        game_data["player_score"] += game_data["santa_head_points"]
                        break
                        
    #check collision between the star and fireplaces
        if game_data["fireplaces_active"]:
            for fireplace in fireplaces:
                if star_rect.colliderect(fireplace["rect"]):
                    game_data["star_active"] = False
                    x = star_rect.x - explosion_graphics[0].get_width()//2
                    y = star_rect.y - explosion_graphics[0].get_height()//2
                    play_sound(bang_sound,x)
                    rect = pygame.Rect(x,y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
                    explosion = { "frame":0,
                                "rect":rect,
                                "time": time.time()
                                }            
                    explosion_list.append(explosion)
                    break
    #check colliosions between a present and the player and fireplaces
    # Initialize a new list for remaining presents
    remaining_presents = []

    for present in present_list:
        # Check collision with the player
        offset = (present.x - player_rect.x, present.y - player_rect.y)
        #if present.colliderect(player_rect):
        if current_player_mask.overlap(present_mask, offset):
            print("GAME OVER!!!")
            play_sound(bang_sound, player_rect.x)
            game_data["is_game_over"] = True
            pygame.time.wait(2000)
            return  # Exit the function immediately after ending the game

        # Check collision with presents and fireplaces
        collided_with_fireplace = False
        if game_data["fireplaces_active"]:
            collided_with_fireplace = False
            for fireplace in fireplaces:
                if present.colliderect(fireplace["rect"]):
                    collided_with_fireplace = True
                    x = present.x - explosion_graphics[0].get_width()//2
                    y = present.y - explosion_graphics[0].get_height() //2
                    play_sound(bang_sound,x)
                    rect = pygame.Rect(x,y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
                    explosion = { "frame":0,
                                "rect":rect,
                                "time": time.time()
                                }            
                    explosion_list.append(explosion)
                    break  # Stop checking once a collision is detected

        # If the present didn't collide with anything, keep it in the list
        if not collided_with_fireplace:
            remaining_presents.append(present)

    # Update the present_list with the remaining presents
    present_list = remaining_presents
            
    #finally check collisions between the star and the sleigh at the top                       
    if game_data["santa_sleigh_active"] and game_data["star_active"]:
        if star_rect.colliderect(santa_sleigh_rect):
            game_data["player_score"] += game_data["santa_sleigh_points"]
            game_data["santa_sleigh_active"] = False
            game_data["sleigh_time"] = pygame.time.get_ticks()
            game_data["star_active"] = False
            current_player_image = player_image_star
            current_player_mask = pygame.mask.from_surface(player_image_star)
            x = santa_sleigh_rect.x
            y = santa_sleigh_rect.y
            rect = pygame.Rect(x,y, explosion_graphics[0].get_width(), explosion_graphics[0].get_height())
            explosion = { "frame":0,
                            "rect":rect,
                            "time": time.time()
                            }            
            explosion_list.append(explosion)
    
        
def get_input():
    global current_player_image, star_active, star_pos, star_rect
    global playerpos, game_data, current_player_mask 
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        playerpos[0] -= player_speed
        # Prevent moving off-screen
        if playerpos[0] < 0:
            playerpos[0] = 0

    # Move player right
    if keys[pygame.K_RIGHT]:
        playerpos[0] += player_speed
        # Prevent moving off-screen
        if playerpos[0] > SCREEN_WIDTH - player_width:
            playerpos[0] = SCREEN_WIDTH - player_width
            
    # PLayer fire shot
    if keys[pygame.K_SPACE]:
        if game_data["star_active"] == False:
            game_data["star_active"] = True
        current_player_image = player_image_nostar
        current_player_mask = pygame.mask.from_surface(player_image_nostar)
        play_sound(player_shoot_sound, playerpos[0])
        #player_shoot_sound.play()
        star_pos = [playerpos[0]+53, playerpos[1]]
        star_rect = pygame.Rect(star_pos[0], star_pos[1], star_width, star_height)
        game_data["star_active"] = True 

def check_game_end():
    global game_data
    if game_data["is_game_over"]:
        game_data["game_state"] = GAME_STATE_GAME_OVER
        game_data["game_over"] = True

def check_level_end():
    global current_level
    # Check if there are any active Santas
    has_active_santas = any(santa["active"] for row in santa_heads for santa in row)

    if not has_active_santas:
        print("No more active Santas!")
        # Trigger level completion or game state change
        start_next_level()

def start_next_level():
    global  current_player_image, current_player_mask, star_rect,  santa_heads
    global santa_heads_pos, present_list, fireplaces, snowflakes
    global game_data
     
    
    pygame.time.wait(3000);
    game_data["current_level"] = min(game_data["current_level"]+1, 10)
    santa_heads_speed = 2 + game_data["current_level"]*2
    game_data["star_active"] = False

    current_player_image = player_image_star
    current_player_mask = pygame.mask.from_surface(player_image_star)
    star_rect = star_image.get_rect()
    
    # Reset Santa sleigh
    game_data["santa_sleigh_active"] = False
    game_data["sleigh_time"] = pygame.time.get_ticks()
    
    # Reset Santa heads
    # Initialize santa_heads with dictionaries
    santa_heads = [
        [
        {"active": True, 
        "rect": santa_image.get_rect(),
        "exploding":False,
        "explode_frame": 0,
        "explode_time": 0} for _ in range(11)]
        for _ in range(5)
    ]

    santa_heads_pos = [santa_x, 150+(game_data["current_level"]*10)]
    game_data["santa_heads_dir"] = LEFT
    
    game_data["santa_sleigh_speed"] += 2
    game_data["santa_sleigh_points"] += 100
    game_data["santa_head_points"] += 5
    # Reset presents
    present_list = []
    
    # Reset fireplaces
    fireplaces = []
    for i in range (4):
        x = (gap_width * (i + 1)) + (fireplace_width * i)
        fireplace = { "x": x,
                        "y": fireplace_y,
                        "rect": fireplace_image.get_rect()
                    }
        fireplaces.append( fireplace )

    game_data["fireplaces_active"] = True
    # Reset snowflakes
    snowflakes = []
    for _ in range(200):
        snowflakes.append({
            "x": random.randint(0, SCREEN_WIDTH),
            "y": random.randint(0, SCREEN_HEIGHT),
            "size": random.randint(2, 5),
            "speed": random.uniform(1, 3),
        })
    #game_data["game_state"] = GAME_STATE_RUNNING
    #game_data["is_game_over"] = False
        
        
    
#***********************************************************************
#*                       PYGAME INIT and setup                         *
#***********************************************************************
pygame.init()
LEFT = -1
RIGHT = 1

SCREEN_WIDTH = 2048
SCREEN_HEIGHT = 1536
# Set up the drawing window
screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
pygame.display.set_caption("Santavaders")
pygame.key.set_repeat()

#***********************************************************************
#*                     SOUNDS AND MUSIC                                *
#***********************************************************************
pygame.mixer.init()

santa_sleigh_sound = pygame.mixer.Sound("media/sounds/santa-claus-laughing.ogg")
santa_sleigh_sound.set_volume(1)

player_shoot_sound = pygame.mixer.Sound("media/sounds/bell_shake.ogg")
player_shoot_sound.set_volume(1)

santa_shoot_sound = pygame.mixer.Sound("media/sounds/santa_chuckle.ogg")
santa_shoot_sound.set_volume(1)

bang_sound = pygame.mixer.Sound("media/sounds/bangmedium.ogg")
bang_sound.set_volume(1)



song_list = glob.glob("./media/music/*.mp3")

pygame.mixer.music.set_volume(0.25)
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
font = pygame.font.Font(font_path, 100)  # Large font size for boldness


#***********************************************************************
#*                       TITLE IMAGES                                  *
#***********************************************************************
# Load the title screen image
title_screen_image = pygame.image.load("media/graphics/title_screen.png")
title_screen_image = pygame.transform.scale(title_screen_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


#***********************************************************************
#*                       PLAYER IMAGE AND SETUP                        *
#***********************************************************************

player_image_star = pygame.image.load("media/graphics/treewstar_small.png")
player_image_nostar = pygame.image.load("media/graphics/treenostar_small.png")

player_width, player_height = player_image_star.get_size()
player_rect = player_image_nostar.get_rect() 

current_player_mask = pygame.mask.from_surface(player_image_star)
current_player_image = player_image_star

#set inital postion and velocity
playerpos = [SCREEN_WIDTH// 2 - player_width // 2, SCREEN_HEIGHT - player_height]
player_speed = 5

#***********************************************************************
#*                       STAR/MISSILE SETUP                            *
#***********************************************************************
#star_active = False
star_image = pygame.image.load("media/graphics/star_small.png")
star_width, star_height = star_image.get_size()
star_rect = star_image.get_rect()
star_pos = [0,0]
#star_speed = 8


#***********************************************************************
#*                       SANTA HEADS SETUP                             *
#***********************************************************************

santa_image = pygame.image.load("media/graphics/santa_head_small.png")
santa_width, santa_height = santa_image.get_size()

# Initialize santa_heads with dictionaries
santa_heads = [
    [
    {"active": True, 
    "rect": santa_image.get_rect(),
    "exploding":False,
    "explode_frame": 0,
    "explode_time": 0} for _ in range(11)]
    for _ in range(5)
]

santa_x = (SCREEN_WIDTH - ( (santa_width * 11) + (santa_width//2 * 11) ) )/2
santa_heads_pos = [santa_x, 130]

#***********************************************************************
#*                       SANTA SLEIGH                                  *
#***********************************************************************
santa_sleigh_image = pygame.image.load("media/graphics/santa_sleigh_small.png")
santa_sleigh_pos = [0,20]
santa_sleigh_rect = santa_sleigh_image.get_rect()
#sleigh_time = pygame.time.get_ticks()


#***********************************************************************
#*                       SNOWFLAKE AREAS                               *
#***********************************************************************

snowflakes = []  # List to hold snowflake properties
for _ in range(150):
    snowflakes.append({
        "x": random.randint(0, SCREEN_WIDTH),  # Random x position
        "y": random.randint(0, SCREEN_HEIGHT),  # Random y position
        "size": random.randint(2, 5),  # Random size
        "speed": random.uniform(1, 3)  # Random fall speed
    })

#***********************************************************************
#*                       FIREPLACE/SHIELDS SETUP                       *
#***********************************************************************
fireplace_image = pygame.image.load("media/graphics/fireplace_small.png")
fireplace_width, fireplace_height = fireplace_image.get_size()
fireplace_width, fireplace_height = fireplace_image.get_size()
fireplace_y = playerpos[1]-fireplace_height-50 

# Calculate the gap width
total_gap_space = SCREEN_WIDTH - (4 * fireplace_width)
gap_width = total_gap_space / (4 + 1)


fireplaces = []
for i in range (4):
    x = (gap_width * (i + 1)) + (fireplace_width * i)
    fireplace = { "x": x,
                    "y": fireplace_y,
                    "rect": fireplace_image.get_rect()
                }
    fireplaces.append( fireplace )
#fireplaces_active = True


#***********************************************************************
#*                       PRESENT/ENEMY BULLETS SETUP                   *
#***********************************************************************
present_image = pygame.image.load("media/graphics/present_small.png")
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
    print(filename)
    explosion =  pygame.image.load(filename)
    explosion_graphics.append(explosion)

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

game_state = GAME_STATE_TITLE #set initial game state
# Run until the user asks to quit
running = True


 
#***********************************************************************
#*                       General game info                             *
#***********************************************************************


game_data = {   "game_state": GAME_STATE_RUNNING,
                "running": True,
                "player_score":0,
                "high_score":0,
                "current_level":1,
                "game_sound_state": True,
                "is_game_over": False,
                "santa_head_points": 10,
                "present_speed": 5,
                "fireplaces_active": True,
                "sleigh_time": 0,
                "santa_sleigh_speed": 3,
                "santa_sleigh_active": False,
                "santa_heads_speed": 2,
                "santa_sleigh_points": 300,
                "santa_heads_dir": LEFT,
                "star_active": False,
                "star_speed": 8
}
                
                
                
                
                
                
#***********************************************************************
#*                       START GAME!!!                                 *
#***********************************************************************

display_title_screen()
time.sleep(.5)

song = random.choice(song_list)
pygame.mixer.music.load(song)
clock = pygame.time.Clock()
clock.tick(10)
pygame.mixer.music.play(0)
clock.tick(10)

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
        draw_scene(True)
        pygame.display.update()
        check_game_end()
        check_level_end()
        dt=clock.tick(60)

# Done! Time to quit.
print("Goodbye!!")
pygame.quit()
sys.exit()
