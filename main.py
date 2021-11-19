from typing import Set
import pygame
import os
import random

class Settings:
    # Window settings
    window_height = 750
    window_width = 1000
    window_fps = 60
    window_caption = ""

    # Base paths
    path_working_directory = os.path.dirname(os.path.abspath(__file__))
    path_assets = os.path.join(path_working_directory, 'assets')
    path_images = os.path.join(path_assets, 'images')
    path_fonts = os.path.join(path_assets, 'fonts')

    # Game settings
    sprite_size_pigeon = 0.4
    max_spawn_attemps = 50
    pigeon_bottom_offset = 200
    stone_count_start = 10
    stone_count_max = 200
    lives_initial = 3
    heart_offset_top = 50

    # Text
    title_gameover = 'Verloren!'
    title_resume = 'Drücken Sie <Space>'
    title_points = 'Punkte: %s'
    
    font_pause = ('arialblack', 64)
    font_points = ('arialblack', 28)

class Background(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'background.png')).convert()
        self.image = pygame.transform.scale(self.image, (
            Settings.window_width,
            Settings.window_height
        ))

    def draw(self) -> None:
        # Blit background image at coords 0/0 (top-left)
        game.screen.blit(self.image, (0, 0))

    def update(self) -> None:
        pass

class PseudoStoneSprite(pygame.sprite.Sprite):
    def __init__(self, pseudo_ratio) -> None:
        super().__init__()

        '''
        This class is used for the find_free_space_on_y_axis of Stone.
        The purpose of this class is to check if the pseudo sprite with the same width (but invisible) fits into a gap on the y axis
        '''
        self.image = pygame.image.load(os.path.join(Settings.path_images, 'stone.png'))
        self.rect = self.image.get_rect()
        self.rand_size_ratio = pseudo_ratio
        self.resize_image()
    
    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            # Proportional scale down/up
            int(self.rect.width * self.rand_size_ratio),
            int(self.rect.height * self.rand_size_ratio)
        ))
        self.rect = self.image.get_rect()

class Stone(pygame.sprite.Sprite):
    def __init__(self, game, speed) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'stone.png'))
        self.rect = self.image.get_rect()
        self.rand_size_ratio = random.uniform(0.08, 0.2)
        self.speed_y = int(self.rand_size_ratio * speed) # Downforce (speed) in relation to its size
        
        if self.speed_y <= 0:
            self.speed_y = 1 # Minimal speed

        self.resize_image()
        self.rect.top = 15
        self.rect.left = self.find_free_space_on_y_axis(game)
    
    def draw(self) -> None:
        game.screen.blit(self.image, self.rect)
    
    def update(self) -> None:
        self.rect.top += self.speed_y
        self.sprite_outside_screen()
        

    def sprite_outside_screen(self):
        if self.rect.top > Settings.window_height:
            self.kill()
            game.points += int(self.rand_size_ratio * 10) # Instead of giving 1 point as the task claims, i give the user points by the size of the rock

            if game.stone_spawn_cooldown_initial > game.stone_spawn_cooldown_min:
                game.stone_spawn_cooldown_initial -= 5
            else: 
                game.stone_spawn_cooldown_initial = game.stone_spawn_cooldown_min
            
            if game.stones_on_screen < Settings.stone_count_max:
                game.stones_on_screen += 1
            else:
                game.stones_on_screen = Settings.stone_count_max

    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            int(self.rect.width * self.rand_size_ratio),
            int(self.rect.height * self.rand_size_ratio)
        ))
        self.rect = self.image.get_rect()

    def find_free_space_on_y_axis(self, game, depth=0):
        candidate = random.randint(1, Settings.window_width - self.rect.width) # Random unverified position

        if depth > Settings.max_spawn_attemps: # Max recursive depth
            print("Failed to find position")
            return candidate

        # Create pseudo object and check collisions
        pseudo_object = PseudoStoneSprite(self.rand_size_ratio)
        pseudo_hits = pygame.sprite.spritecollide(pseudo_object, game.stones, False, pygame.sprite.collide_mask)

        if len(pseudo_hits) > 1:
            # Find new position if has been pseudo hit
            return self.find_free_space_on_y_axis(game, depth + 1)

        return candidate

class Pigeon(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'pigeon.png'))
        self.rect = self.image.get_rect()
        self.resize_image()
        self.rect.top = Settings.window_height - Settings.pigeon_bottom_offset
        self.rect.left = Settings.window_width // 2 - self.rect.width // 2
        self.speed = 3
        self.direction_hori = 1 # Positive: Right; Negative: Left
        self.direction_vert = 1 # Positive: Up; Negative: Down
        self.looking = 1 # Positive: Right; Negative: Left
        self.moving_hori = False
        self.moving_vert = False
    
    def draw(self) -> None:
        game.screen.blit(self.image, self.rect)

    def update(self) -> None:
        if self.moving_hori:
            if self.direction_hori > 0:
                self.move_right(self.speed)
            else:
                self.move_left(self.speed)

        if self.moving_vert:
            if self.direction_vert > 0:
                self.move_up(self.speed)
            else:
                self.move_down(self.speed)

        self.collision_stone()

    def collision_stone(self):
        hits = pygame.sprite.spritecollide(self, game.stones, False, pygame.sprite.collide_mask)

        if len(hits) > 0:
            hits[0].kill() # Delete stone
            game.hearts.remove(game.hearts.sprites()[0]) # Remove one heart
            self.hit_by_stone()
    
    def hit_by_stone(self):
        game.stones.empty()
        self.rect.top = Settings.window_height - Settings.pigeon_bottom_offset
        self.rect.left = Settings.window_width // 2 - self.rect.width // 2

        game.lives -= 1
        if game.lives <= 0:
            game.game_over = True
    
    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            int(self.rect.width * Settings.sprite_size_pigeon),
            int(self.rect.height * Settings.sprite_size_pigeon)
        ))
        self.rect = self.image.get_rect()
    
    def move_right(self, speed=1):
        if self.looking < 0:
            self.image = pygame.transform.flip(self.image, True, False) # Flip sprite to make it look into the right direction
            self.looking = 1

        self.rect.left += speed

    def move_left(self, speed=1):
        if self.looking > 0:
            self.image = pygame.transform.flip(self.image, True, False) # Flip sprite to make it look into the right direction
            self.looking = -1
        self.rect.left -= speed
    
    def move_up(self, speed=1):
        self.rect.top -= speed
    
    def move_down(self, speed=1):
        self.rect.top += speed

