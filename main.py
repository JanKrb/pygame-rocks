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

class Background:
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'background.png')).convert()
        self.image = pygame.transform.scale(self.image, (
            Settings.window_width,
            Settings.window_height
        ))

    def draw(self) -> None:
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
            (self.rect.width * self.rand_size_ratio),
            (self.rect.height * self.rand_size_ratio)
        ))
        self.rect = self.image.get_rect()

class Stone(pygame.sprite.Sprite):
    def __init__(self, game) -> None:
        super().__init__()

        self.image = pygame.image.load(os.path.join(Settings.path_images, 'stone.png'))
        self.rect = self.image.get_rect()
        self.rand_size_ratio = random.uniform(0.01, 0.2)
        self.resize_image()
        self.rect.top = 15
        self.rect.left = self.find_free_space_on_y_axis(game)
    
    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            (self.rect.width * self.rand_size_ratio),
            (self.rect.height * self.rand_size_ratio)
        ))
        self.rect = self.image.get_rect()

    def find_free_space_on_y_axis(self, game, depth=0):
        candidate = random.randint(1, Settings.window_width - self.rect.width)

        if depth > Settings.max_spawn_attemps:
            print("Failed to find position")
            return candidate

        pseudo_object = PseudoStoneSprite(self.rand_size_ratio)
        pseudo_hits = pygame.sprite.spritecollide(pseudo_object, game.stones, False)

        if len(pseudo_hits) > 0:
            return self.find_free_space_on_y_axis(game, depth + 1)

        return candidate

class Pigeon(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.images = [pygame.image.load(os.path.join(Settings.path_images, 'pigeon', str(image) + '.png')) for image in range(1, 7)]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.animation_cooldown = 5
        self.resize_image()
        self.rect.top = Settings.window_height - Settings.pigeon_bottom_offset
        self.rect.left = Settings.window_width // 2 - self.rect.width // 2
        self.speed = 0
        self.direction = 1 # Positive: Right; Negative: Left
    
    def draw(self) -> None:
        game.screen.blit(self.image, self.rect)
    
    def get_position(self):
        return (self.rect.top, self.rect.left)

    def update(self) -> None:
        prev_pos = self.get_position()

        if self.animation_cooldown <= 0:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0

            self.image = self.images[self.image_index]
            self.rect = self.image.get_rect()
            self.rect.top = prev_pos[0]
            self.rect.left = prev_pos[1]
            self.resize_image(prev_pos)
            self.animation_cooldown = 5
        else:
            self.animation_cooldown -= 1
    
    def resize_image(self, prev_pos=(0,0)):
        self.image = pygame.transform.scale(self.image, (
            (self.rect.width * Settings.sprite_size_pigeon),
            (self.rect.height * Settings.sprite_size_pigeon)
        ))
        self.rect = self.image.get_rect()
        self.rect.top = prev_pos[0]
        self.rect.left = prev_pos[1]
    
    def move_right(self, speed=1):
        if self.direction < 0:
            # Make pigeon look to left
            pass
        self.rect.left += speed

        prev_pos = self.get_position()
        self.resize_image(prev_pos)

    def move_left(self, speed=1):
        if self.direction > 0:
            # Make pigeon look to right
            pass
        self.rect.left -= speed

        prev_pos = self.get_position()
        self.resize_image(prev_pos)

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

        for _ in range(15):
            self.stones.add(Stone(self))

        self.enemy_spawn_cooldown_current = 1000
        self.enemy_spawn_cooldown_counter = self.enemy_spawn_cooldown_current
        self.enemy_spawn_cooldown_minimal = 100
        self.enemy_spawn_cooldown_step = 5


    def start(self) -> None:
        self.running = True

        while self.running:
            self.clock.tick(Settings.window_fps)

            self.watch_events()
            self.update()
            self.draw()

        pygame.quit()
    
    def watch_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_d:
                    self.pigeon.move_right()
                elif event.key == pygame.K_a:
                    self.pigeon.move_left()

    def update(self) -> None:
        self.background.update()
        self.pigeon.update()
        self.stones.update()

        # Spawn enemies
        if self.enemy_spawn_cooldown_counter > 0:
            self.enemy_spawn_cooldown_counter -= 0
        else:
            # Spawn
            self.enemy_spawn_cooldown_current -= self.enemy_spawn_cooldown_step
            self.enemy_spawn_cooldown_counter = self.enemy_spawn_cooldown_current


    def draw(self) -> None:
        self.background.draw()
        self.pigeon.draw()
        self.stones.draw(self.screen)
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.start()