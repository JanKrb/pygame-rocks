from typing import Set
import pygame
import os

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
    sprite_size_enemy = 0.4

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

class Pigeon(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

        self.images = [pygame.image.load(os.path.join(Settings.path_images, 'pigeon', str(image) + '.png')) for image in range(1, 7)]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.animation_cooldown = 5
        self.resize_image()
    
    def draw(self) -> None:
        game.screen.blit(self.image, (0, 0))
    
    def update(self) -> None:
        if self.animation_cooldown <= 0:
            self.image_index += 1
            if self.image_index >= len(self.images):
                self.image_index = 0

            self.image = self.images[self.image_index]
            self.rect = self.image.get_rect()
            self.resize_image()
            self.animation_cooldown = 5
        else:
            self.animation_cooldown -= 1
    
    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            (self.rect.width * Settings.sprite_size_enemy),
            (self.rect.height * Settings.sprite_size_enemy)
        ))
        self.rect = self.image.get_rect()

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
        self.enemies = pygame.sprite.Group()
        self.pigeon = Pigeon()

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

    def update(self) -> None:
        self.background.update()
        self.pigeon.update()

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
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.start()