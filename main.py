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
        self.speed_y = int(self.rand_size_ratio * speed)
        
        if self.speed_y <= 0:
            self.speed_y = 1 # Minimal speed

        self.resize_image()
        self.rect.top = 15
        self.rect.left = self.find_free_space_on_y_axis(game)
    
    def draw(self) -> None:
        game.screen.blit(self.image, self.rect)
    
    def update(self) -> None:
        self.rect.top += self.speed_y

        if self.rect.top > Settings.window_height:
            self.kill()

            if game.stone_spawn_cooldown_initial > game.stone_spawn_cooldown_min:
                print("slow cooldown")
                game.stone_spawn_cooldown_initial -= 5
            else: 
                game.stone_spawn_cooldown_initial = game.stone_spawn_cooldown_min
            
            if game.stones_on_screen < Settings.stone_count_max:
                print("incr count")
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
        candidate = random.randint(1, Settings.window_width - self.rect.width)

        if depth > Settings.max_spawn_attemps:
            print("Failed to find position")
            return candidate

        pseudo_object = PseudoStoneSprite(self.rand_size_ratio)
        pseudo_hits = pygame.sprite.spritecollide(pseudo_object, game.stones, False, pygame.sprite.collide_mask)

        if len(pseudo_hits) > 1:
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
        self.direction_vert = 1 # Positive: Iü; Negative: Down
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
    
    def resize_image(self):
        self.image = pygame.transform.scale(self.image, (
            int(self.rect.width * Settings.sprite_size_pigeon),
            int(self.rect.height * Settings.sprite_size_pigeon)
        ))
        self.rect = self.image.get_rect()
    
    def move_right(self, speed=1):
        if self.looking < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.looking = 1

        self.rect.left += speed

    def move_left(self, speed=1):
        if self.looking > 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.looking = -1
        self.rect.left -= speed
    
    def move_up(self, speed=1):
        self.rect.top -= speed
    
    def move_down(self, speed=1):
        self.rect.top += speed

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

        self.stones_on_screen = Settings.stone_count_start
        self.stone_speed = 10
        self.stone_spawn_cooldown_initial = 150
        self.stone_spawn_cooldown = self.stone_spawn_cooldown_initial
        self.stone_spawn_cooldown_min = 20

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
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    self.pigeon.moving_hori = False
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.pigeon.moving_vert = False

    def update(self) -> None:
        self.background.update()
        self.pigeon.update()
        self.stones.update()

        # Respawn stones
        if self.stone_spawn_cooldown <= 0:
            if len(self.stones) < self.stones_on_screen:
                game.stones.add(Stone(self, self.stone_speed))
                self.stone_spawn_cooldown = self.stone_spawn_cooldown_initial
        else:
            self.stone_spawn_cooldown -= 1


    def draw(self) -> None:
        self.background.draw()
        self.pigeon.draw()
        self.stones.draw(self.screen)
        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.start()