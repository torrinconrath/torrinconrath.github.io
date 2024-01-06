import pygame
import sys
import os
import random
import math

# Define some sizes
character_size = 50  
bullet_size = 10
enemy_size = 50
screen_width = 800
screen_height = 800

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