class Heart(pygame.sprite.Sprite):
    def __init__(self, y_offset=0) -> None:
        super().__init__()

        scale_ratio = 0.075

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'heart.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (
            int(self.image.get_rect().width * scale_ratio),
            int(self.image.get_rect().height * scale_ratio)
        ))

        self.rect = self.image.get_rect()
        self.rect.top = Settings.window_height - Settings.heart_offset_top
        self.rect.left = (Settings.window_width - 150) + (25 * (y_offset + 1))
    
    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Game:
    def __init__(self) -> None:
        super().__init__()

        # PyGame Init
        os.environ['SDL_VIDEO_WINDOW_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(Settings.window_caption)

        self.screen = pygame.display.set_mode((Settings.window_width, Settings.window_height))
        self.clock = pygame.time.Clock()
        self.running = False

        # Sprites
        self.background = Background()
        self.stones = pygame.sprite.Group()
        self.pigeon = Pigeon()
        
        self.lives = Settings.lives_initial
        self.game_over = False
        self.points = 0

        self.stones_on_screen = Settings.stone_count_start
        self.stone_speed = 25
        self.stone_spawn_cooldown_initial = 150
        self.stone_spawn_cooldown = self.stone_spawn_cooldown_initial
        self.stone_spawn_cooldown_min = 20

        self.hearts = pygame.sprite.Group()
        for i in range(self.lives):
            self.hearts.add(Heart(i))

        # Init fonts
        self.font_pause = pygame.font.SysFont(Settings.font_pause[0], Settings.font_pause[1])
        self.font_points = pygame.font.SysFont(Settings.font_points[0], Settings.font_points[1])

    def start(self) -> None:
        self.running = True

        while self.running:
            self.clock.tick(Settings.window_fps)

            self.watch_events()

            if not self.game_over:
                self.update()
                self.draw()
            else:
                self.render_game_over()

        pygame.quit()
    
    def watch_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RIGHT:
                    self.pigeon.direction_hori = 1
                    self.pigeon.moving_hori = True
                elif event.key == pygame.K_LEFT:
                    self.pigeon.direction_hori = -1
                    self.pigeon.moving_hori = True
                elif event.key == pygame.K_UP:
                    self.pigeon.direction_vert = 1
                    self.pigeon.moving_vert = True
                elif event.key == pygame.K_DOWN:
                    self.pigeon.direction_vert = -1
                    self.pigeon.moving_vert = True
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    else:
                        # special effect
                        pass
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    self.pigeon.moving_hori = False
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.pigeon.moving_vert = False

    def reset(self) -> None:
        '''
        Reset game to the initial
        '''
        
        self.lives = Settings.lives_initial
        self.stones.empty()
        self.pigeon.rect.top = Settings.window_height - Settings.pigeon_bottom_offset
        self.pigeon.rect.left = Settings.window_width // 2 - self.pigeon.rect.width // 2
        self.points = 0
        self.stone_spawn_cooldown_initial = 150
        self.stone_spawn_cooldown = self.stone_spawn_cooldown_initial

        for i in range(self.lives):
            self.hearts.add(Heart(i))

        self.game_over = False

    def update(self) -> None:
        self.background.update()
        self.pigeon.update()
        self.stones.update()
        self.hearts.update()

        # Respawn stones
        if self.stone_spawn_cooldown <= 0:
            if len(self.stones) < self.stones_on_screen:
                game.stones.add(Stone(self, self.stone_speed))
                self.stone_spawn_cooldown = self.stone_spawn_cooldown_initial
        else:
            self.stone_spawn_cooldown -= 1

    def render_game_over(self) -> None:
        self.background.draw()

        text = self.font_pause.render(Settings.title_gameover, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.top = (Settings.window_height // 2) - (text_rect.height // 2)
        text_rect.left = (Settings.window_width // 2) - (text_rect.width // 2)

        text_resume = self.font_pause.render(Settings.title_resume, True, (0, 0, 0))
        text_resume_rect = text_resume.get_rect()
        text_resume_rect.top = (Settings.window_height // 2) - (text_resume_rect.height // 2) + text_rect.height + 25
        text_resume_rect.left = (Settings.window_width // 2) - (text_resume_rect.width // 2)

        self.screen.blit(text, text_rect)
        self.screen.blit(text_resume, text_resume_rect)

        pygame.display.flip()
    
    def draw_points(self):
        points_text = self.font_points.render(Settings.title_points.replace('%s', str(self.points)), True, (255, 255, 255))
        points_text_rect = points_text.get_rect()
        points_text_rect.top = Settings.window_height - 50
        points_text_rect.left = 25

        self.screen.blit(points_text, points_text_rect)

    def draw(self) -> None:
        self.background.draw()
        self.pigeon.draw()
        self.stones.draw(self.screen)
        self.hearts.draw(self.screen)
        self.draw_points()
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.start()