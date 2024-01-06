import pygame
import sys
import os
import random
import math
from pygame.locals import(
    K_RETURN,
    KEYDOWN,
    QUIT
)

# Import the classes from the separate file
from game_classes import (
    Character,
    Bullet,
    Enemy,
    Scoreboard,
    Heart,
    Lightning,
    Bomb,
    Ally,
    Infection,
    Barrier,
    Shield
)

class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen_width = 800
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AGENT V.S. GHOSTS")

        # Define tan and brown colors
        self.tan = (210, 180, 140)
        self.brown = (61, 39, 24)

        # Initialize game state variables
        self.infected = False
        self.four_bullet = False
        self.bullet_fired = False
        self.game_running = True
        self.game_over = False
        self.game_start = False
        self.end_screen = False
        self.menu_screen = False

        # Initialize game objects
        self.character = Character()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.scoreboard = Scoreboard()
        self.scoreboard.update_text_dimensions()
        self.hearts = pygame.sprite.Group()
        self.lightnings = pygame.sprite.Group()
        self.cannons = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.infections = pygame.sprite.Group() 
        self.allies = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()

        # Track time for spawning
        self.spawn_timer = pygame.time.get_ticks()
        self.spawn_delay = 3000  # 3000 milliseconds = 3 seconds

        # Time speedup interval for the enemies
        self.spawn_speedup_interval = 30000  # 30000 milliseconds = 30 seconds
        spawn_speedup_percentage = 0.03  # 3% faster spawn rate

        # Power up spawn time 
        self.power_up_timer = pygame.time.get_ticks()
        self.power_up_spawn = 10000 # 10000 milliseconds = 10 seconds

        # Create hearts
        self.heart_spacing = 50
        self.heart_start_x = (self.screen_width - 60)
        self.heart_start_y = 20
        for i in range(3):
            heart = Heart(self.heart_start_x - i * self.heart_spacing, self.heart_start_y)
            self.hearts.add(heart)

    # A function that displays the menu
    def show_menu(self):
        
        # Create a new Pygame window for the menu screen
        menu_screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AGENT V.S. GHOSTS")

        # Fill the background with a color
        menu_screen.fill((255, 255, 255))

        # Create a font for the AGENT V.S. GHOSTS game message
        font = pygame.font.SysFont('courier new', 64, bold=True)

        # Create a font for the start message
        start_font = pygame.font.SysFont('courier new', 48, bold=True)

        # Render the AGENT V.S. GHOSTS game message
        menu_text = font.render("AGENT V.S. GHOSTS", True, (0, 0, 0))
        menu_text_rect = menu_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))

        # Render the start message
        start_text = start_font.render("Press Enter To Start", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 150))

        # Blit the text onto the screen
        menu_screen.blit(menu_text, menu_text_rect)
        menu_screen.blit(start_text, start_text_rect)

        # Update the display
        pygame.display.flip()

    # A function that displays the game over window
    def show_game_over(self, score):
        # Create a new Pygame window for the game over screen
        game_over_screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("AGENT V.S. GHOSTS")

        # Fill the background with a color
        game_over_screen.fill((255, 255, 255))

        # Create a font for the game over message
        font = pygame.font.SysFont('courier new', 64, bold=True)

        # Create a font for the start message
        start_font = pygame.font.SysFont('courier new', 48, bold=True)

        # Render the game over message
        game_over_text = font.render("Game Over", True, (0, 0, 0))
        game_over_text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))

        # Render the score message
        score_text = font.render("Score: {}".format(score), True, (0, 0, 0))
        score_text_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))

        # Render the start message
        start_text = start_font.render("Press Enter To Restart", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 150))

        # Blit the text onto the screen
        game_over_screen.blit(game_over_text, game_over_text_rect)
        game_over_screen.blit(score_text, score_text_rect)
        game_over_screen.blit(start_text, start_text_rect)

        # Update the display
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Handle keyboard input
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if self.menu_screen:
                        self.menu_screen = False
                        self.game_start = True
                    elif self.game_over:
                        self.reset_game()
    
    def shooting_logic(self, keys, four_bullet, bullet_fired):

        # Shooting logic
        if keys[pygame.K_UP] and not self.bullet_fired and not self.four_bullet:
            bullet = Bullet(character.rect, "up")
            self.bullets.add(bullet)
            self.bullet_fired = True
        if keys[pygame.K_DOWN] and not self.bullet_fired and not self.four_bullet:
            bullet = Bullet(character.rect, "down")
            self.bullets.add(bullet)
            self.bullet_fired = True
        if keys[pygame.K_LEFT] and not self.bullet_fired and not self.four_bullet:
            bullet = Bullet(character.rect, "left")
            self.bullets.add(bullet)
            self.bullet_fired = True
        if keys[pygame.K_RIGHT] and not self.bullet_fired and not self.four_bullet:
            bullet = Bullet(character.rect, "right")
            self.bullets.add(bullet)
            self.bullet_fired = True
        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            if self.four_bullet and not self.bullet_fired:
                bullet_up = Bullet(character.rect, "up")
                self.bullets.add(bullet_up)
                bullet_down = Bullet(character.rect, "down")
                self.bullets.add(bullet_down)
                bullet_left = Bullet(character.rect, "left")
                self.bullets.add(bullet_left)
                bullet_right = Bullet(character.rect, "right")
                self.bullets.add(bullet_right)
                self.bullet_fired = True
        
        # Reset bullet_fired flag if no shooting key is held down
        if not any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
            self.bullet_fired = False   


    def update_objects(self, keys):

        # Update character and other game objects
        self.character.update(keys)
        self.bullets.update()

        # Update enemies given the spawn timer
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_timer >= self.spawn_delay:
            enemy = Enemy(character, allies)
            self.enemies.add(enemy)
            self.spawn_timer = current_time

            # Speed up enemy spawn rate every 3 seconds
            if (current_time - self.spawn_timer) % self.spawn_speedup_interval == 0:
                self.spawn_delay *= (1 - self.spawn_speedup_percentage)

        self.enemies.update()

        powerup_index = random.randint(1, 5)
        # Update the powerups given the spawn timer
        if current_time - self.power_up_timer >= self.power_up_spawn:
            
            if powerup_index == 1:
                lightning = Lightning(character)
                self.lightnings.add(lightning)
                self.power_up_timer = current_time

            if powerup_index == 2:
                cannon = Cannon(character, bullets)
                self.cannons.add(cannon)
                self.power_up_timer = current_time
            
            if powerup_index == 3:
                bomb = Bomb(character, enemies)
                self.bombs.add(bomb)
                self.power_up_timer = current_time
            
            if powerup_index == 4:
                infection = Infection(character)
                infections.add(infection)
                self.power_up_timer = current_time
            
            if powerup_index == 5 and len(shields) < 3: 
                barrier = Barrier(character)
                self.barriers.add(barrier)
                self.power_up_timer = current_time
    
        self.lightnings.update()
        self.cannons.update()
        self.bombs.update()
        self.infections.update()
        self.allies.update(keys)
        self.barriers.update()
        self.shields.update()

        # Game over condition
        if len(hearts) == 0:
            self.game_over = True

    def draw_objects(self):

        # Clear the screen
        screen.fill((0, 0, 0))

        # Define tan and brown colors and square size
        square_size = 20

        # Draw the checkered background
        for row in range(self.screen_height // square_size):
            for col in range(self.screen_width // square_size):
                if (row + col) % 2 == 0:
                    color = self.tan
                else:
                    color = self.brown

                pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

        # Draw all game objects on the screen
        self.character.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemies.draw(self.screen)
        self.allies.draw(self.screen)
        self.shields.draw(self.screen)
        self.hearts.draw(self.screen)
        self.scoreboard.draw()

        pygame.display.flip()

    def reset_game(self):
        self.game_over = False
        self.game_start = True
        self.end_screen = False

        # Reset the game by re-initializing variables and objects
        self.character = Character()
        self.bullets.empty()
        self.enemies.empty()
        self.allies.empty()
        self.shields.empty()
        self.scoreboard.score = 0
        self.scoreboard.update_text_dimensions()
        self.spawn_timer = pygame.time.get_ticks()

        # Clear the hearts group before adding new hearts
        self.hearts.empty()

        # Create hearts
        heart_spacing = 50
        heart_start_x = (self.screen_width - 60)
        heart_start_y = 20
        for i in range(3):
            heart = Heart(heart_start_x - i * heart_spacing, heart_start_y)
            self.hearts.add(heart)
    
        # Reset powerups
        if len(self.lightnings) != 0:
            self.lightnings.empty()
        if len(self.cannons) != 0:
            self.cannons.empty()
        if len(self.bombs) != 0:
            self.bombs.empty()
        if len(self.infections) != 0:
            self.infections.empty()
        if len(self.allies) != 0:
            self.allies.empty()
        if len(self.barriers) != 0:
            self.barriers.empty()
        if len(self.shields) != 0:
            self.shields.empty()


    def start_game(self):
        clock = pygame.time.Clock()

        while self.game_running:
            clock.tick(60)
            keys = pygame.key.get_pressed()
            self.handle_events()
            
            if self.game_start:
                self.shooting_logic(keys, four_bullet, bullet_fired)
                self.update_objects(keys)
                self.draw_objects()


if __name__ == "__main__":
    game_instance = Game()
    game_instance.start_game()
