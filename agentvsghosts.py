    
def run_game():

    import pygame
    import sys
    import os
    import random
    import math

    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width = 800
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("AGENT V.S. GHOSTS")

    # Define tan and brown colors
    tan = (210, 180, 140)
    brown = (61, 39, 24)

    # Define square size
    square_size = 20

    # Define character size
    character_size = 50  

    # Define bullet size
    bullet_size = 10

    # Define enemy size
    enemy_size = 50

    # Define character class
    class Character(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.image.load("images/agent.png")
            self.image = pygame.transform.scale(self.image, (character_size, character_size))
            self.rect = self.image.get_rect()
            self.rect.center = (screen_width // 2, screen_height // 2)
            self.speed = 4
            self.last_lightning_spawn_time = 0  # Initialize the attribute

        def update(self, keys):
            if keys[pygame.K_w] and self.rect.y > 0:
                self.rect.y -= self.speed
            if keys[pygame.K_s] and self.rect.y < screen_height - character_size:
                self.rect.y += self.speed
            if keys[pygame.K_a] and self.rect.x > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_d] and self.rect.x < screen_width - character_size:
                self.rect.x += self.speed

    # Define bullet class
    class Bullet(pygame.sprite.Sprite):
        def __init__(self, character_rect, direction):
            super().__init__()
            self.image = pygame.image.load("images/bullet.png")
            self.image = pygame.transform.scale(self.image, (bullet_size, bullet_size))
            self.rect = self.image.get_rect()
            self.rect.centerx = character_rect.centerx
            self.rect.centery = character_rect.centery
            self.speed = 10
            self.direction = direction

        def update(self):
            if self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "right":
                self.rect.x += self.speed
            elif self.direction == "up":
                self.rect.y -= self.speed
            elif self.direction == "down":
                self.rect.y += self.speed

    # Define a global variable to store the enemy location
    enemy_location = (0, 0)

    # Define enemy class
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, target, allies):
            super().__init__()
            self.image = pygame.image.load("images/enemy.png")
            self.image = pygame.transform.scale(self.image, (enemy_size, enemy_size))
            self.rect = self.image.get_rect()
            self.speed = 6
            self.target = target
            self.allies = allies

            # Set initial position along the border
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                self.rect.centerx = random.randint(0, screen_width)
                self.rect.y = -enemy_size
            elif side == "bottom":
                self.rect.centerx = random.randint(0, screen_width)
                self.rect.y = screen_height
            elif side == "left":
                self.rect.x = -enemy_size
                self.rect.centery = random.randint(0, screen_height)
            elif side == "right":
                self.rect.x = screen_width
                self.rect.centery = random.randint(0, screen_height)

        def update(self):
            global enemy_location
            global infected

            dx_char = self.target.rect.centerx - self.rect.centerx
            dy_char = self.target.rect.centery - self.rect.centery
            dist_char = math.hypot(dx_char, dy_char)

            # Calculate distance to each ally and find the nearest one
            nearest_ally = None
            nearest_dist_ally = float('inf')

            for ally in self.allies:
                dx_ally = ally.rect.centerx - self.rect.centerx
                dy_ally = ally.rect.centery - self.rect.centery
                dist_ally = math.hypot(dx_ally, dy_ally)

                if dist_ally < nearest_dist_ally:
                    nearest_ally = ally
                    nearest_dist_ally = dist_ally

            # Choose the target based on distance
            if nearest_dist_ally < dist_char:
                dx = nearest_ally.rect.centerx - self.rect.centerx
                dy = nearest_ally.rect.centery - self.rect.centery
            else:
                dx = dx_char
                dy = dy_char

            angle = math.atan2(dy, dx)
            self.rect.x += self.speed * math.cos(angle)
            self.rect.y += self.speed * math.sin(angle)

            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx) 

            # Check for collision with bullets
            bullet_collisions = pygame.sprite.spritecollide(self, bullets, True)
            if bullet_collisions:
                self.kill()  # Remove the enemy 
                scoreboard.increment_score()  # Increment the score

                if infected:
                    ally = Ally(enemy_location)
                    allies.add(ally)

                # Update the global variable with the enemy's current location
                enemy_location = (self.rect.x, self.rect.y)

            # Check for collision with the character
            player_collisions = self.target.rect.colliderect(self)
            if player_collisions:
                self.kill()  # Remove the enemy
                
                if len(shields) == 0:
                    hearts.remove(hearts.sprites()[-1])  # Remove a heart    
                else:
                    shields.remove(shields.sprites()[-1])  # Remove a shield
            
            # Check for collision with allies
            ally_collisions = pygame.sprite.spritecollide(self, self.allies, True)
            if ally_collisions:
                self.kill()  # Remove the enemy

            # Game over condition
            if len(hearts) == 0:
                game_over = True
                game_start = False
                end_screen = True
                show_game_over(scoreboard.score)
        
    # Define scoreboard class
    class Scoreboard:
        def __init__(self):
            self.score = 0
            self.font = pygame.font.SysFont('courier new', 42, bold=True)
            self.text_width = 0
            self.text_height = 0

        def increment_score(self):
            self.score += 1

        def update_text_dimensions(self):
            score_text = self.font.render("Score: {}".format(self.score), True, (0, 0, 0))
            self.text_width, self.text_height = score_text.get_size()    

        def draw(self):
            score_text = self.font.render("Score: {}".format(self.score), True, (0, 0, 0))
            x = (screen_width - self.text_width) // 2
            y = 10
            screen.blit(score_text, (x, y))


    # Define the heart class
    class Heart(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.image.load("images/heart.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    # Define the lightning class
    class Lightning(pygame.sprite.Sprite):
        def __init__(self, character):
            super().__init__()
            self.image = pygame.image.load("images/lightning.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.center = (random.randint(0, screen_width), random.randint(0, screen_height))
            self.character = character
            self.active = False
            self.start_time = pygame.time.get_ticks()

        def update(self):
            if not self.active and pygame.sprite.collide_rect(self, self.character):
                self.active = True
                self.character.speed *= 2  # Speed up the character

            if self.active and pygame.time.get_ticks() - self.start_time >= 5000:
                self.character.speed /= 2  # Restore the character's normal speed
                self.active = False  # Despawn the lightning
                self.kill()

            if pygame.time.get_ticks() - self.start_time >= 7000:
                self.active = False  # Despawn the lightning
                self.kill()

    # Define the cannon class
    class Cannon(pygame.sprite.Sprite):
        def __init__(self, character, bullets):
            super().__init__()
            self.image = pygame.image.load("images/cannon.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.center = (random.randint(0, screen_width), random.randint(0, screen_height))
            self.character = character
            self.bullets = bullets
            self.active = False
            self.start_time = pygame.time.get_ticks()

        def update(self):
            
            global four_bullet # Add this line to modify the global variable

            if not self.active and pygame.sprite.collide_rect(self, self.character):
                self.active = True
                four_bullet = True

            if self.active and pygame.time.get_ticks() - self.start_time >= 5000:
                self.active = False  # Despawn the cannon
                four_bullet = False
                self.kill()

            if pygame.time.get_ticks() - self.start_time >= 7000:
                self.active = False  # Despawn the cannon
                self.kill()

    # Define the bomb class
    class Bomb(pygame.sprite.Sprite):
        def __init__(self, character, enemy):
            super().__init__()
            self.image = pygame.image.load("images/bomb.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.normal = pygame.image.load("images/bomb.png")
            self.normal = pygame.transform.scale(self.normal, (40, 40))
            self.exploding = pygame.image.load("images/bomb_exploding.png")
            self.exploding = pygame.transform.scale(self.exploding, (40, 40))

            self.rect = self.image.get_rect()
            self.rect.center = (random.randint(0, screen_width), random.randint(0, screen_height))
            self.character = character
            self.enemies = enemies
            self.active = False
            self.start_time = pygame.time.get_ticks()

        def update(self):

            if not self.active and pygame.sprite.collide_rect(self, self.character):
                self.image = self.exploding
                self.active = True

            if self.active and pygame.time.get_ticks() - self.start_time >= 5000:
                # Kill enemies currently spawned
                for enemy in self.enemies:
                    enemy.kill()

                self.image = self.normal
                self.active = False  # Despawn the bomb
                self.kill()

            if pygame.time.get_ticks() - self.start_time >= 7000:
                self.active = False  # Despawn the bomb
                self.kill()

    # Define ally class
    class Ally(pygame.sprite.Sprite):
        def __init__(self, spawn_location):
            super().__init__()
            self.image = pygame.image.load("images/zombie.png")
            self.image = pygame.transform.scale(self.image, (character_size, character_size))
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = spawn_location
            self.speed = 1

        def update(self, keys):
            if keys[pygame.K_w] and self.rect.y > 0:
                self.rect.y -= self.speed
            if keys[pygame.K_s] and self.rect.y < screen_height - character_size:
                self.rect.y += self.speed
            if keys[pygame.K_a] and self.rect.x > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_d] and self.rect.x < screen_width - character_size:
                self.rect.x += self.speed
            

    class Infection(pygame.sprite.Sprite):
        def __init__(self, character):
            super().__init__()
            self.image = pygame.image.load("images/poison.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.center = (random.randint(0, screen_width), random.randint(0, screen_height))
            self.character = character
            self.active = False
            self.start_time = pygame.time.get_ticks()

        def update(self):

            global infected # A global boolean infected

            if not self.active and pygame.sprite.collide_rect(self, self.character):
                self.active = True
                infected = True

            if self.active and pygame.time.get_ticks() - self.start_time >= 5000:
                self.active = False  # Despawn the poison
                infected = False
                self.kill()       

            if pygame.time.get_ticks() - self.start_time >= 7000:
                self.active = False  # Despawn the poison
                self.kill()
            

    class Barrier(pygame.sprite.Sprite):
        def __init__(self, character):
            super().__init__()
            self.image = pygame.image.load("images/barrier.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.center = (random.randint(0, screen_width), random.randint(0, screen_height))
            self.character = character
            self.active = False
            self.start_time = pygame.time.get_ticks()
            self.shield_spacing = 50
            self.shield_start_x = 20
            self.shield_start_y = 20

        def update(self):

            if not self.active and pygame.sprite.collide_rect(self, self.character):
                self.active = True

                if len(shields) < 3:
                    # Create a shield sprite and add it to the shields group
                    shield = Shield(self.shield_start_x + len(shields) * self.shield_spacing, self.shield_start_y)
                    shields.add(shield)

            if self.active and pygame.time.get_ticks() - self.start_time >= 5000:
                self.active = False  # Despawn the barrier
                self.kill()

            if pygame.time.get_ticks() - self.start_time >= 7000:
                self.active = False  # Despawn the barrier
                self.kill()


    # Define the shield class
    class Shield(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.image.load("images/shield.png")
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    # Create character sprite
    character = Character()

    # Create a sprite group for bullets
    bullets = pygame.sprite.Group()

    # Create enemy sprite group
    enemies = pygame.sprite.Group()

    # Create scoreboard
    scoreboard = Scoreboard()
    scoreboard.update_text_dimensions()

    # Create heart sprite group
    hearts = pygame.sprite.Group()

    # Create a lightning group
    lightnings = pygame.sprite.Group()

    # Create a cannon group
    cannons = pygame.sprite.Group()

    # Create a bomb group
    bombs = pygame.sprite.Group()

    # Create a infection group
    infections = pygame.sprite.Group() 

    # Create an ally group
    allies = pygame.sprite.Group()

    # Create a barrier group
    barriers = pygame.sprite.Group()

    # Create a shield group
    shields = pygame.sprite.Group()

    # Create hearts
    heart_spacing = 50
    heart_start_x = (screen_width - 60)
    heart_start_y = 20
    for i in range(3):
        heart = Heart(heart_start_x - i * heart_spacing, heart_start_y)
        hearts.add(heart)

    # Flag to track if a bullet has been fired
    bullet_fired = False

    # Track time for enemy spawning
    spawn_timer = pygame.time.get_ticks()
    spawn_delay = 3000  # 3000 milliseconds = 3 seconds

    # Time speedup interval for the enemies
    spawn_speedup_interval = 30000  # 30000 milliseconds = 30 seconds
    spawn_speedup_percentage = 0.03  # 3% faster spawn rate

    # Power up spawn time 
    power_up_timer = pygame.time.get_ticks()
    power_up_spawn = 10000 # 10000 milliseconds = 10 seconds

    # A function that displays the menu
    def show_menu():
        
        # Create a new Pygame window for the menu screen
        menu_screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AGENT V.S. GHOSTS")

        # Fill the background with a color
        menu_screen.fill((255, 255, 255))

        # Create a font for the AGENT V.S. GHOSTS game message
        font = pygame.font.SysFont('courier new', 64, bold=True)

        # Create a font for the start message
        start_font = pygame.font.SysFont('courier new', 48, bold=True)

        # Render the AGENT V.S. GHOSTS game message
        menu_text = font.render("AGENT V.S. GHOSTS", True, (0, 0, 0))
        menu_text_rect = menu_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))

        # Render the start message
        start_text = start_font.render("Press Enter To Start", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

        # Blit the text onto the screen
        menu_screen.blit(menu_text, menu_text_rect)
        menu_screen.blit(start_text, start_text_rect)

        # Update the display
        pygame.display.flip()


    # A function that displays the game over window
    def show_game_over(score):
        # Create a new Pygame window for the game over screen
        game_over_screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AGENT V.S. GHOSTS")

        # Fill the background with a color
        game_over_screen.fill((255, 255, 255))

        # Create a font for the game over message
        font = pygame.font.SysFont('courier new', 64, bold=True)

        # Create a font for the start message
        start_font = pygame.font.SysFont('courier new', 48, bold=True)

        # Render the game over message
        game_over_text = font.render("Game Over", True, (0, 0, 0))
        game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))

        # Render the score message
        score_text = font.render("Score: {}".format(score), True, (0, 0, 0))
        score_text_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

        # Render the start message
        start_text = start_font.render("Press Enter To Restart", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

        # Blit the text onto the screen
        game_over_screen.blit(game_over_text, game_over_text_rect)
        game_over_screen.blit(score_text, score_text_rect)
        game_over_screen.blit(start_text, start_text_rect)

        # Update the display
        pygame.display.flip()

    # ============= START OF GAME LOOP ================ #

    # Initialize the infected flag
    infected = False

    # Initialize the four bullet flag
    four_bullet = False

    # Initialize the game running flag
    game_running = True

    # Initialize the game over flag
    game_over = False

    # Initialize the game start flag
    game_start = False

    # Initialize the end screen flag
    end_screen = False

    # Initialize the menu screen flag
    menu_screen = False

    # Clock to create a constant fps
    clock = pygame.time.Clock()

    # Game loop
    while game_running:

        # Set FPS to 60 
        clock.tick(60)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Check if Enter key is pressed
                    if menu_screen:
                        menu_screen = False
                        game_start = True

                    elif game_over:
                        game_over = False
                        game_start = True
                        end_screen = False

                        # Reset the game by re-initializing variables and objects
                        character = Character()
                        bullets.empty()
                        enemies.empty()
                        scoreboard.score = 0
                        scoreboard.update_text_dimensions()
                        spawn_timer = pygame.time.get_ticks()
                        pygame.display.set_caption("AGENT V.S. GHOSTS")

                        # Clear the hearts group before adding new hearts
                        hearts.empty()

                        # Create hearts
                        heart_spacing = 50
                        heart_start_x = (screen_width - 60)
                        heart_start_y = 20
                        for i in range(3):
                            heart = Heart(heart_start_x - i * heart_spacing, heart_start_y)
                            hearts.add(heart)
                        
                        # Reset powerups
                        lightnings.empty()
                        cannons.empty()
                        bombs.empty()
                        infections.empty()
                        allies.empty()
                        barriers.empty()
                        shields.empty()

                        # Track time for enemy spawning
                        spawn_timer = pygame.time.get_ticks()
                        spawn_delay = 3000  # 3000 milliseconds = 3 seconds

                        # Time speedup interval for the enemies
                        spawn_speedup_interval = 30000  # 30000 milliseconds = 30 seconds
                        spawn_speedup_percentage = 0.03  # 3% faster spawn rate

                        # Power up spawn time 
                        power_up_timer = pygame.time.get_ticks()
                        power_up_spawn = 10000 # 10000 milliseconds = 10 seconds
                    

        if not game_over and game_start:
        
            # Handle keyboard input for character
            keys = pygame.key.get_pressed()
            character.update(keys)

            # Shooting logic
            if keys[pygame.K_UP] and not bullet_fired and not four_bullet:
                bullet = Bullet(character.rect, "up")
                bullets.add(bullet)
                bullet_fired = True
            if keys[pygame.K_DOWN] and not bullet_fired and not four_bullet:
                bullet = Bullet(character.rect, "down")
                bullets.add(bullet)
                bullet_fired = True
            if keys[pygame.K_LEFT] and not bullet_fired and not four_bullet:
                bullet = Bullet(character.rect, "left")
                bullets.add(bullet)
                bullet_fired = True
            if keys[pygame.K_RIGHT] and not bullet_fired and not four_bullet:
                bullet = Bullet(character.rect, "right")
                bullets.add(bullet)
                bullet_fired = True
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                if four_bullet and not bullet_fired:
                    bullet_up = Bullet(character.rect, "up")
                    bullets.add(bullet_up)
                    bullet_down = Bullet(character.rect, "down")
                    bullets.add(bullet_down)
                    bullet_left = Bullet(character.rect, "left")
                    bullets.add(bullet_left)
                    bullet_right = Bullet(character.rect, "right")
                    bullets.add(bullet_right)
                    bullet_fired = True
    

            # Update bullets
            bullets.update()

            # Update enemies given the spawn timer
            current_time = pygame.time.get_ticks()
            if current_time - spawn_timer >= spawn_delay:
                enemy = Enemy(character, allies)
                enemies.add(enemy)
                spawn_timer = current_time

                # Speed up enemy spawn rate every 3 seconds
                if (current_time - spawn_timer) % spawn_speedup_interval == 0:
                    spawn_delay *= (1 - spawn_speedup_percentage)

            enemies.update()

            powerup_index = random.randint(1, 5)
            # Update the powerups given the spawn timer
            if current_time - power_up_timer >= power_up_spawn:
                
                if powerup_index == 1:
                    lightning = Lightning(character)
                    lightnings.add(lightning)
                    power_up_timer = current_time

                if powerup_index == 2:
                    cannon = Cannon(character, bullets)
                    cannons.add(cannon)
                    power_up_timer = current_time
                
                if powerup_index == 3:
                    bomb = Bomb(character, enemies)
                    bombs.add(bomb)
                    power_up_timer = current_time
                
                if powerup_index == 4:
                    infection = Infection(character)
                    infections.add(infection)
                    power_up_timer = current_time
                
                if powerup_index == 5 and len(shields) < 3: 
                    barrier = Barrier(character)
                    barriers.add(barrier)
                    power_up_timer = current_time

            # Update the lightning
            lightnings.update()

            # Update the cannon
            cannons.update()

            # Update the bomb
            bombs.update()

            # Update the infection
            infections.update()
            
            # Updates the allies
            allies.update(keys)

            # Update the barriers
            barriers.update()

            # Update the shields
            shields.update()
            
            # Game over condition
            if len(hearts) == 0:
                game_over = True
                

            # Clear the screen
            screen.fill((0, 0, 0))

            # Draw the checkered background
            for row in range(screen_height // square_size):
                for col in range(screen_width // square_size):
                    if (row + col) % 2 == 0:
                        color = tan
                    else:
                        color = brown

                    pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

            # Draw the character
            screen.blit(character.image, character.rect)

            # Draw bullets
            bullets.draw(screen)

            # Draw enemies
            enemies.draw(screen)

            # Draw the scoreboard
            scoreboard.draw()

            # Draw the hearts
            hearts.draw(screen)

            # Draw the lightning
            lightnings.draw(screen)

            # Draw the cannon
            cannons.draw(screen)

            # Draw the bomb
            bombs.draw(screen)

            # Draw the infection
            infections.draw(screen)

            # Draw the allies
            allies.draw(screen)

            # Draw the barriers
            barriers.draw(screen)

            # Draw the shields
            shields.draw(screen)


            # Reset bullet_fired flag if no shooting key is held down
            if not any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]):
                bullet_fired = False   

            # Flip the display
            pygame.display.flip()

        # When the game starts
        elif not menu_screen and not game_start:

            # Show the menu screen
            show_menu()
            menu_screen = True

        # When the game ends (break happens)
        elif not end_screen and game_over:

            # Show the game over screen
            show_game_over(scoreboard.score)
            end_screen = True

        # Ending condition
        else:
            # Handle keyboard input for when no screen
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()


def brython_run_script():
    # Your main game loop or initialization logic
    while True:
        # Example: Print something to console
        print("Game is running!")

        # Simulate a game tick delay
        pygame.time.delay(1000)  # 1000 milliseconds = 1 second


