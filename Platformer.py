import pygame
from pygame.locals import *
import pickle
from pygame import mixer
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# define colours
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)

# define game variables
tile_size = 40
game_over = 0
main_menu = True
level = 1
max_levels = 7
score = 0

# load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.2)
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)
attack_fx = pygame.mixer.Sound('img/attack.wav')
attack_fx.set_volume(0.5)

# load images
bg_img = pygame.image.load('img/background.png')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')
enemy_1_img = pygame.image.load('img/enemy_1.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
level_exit_img = pygame.image.load('img/exit.png')
coin_img = pygame.image.load('img/coin.png')

# load in slime image set
slime_images_right = []
slime_images_left = []
for num in range(0, 4):
    img_right = pygame.image.load(f'img/enemies/slime/slime-move-{num}.png')
    img_right = pygame.transform.scale(img_right, (tile_size, tile_size))
    img_left = pygame.transform.flip(img_right, True, False)
    slime_images_right.append(img_right)
    slime_images_left.append(img_left)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_grid():
    for line in range(0, (screen_width // tile_size)):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

def reset_level(level):
    player.restart(80 - 20, screen_height - 90)
    enemy_1_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    coin_group.empty()
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (100, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action

class World():
    def __init__(self, data):
        # create list of tile images and their coordinates as tuples
        self.tile_list = []

        row_count = 0
        for row in data:
          col_count = 0
          for tile in row:
              if tile == 1:
                  img = pygame.transform.scale(dirt_img, (tile_size, tile_size))    # scale dirt image to tile_size
                  img_rect = img.get_rect()             # create rectangle around image
                  img_rect.x = col_count * tile_size    # define x coord of rectangle
                  img_rect.y = row_count * tile_size    # and y
                  tile = (img, img_rect)                # create tuple of image
                  self.tile_list.append(tile)           # will append a list of tuples with the image and coordinates
              if tile == 2:
                  img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                  img_rect = img.get_rect()
                  img_rect.x = col_count * tile_size
                  img_rect.y = row_count * tile_size
                  tile = (img, img_rect)
                  self.tile_list.append(tile)
              if tile == 3:
                  enemy_1 = Enemy_1(col_count * tile_size, row_count * tile_size)
                  enemy_1_group.add(enemy_1)
              if tile == 4:
                  platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                  platform_group.add(platform)
              if tile == 5:
                  platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                  platform_group.add(platform)
              if tile == 6:
                  lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                  lava_group.add(lava)
              if tile == 7:
                  coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                  coin_group.add(coin)
              if tile == 8:
                  exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                  exit_group.add(exit)
              col_count += 1
          row_count += 1

    def draw(self):
      for tile in self.tile_list:
          screen.blit(tile[0], tile[1])
          #pygame.draw.rect(screen, (255,255,255), tile[1], 2)

class Enemy_1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image_set_right = slime_images_right
        self.image_set_left = slime_images_left
        self.image = slime_images_right[0]
        self.image_rect = self.image.get_rect()
        self.rect = pygame.Rect(self.image_rect.left + 5, self.image_rect.top + 20, self.image_rect.width - 10, self.image_rect.height - 20)
        self.rect.x = x
        self.rect.y = y + 20
        self.move_direction = 1
        self.move_counter = 0
        self.counter = 0
        self.index = 0

    def update(self):
        anim_cooldown = 10
        self.counter += 1
        if self.counter > anim_cooldown:
            self.index += 1
            self.counter = 0
            if self.index >= len(self.image_set_right):
                self.index = 0
            if self.move_direction == -1:
                self.image = self.image_set_right[self.index]
            else:
                self.image = self.image_set_left[self.index]
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter = -50
        self.image_rect = pygame.Rect(self.rect.left - 5, self.rect.top - 20, self.rect.width + 10, self.rect.height + 20)

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.img_list = []
        lava_img_1 = pygame.image.load('img/lava_1.png')
        self.img_list.append(pygame.transform.scale(lava_img_1, (tile_size, tile_size // 2)))
        lava_img_2 = pygame.image.load('img/lava_2.png')
        self.img_list.append(pygame.transform.scale(lava_img_2, (tile_size, tile_size // 2)))
        self.image = self.img_list[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.anim_counter = 0
        self.anim_cooldown = 15
        self.index = 0

    def update(self):
        self.anim_counter += 1
        if self.anim_counter > self.anim_cooldown:
            self.anim_counter = 0
            self.index += 1
            self.image = self.img_list[self.index]
            if self.index == 1:
                self.index = -1

class Exit(pygame.sprite.Sprite):
    def __init__(self,x ,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = level_exit_img
        self.image = pygame.transform.scale(self.image, (tile_size, int(1.5 * tile_size)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self,x ,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = coin_img
        self.image = pygame.transform.scale(self.image, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/cloud.png')
        self.image = pygame.transform.scale(self.image, (60, 15))
        self.rect = self.image.get_rect()
        self.rect.x = x - 10
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if self.move_counter > 50:
            self.move_direction *= -1
            self.move_counter = -50

class Player():
    def __init__(self, x, y):
        self.restart(x, y)

    def restart(self, x, y):
        # load in running image set
        self.images_right = []
        self.images_left = []
        self.index_x = 0
        self.counter_x = 0
        for num in range(0, 6):
            img_right = pygame.image.load(f'img/player/adventurer-run-0{num}.png')
            img_right = pygame.transform.scale(img_right, (68, 50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        # load in idle image set
        self.images_idle_right = []
        self.images_idle_left = []
        self.index_idle = 0
        self.counter_idle = 0
        for num in range(0, 4):
            img_right = pygame.image.load(f'img/player/adventurer-idle-0{num}.png')
            img_right = pygame.transform.scale(img_right, (68,50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_idle_right.append(img_right)
            self.images_idle_left.append(img_left)

        # load in jump image set
        self.images_jump_right = []
        self.images_jump_left = []
        self.index_jump = 0
        self.counter_jump = 0
        for num in range(0, 4):
            img_right = pygame.image.load(f'img/player/adventurer-jump-0{num}.png')
            img_right = pygame.transform.scale(img_right, (68,50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_jump_right.append(img_right)
            self.images_jump_left.append(img_left)

        # load in falling image set
        self.images_fall_right = []
        self.images_fall_left = []
        self.index_fall = 0
        self.counter_fall = 0
        for num in range(0, 2):
            img_right = pygame.image.load(f'img/player/adventurer-fall-0{num}.png')
            img_right = pygame.transform.scale(img_right, (68,50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_fall_right.append(img_right)
            self.images_fall_left.append(img_left)

        # load in attack image set
        self.images_attack_right = []
        self.images_attack_left = []
        self.attack_index = 0
        self.attack_counter = 0
        for num in range(0, 6):
            img_right = pygame.image.load(f'img/player/adventurer-attack2-0{num}.png')
            img_right = pygame.transform.scale(img_right, (68,50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_attack_right.append(img_right)
            self.images_attack_left.append(img_left)

        self.img_ghost = pygame.image.load('img/ghost.png')
        self.img_ghost = pygame.transform.scale(self.img_ghost, (40, 50))
        self.img = self.images_idle_right[self.index_idle]
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image_rect = self.rect
        self.rect = pygame.Rect(self.rect.x + 24, self.rect.y + 10, 68-2*24, 50-10)
        self.vel_y = 0
        self.jumped = False
        self.in_air = False
        self.direction = 1
        self.attacked = False
        self.attacking = False

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 4
        idle_cooldown = 13
        col_thresh = 16
        fall_cooldown = 5
        jump_cooldown = 5

        if game_over == 0:
            # get keypresses
            #pygame.event.get()
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -13
                self.jumped = True
                #self.on_platform = False
                jump_fx.play()
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 3
                self.counter_x += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 3
                self.counter_x += 1
                self.direction = 1
            if key[pygame.K_e] and self.attacked == False:
                self.attack()
                self.attacked = True
                self.attacking = True
            if not key[pygame.K_e]:
                self.attacked = False

            # walk animation
            if dx != 0 and not self.in_air and not self.attacking:
                self.index_idle = 0
                self.attack_index = 0
                if self.counter_x > walk_cooldown:
                    self.counter_x = 0
                    self.index_x += 1
                    if self.index_x >= len(self.images_right):
                        self.index_x = 0
                    if self.direction == -1:
                        self.img = self.images_left[self.index_x]
                    else:
                        self.img = self.images_right[self.index_x]

            # idle animation
            if dx == 0 and not self.in_air and not self.attacking:
                self.counter_x = 0
                self.index_x = 0
                self.attack_index = 0
                self.counter_idle += 1
            if self.counter_idle > idle_cooldown:
                self.counter_idle = 0
                self.index_idle += 1
                if self.index_idle >= len(self.images_idle_right):
                    self.index_idle = 0
                if self.direction == -1:
                    self.img = self.images_idle_left[self.index_idle]
                else:
                    self.img = self.images_idle_right[self.index_idle]

            # falling animation
            if self.in_air and self.vel_y >= 0:
                self.counter_fall += 1
                if self.counter_fall > fall_cooldown:
                    self.counter_fall = 0
                    self.index_fall += 1
                    if self.index_fall >= len(self.images_fall_right):
                        self.index_fall = 0
                    if self.direction == -1:
                        self.img = self.images_fall_left[self.index_fall]
                    else:
                        self.img = self.images_fall_right[self.index_fall]

            # jumping animation
            if self.in_air and self.vel_y < 0:
                self.counter_jump += 1
                if self.counter_jump > jump_cooldown:
                    self.counter_jump = 0
                    self.index_jump += 1
                    if self.index_jump >= len(self.images_jump_right):
                        self.index_jump = 3
                    if self.direction == -1:
                        self.img = self.images_jump_left[self.index_jump]
                    else:
                        self.img = self.images_jump_right[self.index_jump]

            # call attack animation
            if self.attacking:
                self.attack()

            # add gravity
            self.vel_y += 0.8
            if self.vel_y >= 8:
                self.vel_y = 8
            dy += int(round(self.vel_y))

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                # check in y direction
                if tile[1].colliderect(self.rect.left, self.rect.top + dy, self.rect.width, self.rect.height):
                    # is below block - hitting head
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # is falling onto block
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
                # check in x direction
                if tile[1].colliderect(self.rect.left + dx, self.rect.top, self.rect.width, self.rect.height):
                    dx = 0


            # check for collision with enemies
            if pygame.sprite.spritecollide(self, enemy_1_group, False):
                game_over = -1
                game_over_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # check for collision with platform
            for platform in platform_group:
                # check in x direction
                if platform.rect.colliderect(self.rect.left + dx, self.rect.top, self.rect.width, self.rect.height):
                    dx = 0
                # check in y direction
                if platform.rect.colliderect(self.rect.left, self.rect.top + dy, self.rect.width, self.rect.height):
                    # hitting head on platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # if falling onto platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                        dx += platform.move_direction * platform.move_x

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.img = self.img_ghost
            draw_text('GAME OVER!', font, red, (screen_width // 2) - 200, 200)
            self.rect.y -= 4

        # create an enlarged copy of the hitbox rect for use in the blit function below
        self.image_rect = pygame.Rect(self.rect.left - 24, self.rect.top -10, self.rect.right + 24, self.rect.y)

        # draw player onto screen
        screen.blit(self.img, self.image_rect)
        # pygame.draw.rect(screen, (255,255,255), self.rect, 2)
        # pygame.draw.rect(screen, (255,255,255), (self.rect.right, self.rect.top, 19, self.rect.height), 2)

        return game_over

    def attack(self):
        attack_cooldown = 4
        self.attacking = True

        # attack animation
        self.attack_counter += 1
        self.counter_x = 0
        self.counter_idle = 0
        if self.attack_counter > attack_cooldown:
            self.attack_counter = 0
            self.attack_index += 1
            if self.attack_index >= len(self.images_attack_right):
                self.attacking = False
                self.attack_index = 5
            if self.direction == 1:
                self.img = self.images_attack_right[self.attack_index]
            else:
                self.img = self.images_attack_left[self.attack_index]

        # create attack hitbox for collision detection based on player rect and direction
        if self.attack_index == 3 and self.attack_counter == 0:
            attack_fx.play()
            if self.direction == 1:
                self.attack_rect = pygame.Rect(self.rect.right, self.rect.top, 19, self.rect.height)
            else:
                self.attack_rect = pygame.Rect(self.rect.left, self.rect.top, -19, self.rect.height)

            for enemy in enemy_1_group:
                if enemy.rect.colliderect(self.attack_rect):
                    enemy.kill()

# initial loading of player and sprite groups
player = Player(80 - 20, screen_height - 90)
enemy_1_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# create dummy coin for score
score_coin = Coin(18, 25)
coin_group.add(score_coin)

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World(world_data)

# creating buttons
restart_button = Button(screen_width // 2 - 150, screen_height // 2 - 35, restart_img)
exit_button = Button(screen_width // 2 + 50, screen_width // 2 - 35, exit_img)
start_button = Button(screen_width // 2 - 150, screen_height // 2 -35, start_img)

# game loop
run = True
while run:

    # run fps clock and draw background
    clock.tick(fps)
    screen.blit(bg_img, (0,0))

    # starting game menu
    if main_menu == True:
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False

    # not at game menu
    else:
        world.draw()

        # draw sprite classes
        lava_group.draw(screen)
        platform_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)
        for sprite in enemy_1_group:
            screen.blit(sprite.image, sprite.image_rect)

        # if still alive
        if game_over == 0:
            enemy_1_group.update()
            lava_group.update()
            platform_group.update()
            coin_group.add(score_coin)
            # update score
            # check if coin collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1
            draw_text(str(score), font_score, white, 33, 8)

        # at level completion
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('Have a chicken dinner!', font, red, (screen_width // 2) - 200, (screen_height // 2) - 20)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

        # player has died
        if game_over == -1:
            if restart_button.draw():
                player.restart(80 - 20, screen_height - 90)
                world = reset_level(level)
                game_over = 0
            if exit_button.draw():
                run = False

        # update player and check if died or completed level
        game_over = player.update(game_over)

    # always have quit available to prevent game hanging
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # casts changes to the screen
    pygame.display.update()

pygame.quit()
