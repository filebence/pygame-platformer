import pygame, random
from os import path, walk
from os.path import join
from pytmx import load_pygame
from pygame.locals import *
from particles import *
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
TILE_SIZE = 64
FPS = 60
CLOCK = pygame.time.Clock()
GAME_OVER = 0
MAIN_MENU = True
COLOR = "Blue"
LEVEL = 0
MAX_LEVELS = 12
MAX_HP = 3
HP = 3
PLAYER_NAME = ""
last_tick = pygame.time.get_ticks()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME|pygame.FULLSCREEN|pygame.SCALED)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
pygame.display.set_caption("Platformer")

def draw_grid():
    for i in range(SCREEN_WIDTH // TILE_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (i * TILE_SIZE, 0), (i * TILE_SIZE, SCREEN_HEIGHT))
    for j in range(SCREEN_HEIGHT // TILE_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, j * TILE_SIZE), (SCREEN_WIDTH, j * TILE_SIZE))

start_img = pygame.image.load(join("assets", "Button", "start.png")).convert_alpha()
exit_img = pygame.image.load(join("assets", "Button", "exit.png")).convert_alpha()
menu_img = pygame.image.load(join("assets", "Button", "menu.png")).convert_alpha()
exit2_img = pygame.image.load(join("assets", "Button", "exit2.png")).convert_alpha()
exit2_img = pygame.transform.scale(exit2_img, (30, 30))

task_gui = pygame.image.load("assets/GUI/taskgui.png").convert_alpha()
task_gui_rect = task_gui.get_frect(center = screen.get_frect().center)

live_bar = pygame.image.load("assets/GUI/livebar.png").convert_alpha()
live_bar = pygame.transform.scale(live_bar, (198, 102))
heart = pygame.image.load("assets/GUI/heart.png").convert_alpha()
heart = pygame.transform.scale(heart, (36, 36))
fruits = pygame.image.load("assets/GUI/fruits.png").convert_alpha()
fruits = pygame.transform.scale(fruits, (32, 32))

# _____ TASK1 _____
def task1generator():
    result = []
    for i in range(21):
        for j in range(21-i):
            ossz = [str(i),"+",str(j),"=",str(i+j)]
            ossz[random.choice([0, 2, 4])] = "?"
            kiv = [str(i+j),"-",str(i),"=",str(j)]
            kiv[random.choice([0, 2, 4])] = "?"
            result.append(ossz)
            result.append(kiv)
    random.shuffle(result)
    return result
task1_list = task1generator()

def select_task1_list():
    random_task1 = random.choice(task1_list)
    for i in range(len(random_task1)):
        Task1((292 + i * 110, 320), random_task1[i], task1_group)
    task1_list.remove(random_task1)

# _____ TASK2 _____
def task2generator():
    nums = random.sample(range(0, 21), 4)
    ops = random.sample([">", ">", "<", "<"], 3)
    result = []
    s = 0
    for i in range(len(nums+ops)):
        if i % 2 == 0: result.append(str(nums[s]))
        else: result.append(ops[s])
        if i % 2: s += 1
    return result

# _____ TASK3 _____
def task3generator():
    start_num = random.randint(4, 17)
    result_num = [str(start_num)]
    result_steps = []
    while len(result_num) <= 5:
        random_num = random.randint(-start_num, 20-start_num)
        if random_num == 0:
            continue
        next_num = start_num + random_num
        if random_num > 0:
            result_steps.append("+" + str(random_num))
        else:
            result_steps.append(str(random_num))
        result_num.append(str(next_num))
        start_num = next_num
    return result_steps, result_num

# _____ TASK4 _____
def task4generator():
    task4sample = random.sample(range(1, 16), 8)
    for i in range(len(task4sample)):
        if i < 4:
            Task4((250 + i * 135, 315), str(task4sample[i]))
        else:
            Task4((250 + (i - 4) * 135, 450), str(task4sample[i]))

def reset_level(level):
    finish_group.empty()
    wall_group.empty()
    npc_group.empty()
    fruit_group.empty()
    spike_group.empty()
    octi_group.empty()

    if 1 < level <= 4:
        task1_group.empty()
        task1button.reset()
        select_task1_list()
    
    if 4 < level <= 7:
        task2board_group.empty()
        task2opcards_group.empty()
        task2numcards_group.empty()
        random_task2_result = task2generator()
        sample_board = [0, 1, 0, 1, 0, 1, 0]
        for board in range(len(sample_board)):
            Task2Board(212 + board * 100, 270, sample_board[board], "", task2board_group)
            if sample_board[board] == 0:
                Task2Board(332 + board * 60, 490, 0, str(random_task2_result[board]), task2numcards_group)
            else:
                Task2Board(362 + board * 50, 390, 1, random_task2_result[board], task2opcards_group)

    if 7 < level <= 10:
        task3_group.empty()
        global result_steps, result_num
        result_steps, result_num = task3generator()
        for num in range(len(result_num)):
            Task3((207 + num * 122, 410), "nums", num, task3_group)
        for step in range(len(result_steps)):
            Task3((268 + step * 122, 350), "steps", step, task3_group)

    if 10 < level:
        task4_group.empty()
        task4generator()

    if path.exists(f"Maps/{level}.tmx"):
        world = World(f"Maps/{level}.tmx")

    player.reset(world.player_pos, world.player_surfs)

    return world

def import_folder(*path):
    frames = []
    for folder_path, sub_folders, file_names in walk(join(*path)):
        for file_name in sorted(file_names, key = lambda name: int(name.split(".")[0])):
            full_path = join(folder_path, file_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames

class CurrentLevel:

    def __init__(self):
        self.image = pygame.image.load(join("assets", "GUI", "level.png")).convert_alpha()
        self.font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 65)
    
    def draw(self, current, max):
        level = self.font.render(f"{current}/{max}", True, (50, 50, 50))
        level_rect = level.get_frect(centerx = screen.get_frect().centerx, top = 1)
        self.rect = self.image.get_frect(centerx = level_rect.centerx, centery = level_rect.centery + 4)
        screen.blit(self.image, self.rect)
        screen.blit(level, level_rect)

class Button():
    def __init__(self, text, x, y, image):
        self.text = text
        self.image = image
        self.rect = self.image.get_frect(centerx = x, top = y)
        self.mask = pygame.mask.from_surface(self.image)
        font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 65)
        self.txt_img = font.render(self.text, True, (255, 255, 255))
        self.txt_rect = self.txt_img.get_frect(left = self.rect.left + 110, centery = self.rect.centery - 4)
        self.clicked = False
        self.warning = False
    
    def warning_msg(self):
        not_selected_font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 40)
        not_selected_img = not_selected_font.render("Kattints az egyik karakterre, mielőtt indulnál!", True, (255, 255, 255), (250, 40, 40))
        not_selected_rect = not_selected_img.get_frect(centerx = screen.get_frect().centerx, top = 415)
        screen.blit(not_selected_img, not_selected_rect)

    def draw(self):
        global PLAYER_NAME
        action = False
        pos = pygame.mouse.get_pos()
        if self.warning:
            self.warning_msg()
        if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0] and self.mask.get_at((pos[0] - self.rect.x, pos[1] - self.rect.y)):
            action = True
            self.clicked = True
            if self.text == "Indítás":
                if PLAYER_NAME == "":
                    self.warning = True
        if PLAYER_NAME != "":
            self.warning = False
        self.clicked = False
        screen.blit(self.image, self.rect)
        screen.blit(self.txt_img, self.txt_rect)

        return action

class Characters():
    def __init__(self, x, y, name):
        self.name = name
        self.frames = import_folder("assets", "Player", f"{name}", "Running")
        self.selected_frames = import_folder("assets", "Player", "Selected")
        self.selected_index = 0
        self.frame_index = 0
        self.image = pygame.image.load(join("assets", "Player", f"{self.name}", "Idle", "0.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_frect(topleft = (x, y))
        self.mask = pygame.mask.from_surface(self.image)
        font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 30)
        self.txt_img = font.render(self.name, True, (0, 0, 0))
        self.txt_rect = self.txt_img.get_frect(centerx = self.rect.centerx, top = self.rect.bottom)
        self.animation_speed = 5
        self.activate = False
    
    def draw(self, dt):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and self.activate == False and self.mask.get_at((pos[0] - self.rect.x, pos[1] - self.rect.y)):
            self.frame_index += self.animation_speed * dt
            self.image = self.frames[int(self.frame_index % len(self.frames))]
            self.image = pygame.transform.scale(self.image, (200, 200))
            
            if pygame.mouse.get_just_pressed()[0]:
                global PLAYER_NAME
                PLAYER_NAME = self.name
                self.activate = True
        else:
            if self.activate == False:
                self.frame_index = 0
            self.image = pygame.image.load(join("assets", "Player", f"{self.name}", "Idle", "0.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (200, 200))
        
        if self.activate:
            self.frame_index += self.animation_speed * dt
            self.image = self.frames[int(self.frame_index % len(self.frames))]
            self.image = pygame.transform.scale(self.image, (200, 200))
            self.selected_index += self.animation_speed * dt
            self.selected_image = self.selected_frames[int(self.selected_index % len(self.selected_frames))]
            self.selected_rect = self.selected_image.get_frect(centerx = self.rect.centerx, top = self.txt_rect.bottom)

            screen.blit(self.selected_image, self.selected_rect)
        
        if PLAYER_NAME != self.name:
            self.activate = False
    
        screen.blit(self.image, self.rect)
        screen.blit(self.txt_img, self.txt_rect)

class Control:

    def __init__(self):
        self.control_font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 40)
        self.control_font2 = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 60)

        self.up_img = pygame.image.load(join("assets", "GUI", "arrows", "up.png")).convert_alpha()
        self.left_img = pygame.image.load(join("assets", "GUI", "arrows", "left.png")).convert_alpha()
        self.right_img = pygame.image.load(join("assets", "GUI", "arrows", "right.png")).convert_alpha()
        self.control_img = pygame.image.load(join("assets", "GUI", "control_gui.png")).convert_alpha()
        self.finish_img = pygame.image.load(join("assets", "GUI", "finish_gui.png")).convert_alpha()

        self.up_img = pygame.transform.scale(self.up_img, (64, 64)).convert_alpha()
        self.left_img = pygame.transform.scale(self.left_img, (64, 64))
        self.right_img = pygame.transform.scale(self.right_img, (64, 64))

        self.up_rect = self.up_img.get_frect(centerx = screen.get_frect().centerx, y = 300)
        self.left_rect = self.left_img.get_frect(topright = self.up_rect.bottomleft)
        self.right_rect = self.right_img.get_frect(topleft = self.up_rect.bottomright)
        self.finish_rect = self.finish_img.get_frect(center = (800, 100))

        self.up_text = self.control_font.render("ugrás", True, (0, 0, 0)).convert_alpha()
        self.left_text = self.control_font.render("balra", True, (0, 0, 0)).convert_alpha()
        self.right_text = self.control_font.render("jobbra", True, (0, 0, 0)).convert_alpha()
        self.control_text = self.control_font2.render("Irányítás", True, (0, 0, 0)).convert_alpha()
        self.finish_text = self.control_font.render("Juss el a célba", True, (0, 0, 0)).convert_alpha()

        self.up_text_rect = self.up_text.get_frect(bottom = self.up_rect.top - 5, centerx = self.up_rect.centerx)
        self.left_text_rect = self.left_text.get_frect(bottom = self.left_rect.top - 5, right = self.left_rect.centerx)
        self.right_text_rect = self.right_text.get_frect(bottom = self.right_rect.top - 5, left = self.right_rect.centerx)
        self.control_text_rect = self.control_text.get_frect(centerx = self.up_rect.centerx, bottom = self.up_text_rect.top - 10)
        self.control_rect = self.control_img.get_frect(centerx = self.up_rect.centerx, top = self.control_text_rect.top)
        self.finish_text_rect = self.finish_text.get_frect(center = (800, self.finish_rect.centery - 8))

    def draw(self):
        screen.blit(self.control_img, self.control_rect)
        screen.blit(self.up_img, self.up_rect)
        screen.blit(self.left_img, self.left_rect)
        screen.blit(self.right_img, self.right_rect)
        screen.blit(self.up_text, self.up_text_rect)
        screen.blit(self.left_text, self.left_text_rect)
        screen.blit(self.right_text, self.right_text_rect)
        screen.blit(self.control_text, self.control_text_rect)
        screen.blit(self.finish_img, self.finish_rect)
        screen.blit(self.finish_text, self.finish_text_rect)

class NPCTutorial:

    def __init__(self):
        self.font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 50)
        self.npc_img = pygame.image.load(join("assets", "NPC", "0.png")).convert_alpha()
        self.npc_img = pygame.transform.scale(self.npc_img, (200, 200)).convert_alpha()
        self.npc_img = pygame.transform.flip(self.npc_img, True, False).convert_alpha()
        self.wall_img = pygame.image.load(join("assets", "Tileset", "wall.png")).convert_alpha()
        self.wall_img = pygame.transform.rotate(self.wall_img, 90).convert_alpha()
        self.button = pygame.image.load(join("assets", "GUI", "button.png")).convert_alpha()
        self.button = pygame.transform.scale(self.button, (180, 84)).convert_alpha()
        self.line1 = self.font.render("Szia kis kalandor!", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.line2 = self.font.render("Az én nevem Robi.", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.line3 = self.font.render("A célba jutásod falak akadályozzák.", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.line4 = self.font.render("Keress engem,", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.line5 = self.font.render("ha helyesen megoldod a feladatot,", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.line6 = self.font.render("én eltüntetem neked a falat.", True, (0, 0, 0), (230, 230, 230)).convert_alpha()
        self.button_text = self.font.render("Indulás!", True, (0, 250, 0)).convert_alpha()

        self.npc_rect = self.npc_img.get_frect(topright = (task_gui_rect.right - 50, task_gui_rect.top))
        self.line1_rect = self.line1.get_frect(topleft = (task_gui_rect.left + 80, task_gui_rect.top + 70))
        self.line2_rect = self.line2.get_frect(topright = (self.npc_rect.left + 30, self.line1_rect.bottom + 20))
        self.line3_rect = self.line3.get_frect(topleft = (task_gui_rect.left + 80, self.line2_rect.bottom + 50))
        self.line4_rect = self.line4.get_frect(topleft = (task_gui_rect.left + 80, self.line3_rect.bottom + 50))
        self.line5_rect = self.line4.get_frect(topleft = (task_gui_rect.left + 80, self.line4_rect.bottom + 20))
        self.line6_rect = self.line4.get_frect(topleft = (task_gui_rect.left + 80, self.line5_rect.bottom + 20))
        self.wall_rect = self.wall_img.get_frect(centerx = (self.line4_rect.right + ((task_gui_rect.right - self.line4_rect.right)/2)), centery = 401.5)
        self.button_rect = self.button.get_frect(center = (task_gui_rect.centerx, task_gui_rect.bottom - 40))
        self.button_text_rect = self.button_text.get_frect(center = (task_gui_rect.centerx + 4, task_gui_rect.bottom - 44))

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            return True
    
    def draw(self):
        self.update()
        screen.blit(self.npc_img, self.npc_rect)
        screen.blit(self.line1, self.line1_rect)
        screen.blit(self.line2, self.line2_rect)
        screen.blit(self.line3, self.line3_rect)
        screen.blit(self.line4, self.line4_rect)
        screen.blit(self.line5, self.line5_rect)
        screen.blit(self.line6, self.line6_rect)
        screen.blit(self.wall_img, self.wall_rect)
        screen.blit(self.button, self.button_rect)
        screen.blit(self.button_text, self.button_text_rect)

class Player():

    def __init__(self, pos, frames):
        self.reset(pos, frames)
        self.collected_fruits = 0
        self.custom_font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 50)
    
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

    def update(self, game_over, dt):
        dx = 0
        dy = 0
        collected_num = self.custom_font.render(f"x{self.collected_fruits}", True, (250, 250, 250))

        global LEVEL
        global HP
        global MAX_HP

        if LEVEL == 0:
            control.draw()

        screen.blit(fruits, (40, 90))
        screen.blit(collected_num, (80, 83))

        self.animate(dt)
        screen.blit(self.image, self.rect)
        self.hitbox_rect.centerx = self.rect.centerx
        self.hitbox_rect.bottom = self.rect.bottom

        if game_over == 0:
        
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                self.vel_y = -18
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                self.facing_right = False
                if self.move:
                    self.state = "run"
                    if self.hitbox_rect.x > 0:
                        dx -= 5
            if key[pygame.K_RIGHT]:
                self.facing_right = True
                if self.move:
                    self.state = "run"
                    if self.hitbox_rect.right < SCREEN_WIDTH:
                        dx += 5
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.move = True
                self.state = "idle"
            
            if self.move == False:
                self.state = "idle"

            if self.vel_y < 0: self.state = "jump"
            if self.vel_y > 1: self.state = "fall"

            dy += self.vel_y
            self.vel_y += 1

            self.in_air = True
            for sprite in world.main_sprites.sprites():
                if sprite.rect.colliderect(self.hitbox_rect.x + dx, self.hitbox_rect.y, self.width, self.height):
                    if dx >= 0: self.hitbox_rect.right = sprite.rect.left
                    if dx <= 0: self.hitbox_rect.left = sprite.rect.right
                    dx = 0
                if sprite.rect.colliderect(self.hitbox_rect.x, self.hitbox_rect.y + dy, self.width, self.height):
                    if self.vel_y <= 0:
                        dy = sprite.rect.bottom - self.hitbox_rect.top
                    if self.vel_y >= 0:
                        dy = sprite.rect.top - self.hitbox_rect.bottom
                        self.in_air = False
                    self.vel_y = 0

            if pygame.sprite.spritecollide(self, octi_group, False, pygame.sprite.collide_mask):
                for octi in octi_group.sprites():
                    if dx < 0: 
                        if octi.move_direction > 0:
                            dx = 100
                        if octi.move_direction < 0:
                            dx = 100
                    elif dx > 0:
                        if octi.move_direction > 0:
                            dx = -100
                        if octi.move_direction < 0:
                            dx = -100
                    elif dx == 0:
                        dx = 100 * octi.move_direction
                game_over = -1
                if HP > 0:
                    HP -= 1
            
            if pygame.sprite.spritecollide(self, spike_group, False, pygame.sprite.collide_mask):
                game_over = -1
                if HP > 0:
                    HP -= 1

            if pygame.sprite.spritecollide(self, finish_group, False, pygame.sprite.collide_mask):
                game_over = 1
            
            if pygame.sprite.spritecollide(self, npc_group, False, pygame.sprite.collide_mask):
                if LEVEL == 1:
                    screen.blit(task_gui, task_gui_rect)
                    npc_tutorial.draw()
                    if npc_tutorial.update():
                        wall_group.empty()
                        npc_group.empty()
                if 1 < LEVEL <= 4:
                    screen.blit(task_gui, task_gui_rect)
                    task1_group.draw(screen)
                    task1_group.update()
                    task1button.draw()
                    if task1button.update():
                        wall_group.empty()
                        npc_group.empty()
                if 4 < LEVEL <= 7:
                    screen.blit(task_gui, task_gui_rect)
                    task2board_group.draw(screen)
                    task2board_group.update()
                    task2numcards_group.draw(screen)
                    task2numcards_group.update()
                    task2opcards_group.draw(screen)
                    task2opcards_group.update()
                    if task2button.update():
                        task2button.reset()
                        wall_group.empty()
                        npc_group.empty()
                    task2button.draw()
                if 7 < LEVEL <= 10:
                    screen.blit(task_gui, task_gui_rect)
                    task3_group.draw(screen)
                    task3_group.update()
                    task3button.draw()
                    if task3button.check_result():
                        task3button.reset()
                        wall_group.empty()
                        npc_group.empty()
                if 10 < LEVEL:
                    screen.blit(task_gui, task_gui_rect)
                    task4_group.draw(screen)
                    task4_group.update(dt)
                    task4button.draw()
                    if task4button.update():
                        task4button.reset()
                        wall_group.empty()
                        npc_group.empty()
                    
            for sprite in fruit_group.sprites():
                if pygame.sprite.collide_mask(self, sprite):
                    sprite.kill()
                    self.collected_fruits += 1
                    CollectedFruit((sprite.rect.x, sprite.rect.y), world.collected_fruit, collide_group)
                
            if pygame.sprite.spritecollide(self, wall_group, False):
                for sprite in wall_group.sprites():
                    if self.mask.overlap(sprite.mask, (int(self.rect.x + dx) - int(sprite.rect.x), int(sprite.rect.y) - int(self.rect.y + dy))):
                        dx = 0

            if player.rect.top >= SCREEN_HEIGHT:
                game_over = -1
                if HP > 0:
                    HP -= 1

            self.rect.x += dx
            self.rect.y += dy

        return game_over
    
    def reset(self, pos, frames):
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-28, 0)
        self.hitbox_rect.height = float(self.mask.get_bounding_rects()[0][-1])
        self.animation_speed = 5
        self.width = self.hitbox_rect.width
        self.height = self.hitbox_rect.height
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
        self.move = True

class World():

    def __init__(self, data):

        self.load_assets()

        tmx_map = load_pygame(data)
        self.bg_sprites = pygame.sprite.Group()
        self.main_sprites = pygame.sprite.Group()

        for x, y, image in tmx_map.get_layer_by_name("Background").tiles():
            self.bg = Sprite((x * TILE_SIZE, y * TILE_SIZE), image)
            self.bg_sprites.add(self.bg)
        
        for x, y, image in tmx_map.get_layer_by_name("Main").tiles():
            self.main = Sprite((x * TILE_SIZE, y * TILE_SIZE), image)
            self.main_sprites.add(self.main)

        for x, y, image in tmx_map.get_layer_by_name("Enemy").tiles():
            self.octi = Octi((x * TILE_SIZE, y * TILE_SIZE + 16), self.octi_surf, octi_group)

        for x, y, image in tmx_map.get_layer_by_name("Spike").tiles():
            image = pygame.image.load("assets/Spike/spike.png").convert_alpha()
            self.spike = Sprite((x * TILE_SIZE, y * TILE_SIZE), image)
            spike_group.add(self.spike)
        
        for x, y, image in tmx_map.get_layer_by_name("Finish").tiles():
            self.finish = Sprite((x * TILE_SIZE, y * TILE_SIZE), image)
            finish_group.add(self.finish)
        
        for x, y, image in tmx_map.get_layer_by_name("Wall").tiles():
            self.wall = Sprite((x * TILE_SIZE, y * TILE_SIZE), image)
            wall_group.add(self.wall)
        
        for x, y, image in tmx_map.get_layer_by_name("NPC").tiles():
            self.npc = NPC((x * TILE_SIZE, y * TILE_SIZE), self.npc_surf, npc_group)
            npc_group.add(self.npc)
        
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name == "Player":                           
                self.player_pos = (obj.x, obj.y)
        
        for obj in tmx_map.get_layer_by_name("Fruits"):
            if obj.name == "Apple":
                self.apple = Fruits((obj.x, obj.y), self.apple_surf, fruit_group)
            if obj.name == "Banana":
                self.banana = Fruits((obj.x, obj.y), self.banana_surf, fruit_group)
            if obj.name == "Cherry":
                self.cherry = Fruits((obj.x, obj.y), self.cherry_surf, fruit_group)
            if obj.name == "Kiwi":
                self.kiwi = Fruits((obj.x, obj.y), self.kiwi_surf, fruit_group)
            if obj.name == "Melon":
                self.melon = Fruits((obj.x, obj.y), self.melon_surf, fruit_group)
            if obj.name == "Orange":
                self.orange = Fruits((obj.x, obj.y), self.orange_surf, fruit_group)
            if obj.name == "Pineapple":
                self.pineapple = Fruits((obj.x, obj.y), self.pineapple_surf, fruit_group)
            if obj.name == "Strawberry":
                self.strawberry = Fruits((obj.x, obj.y), self.strawberry_surf, fruit_group)
    
    def load_assets(self):
        self.apple_surf = import_folder("assets", "Fruits", "Apple")
        self.banana_surf = import_folder("assets", "Fruits", "Banana")
        self.cherry_surf = import_folder("assets", "Fruits", "Cherry")
        self.kiwi_surf = import_folder("assets", "Fruits", "Kiwi")
        self.melon_surf = import_folder("assets", "Fruits", "Melon")
        self.orange_surf = import_folder("assets", "Fruits", "Orange")
        self.pineapple_surf = import_folder("assets", "Fruits", "Pineapple")
        self.strawberry_surf = import_folder("assets", "Fruits", "Strawberry")
        self.octi_surf = import_folder("assets", "Enemy")
        self.npc_surf = import_folder("assets", "NPC")

        self.collected_fruit = import_folder("assets", "Fruits", "Collected")

        global PLAYER_NAME
        self.player_name = PLAYER_NAME
        self.player_surfs = {"idle": import_folder("assets", "Player", f"{self.player_name}", "Idle"),
        "run": import_folder("assets", "Player", f"{self.player_name}", "Running"),
        "jump": import_folder("assets", "Player", f"{self.player_name}", "Jumping"),
        "fall": import_folder("assets", "Player", f"{self.player_name}", "Falling")}

    def draw(self):
        self.bg_sprites.draw(screen)
        self.main_sprites.draw(screen)

        spike_group.draw(screen)
        octi_group.draw(screen)
        wall_group.draw(screen)
        npc_group.draw(screen)
        finish_group.draw(screen)
        fruit_group.draw(screen)
        collide_group.draw(screen)

class Sprite(pygame.sprite.Sprite):

    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

class AnimatedSprite(pygame.sprite.Sprite):

    def __init__(self, pos, frames, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 10
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.mask = pygame.mask.from_surface(self.image)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

class Fruits(AnimatedSprite):

    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)

    def update(self, dt):
        self.animate(dt)

class CollectedFruit(AnimatedSprite):

    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)

    def update(self, dt):
        self.animate(dt)
        if int(self.frame_index) == len(self.frames):
            self.kill()

class Octi(AnimatedSprite):

    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.move_direction = 1
        self.move_counter = 0
        self.animation_speed = 7

    def update(self, dt):
        self.animate(dt)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.mask = pygame.mask.from_surface(self.image)
        if self.move_direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter >= 62:
            self.move_direction *= -1
            self.move_counter *= -1

class NPC(AnimatedSprite):

    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.animation_speed = 2

    def update(self, dt):
        self.animate(dt)

finish_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
npc_group = pygame.sprite.Group()
fruit_group = pygame.sprite.Group()
collide_group = pygame.sprite.Group()
octi_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()

task1_group = pygame.sprite.Group()
task2board_group = pygame.sprite.Group()
task2opcards_group = pygame.sprite.Group()
task2numcards_group = pygame.sprite.Group()
task3_group = pygame.sprite.Group()
task4_group = pygame.sprite.Group()

class Task1(pygame.sprite.Sprite):

    def __init__(self, pos, data, groups):
        super().__init__(groups)
        self.pos = pos
        self.data = data
        self.image = pygame.image.load("assets/GUI/big_square.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100)).convert_alpha()
        self.rect = self.image.get_frect(center = self.pos)
        self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 100)
        if self.data == "?":
            self.color = (200, 10, 10)
            self.clickable = True
        else:
            self.clickable = False
            self.color = "black"
        self.active = False
        self.user_text = ""

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and self.clickable and pygame.mouse.get_just_pressed()[0]:
            self.active = True
        if self.active:
            self.image.fill((220, 220, 220), (7, 7, 85, 85))
            self.color = "blue"
            key = pygame.key.get_just_pressed()
            if len(self.user_text) < 2 and self.user_text != "0":
                if key[pygame.K_0]: self.user_text += "0"
                if key[pygame.K_1]: self.user_text += "1"
                if key[pygame.K_2]: self.user_text += "2"
                if key[pygame.K_3]: self.user_text += "3"
                if key[pygame.K_4]: self.user_text += "4"
                if key[pygame.K_5]: self.user_text += "5"
                if key[pygame.K_6]: self.user_text += "6"
                if key[pygame.K_7]: self.user_text += "7"
                if key[pygame.K_8]: self.user_text += "8"
                if key[pygame.K_9]: self.user_text += "9"
            if key[pygame.K_BACKSPACE]: self.user_text = self.user_text[:-1]
            self.data = self.user_text

        self.txt_img = self.font.render(self.data, True, self.color).convert_alpha()
        self.txt_rect = self.txt_img.get_frect(center = self.rect.center)
        screen.blit(self.txt_img, self.txt_rect)

class Task1Button:

    def __init__(self, pos):
        self.pos = pos
        self.image = pygame.image.load("assets/GUI/button.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (210, 100)).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 45)
        self.info_text = ""
        self.info_bg_color = (250, 0, 0)
        self.text = "Ellenőrzés"
    
    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            if self.text == "Tovább":
                return True
            result = []
            for sprite in task1_group.sprites():
                result.append(sprite.data)
            res1, res2 = "".join(result).split("=")
            if "?" in result: self.info_text = "Írj be egy számot a ? helyére!"
            elif "" in result: self.info_text = "Az üres helyre írj be egy számot!"
            elif eval(res1) == eval(res2):
                self.text = "Tovább"
                self.info_text = "Ügyes vagy, így tovább!"
                self.info_bg_color = (0, 250, 0)
            else:
                self.info_text = "Próbáld újra!"
    
    def reset(self):
        self.text = "Ellenőrzés"
        self.info_text = ""
        self.info_bg_color = (250, 0, 0)
    
    def draw(self):
        banner_img = pygame.image.load(join("assets", "GUI", "banner.png")).convert_alpha()
        banner_img = pygame.transform.scale(banner_img, (768, 100)).convert_alpha()
        banner_rect = banner_img.get_frect(centerx = screen.get_frect().centerx, top = task_gui_rect.top + 40)
        banner_txt = self.font.render("Írd be a megfelelő számot a hiányzó helyre!", True, "black").convert_alpha()
        banner_txt_rect = banner_txt.get_frect(center = banner_rect.center)

        info_img = self.font.render(self.info_text, True, "black", self.info_bg_color).convert_alpha()
        info_rect = info_img.get_frect(center = (512, 415))
        txt_img = self.font.render(self.text, True, (0, 250, 0)).convert_alpha()
        txt_rect = txt_img.get_frect(center = self.rect.center)

        screen.blit(banner_img, banner_rect)
        screen.blit(banner_txt, banner_txt_rect)
        screen.blit(info_img, info_rect)
        screen.blit(self.image, self.rect)
        screen.blit(txt_img, txt_rect)

task1button = Task1Button((512, 510))

class Task2Board(pygame.sprite.Sprite):

    def __init__(self, x, y, type, text, group):
        self.pos = (x, y)
        self.text = text
        self.group = group
        self.active = False
        self.type = type
        super().__init__(self.group)
        if self.type == 0:
            self.image = pygame.image.load(join("assets", "GUI", "big_square.png")).convert_alpha() # num place
            self.image = pygame.transform.scale(self.image, (100, 100)).convert_alpha()
            self.image.fill((100, 100, 200), (7, 7, 86, 86))
        if self.type == 1:
            self.image = pygame.image.load(join("assets", "GUI", "big_square.png")).convert_alpha() # ops place
            self.image = pygame.transform.scale(self.image, (80, 80)).convert_alpha()
            self.image.fill((140, 200, 140), (5, 5, 70, 70))
        self.rect = self.image.get_frect(center = self.pos)
    
    def update(self):
        pos = pygame.mouse.get_pos()
        if self.group == task2numcards_group or self.group == task2opcards_group:
            self.font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 120)
            self.txt = self.font.render(self.text, True, (0, 0, 0))
            self.txt_rect = self.txt.get_frect(centerx = self.rect.centerx + 4, centery = self.rect.centery - 4)
            screen.blit(self.txt, self.txt_rect)
            
            if self.active:
                self.rect.center = pos

            if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0] and task2button.active:
                self.active = True

            if pygame.mouse.get_just_released()[0]:
                self.active = False
                if not pygame.sprite.spritecollide(self, task2board_group, False, pygame.sprite.collide_rect):
                    self.rect.center = self.pos
                for sprite in task2board_group.sprites():
                    if sprite.type == 0:
                        if self.group == task2numcards_group:
                            if self.rect.colliderect(sprite.rect):
                                self.rect.center = sprite.pos
                                sprite.text = self.text
                            if not pygame.sprite.spritecollide(sprite, task2numcards_group, False):
                                sprite.text = ""
                        if self.group == task2opcards_group:
                            if self.rect.colliderect(sprite.rect):
                                self.rect.center = self.pos
                    if sprite.type == 1 and self.group == task2opcards_group:
                            if self.rect.colliderect(sprite.rect):
                                self.rect.center = sprite.pos
                                sprite.text = self.text
                            if not pygame.sprite.spritecollide(sprite, task2opcards_group, False):
                                sprite.text = ""

class Task2Button:

    def __init__(self):
        self.banner_img = pygame.image.load(join("assets", "GUI", "banner.png")).convert_alpha()
        self.banner_img = pygame.transform.scale(self.banner_img, (768, 100)).convert_alpha()
        self.banner_rect = self.banner_img.get_frect(centerx = screen.get_frect().centerx, top = task_gui_rect.top + 20)
        self.image = pygame.image.load(join("assets", "GUI", "button.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (220, 80)).convert_alpha()
        self.rect = self.image.get_frect(center = (512, 650))
        self.font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 50)
        self.text = "Ellenőrzés"
        self.active = True
        self.message, self.message_bg = "", "red"
        self.result = []
        self.text_line = self.font.render("Húzd az elemeket az üres négyzetekbe!\n     Alkoss egy helyes sorrendet!", True, (0, 0, 0))
        self.text_line_rect = self.text_line.get_frect(center = (self.banner_rect.centerx + 4, self.banner_rect.centery - 4))

    def reset(self):
        self.text = "Ellenőrzés"
        self.message = ""
        self.message_bg = "red"
        self.active = True

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            self.result = []
            if self.text == "Tovább":
                return True
            for sprite in task2board_group.sprites():
                self.result.append(sprite.text)
            if "" not in self.result:
                if eval("".join(self.result)):
                    self.text = "Tovább"
                    self.message = "Sikerült! Ügyes vagy! :)"
                    self.message_bg = (0, 255, 0)
                    self.active = False
                else:
                    self.message = "Valamit nem jól csináltál!"
            else:
                self.message = "Hoppá, maradt még üres hely!"

        self.txt_image = self.font.render(self.text, True, "green")
        self.txt_rect = self.txt_image.get_frect(centerx = self.rect.centerx + 2, centery = self.rect.centery - 2)
        self.message_txt = self.font.render(self.message, True, (0, 0, 0), self.message_bg).convert_alpha()
        self.message_rect = self.message_txt.get_frect(center = (512, 575))
    
    def draw(self):
        screen.blit(self.message_txt, self.message_rect)
        screen.blit(self.banner_img, self.banner_rect)
        screen.blit(self.text_line, self.text_line_rect)
        screen.blit(self.image, self.rect)
        screen.blit(self.txt_image, self.txt_rect)

task2button = Task2Button()

class Task3(pygame.sprite.Sprite):

    def __init__(self, pos, loc, index, groups):
        self.pos = pos
        self.loc = loc
        self.index = index
        super().__init__(groups)
        if self.loc == "nums":
            self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 100)
            self.image = pygame.image.load("assets/GUI/task3bigsquare.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (92, 76)).convert_alpha()
            self.rect = self.image.get_frect(center = pos)
            self.active = False
            self.user_text = ""
            if self.index == 0:
                self.clickable = False
                self.num_img = self.font.render(result_num[self.index], True, "black")
            else:
                self.clickable = True
                self.active = False
                self.correct = False
                self.num_img = self.font.render("_", True, "black")
        if self.loc == "steps":
            self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 40)
            self.image = pygame.image.load("assets/GUI/arrow.png").convert_alpha()
            self.rect = self.image.get_frect(center = pos)
            self.step_img = self.font.render(result_steps[self.index], True, "black")
            self.step_rect = self.step_img.get_frect(centerx = self.rect.centerx, bottom = self.rect.top)

    def user_input(self):
        pos = pygame.mouse.get_pos()
        if self.loc == "nums":
            if self.rect.collidepoint(pos) and self.clickable and self.correct == False and pygame.mouse.get_just_pressed()[0]:
                self.active = True
                self.user_text = ""
            if not self.rect.collidepoint(pos) and self.clickable and pygame.mouse.get_just_pressed()[0]:
                self.active = False

            if self.active:
                key = pygame.key.get_just_pressed()
                if len(self.user_text) < 2 and self.user_text != "0":
                    if key[pygame.K_0]: self.user_text += "0"
                    if key[pygame.K_1]: self.user_text += "1"
                    if key[pygame.K_2]: self.user_text += "2"
                    if key[pygame.K_3]: self.user_text += "3"
                    if key[pygame.K_4]: self.user_text += "4"
                    if key[pygame.K_5]: self.user_text += "5"
                    if key[pygame.K_6]: self.user_text += "6"
                    if key[pygame.K_7]: self.user_text += "7"
                    if key[pygame.K_8]: self.user_text += "8"
                    if key[pygame.K_9]: self.user_text += "9"
                if key[pygame.K_BACKSPACE]: self.user_text = self.user_text[:-1]
                self.num_img = self.font.render(self.user_text, True, "black")

    def update(self):
        if self.loc == "nums":
            self.user_input()
            self.num_rect = self.num_img.get_frect(center = (self.rect.centerx + 4, self.rect.centery - 4))
            screen.blit(self.num_img, self.num_rect)
        if self.loc == "steps": screen.blit(self.step_img, self.step_rect)

class Task3Button:

    def __init__(self):
        self.image = pygame.image.load(join("assets", "GUI", "button.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (220, 80)).convert_alpha()
        self.rect = self.image.get_frect(center = (512, 600))
        self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 40)
        self.text = "Ellenőrzés"
        self.info_text = ""
        self.info_bg_color = "red"

    def banner(self):
        banner_img = pygame.image.load(join("assets", "GUI", "banner.png")).convert_alpha()
        banner_img = pygame.transform.scale(banner_img, (768, 100)).convert_alpha()
        banner_rect = banner_img.get_frect(centerx = screen.get_frect().centerx, top = task_gui_rect.top + 40)

        txt_img = self.font.render("Folytasd a sorozatot a nyilak fölötti számmal!", True, "black").convert_alpha()
        txt_rect = txt_img.get_frect(center = banner_rect.center)

        screen.blit(banner_img, banner_rect)
        screen.blit(txt_img, txt_rect)

    def reset(self):
        self.text = "Ellenőrzés"
        self.info_text = ""
        self.info_bg_color = "red"

    def check_result(self):
        nums = []
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            if self.text == "Tovább":
                return True
            for sprite in task3_group.sprites():
                if sprite.loc == "nums" and sprite.index > 0:
                    if result_num[sprite.index] == sprite.user_text:
                        sprite.correct = True
                        sprite.image.fill((0, 250, 0), (8, 8, 76, 60))
                    else:
                        sprite.image.fill((250, 0, 0), (8, 8, 76, 60))
                        self.info_text = "Javítsd ki a piros hátterű számokat!"
                    nums.append(sprite.user_text)
            if result_num[1:] == nums:
                self.text = "Tovább"
                self.info_text = "Sikerült, ügyes vagy! \(^o^)/"
                self.info_bg_color = "green"

    def draw(self):
        self.banner()
        text_img = self.font.render(self.text, True, "green").convert_alpha()
        text_rect = text_img.get_frect(center = self.rect.center)
        info_img = self.font.render(self.info_text, True, "black", self.info_bg_color).convert_alpha()
        info_rect = info_img.get_frect(center = (512, 500))
        screen.blit(info_img, info_rect)
        screen.blit(self.image, self.rect)
        screen.blit(text_img, text_rect)

task3button = Task3Button()

class Task4(pygame.sprite.Sprite):

    def __init__(self, pos, text):
        pygame.sprite.Sprite.__init__(self, task4_group)
        self.text = text
        self.image = pygame.image.load("assets/GUI/big_square.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120)).convert_alpha()
        self.rect = self.image.get_frect(topleft = pos)
        self.inner_img = pygame.image.load(join("assets", "Task4", f"{self.text}.png")).convert_alpha()
        self.inner_img = pygame.transform.scale(self.inner_img, (104, 104)).convert_alpha()
        self.inner_rect = self.inner_img.get_frect(center = self.rect.center)
        self.image.fill((255, 255, 255), (8, 8, 104, 104))
        self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 40)
        self.font2 = pygame.font.Font("assets/GUI/monogram-extended.ttf", 30)
        self.green_button = pygame.image.load("assets/GUI/green.png").convert_alpha()
        self.red_button = pygame.image.load("assets/GUI/red.png").convert_alpha()
        self.selected_frames = import_folder(join("assets", "Task4", "Selected"))
        self.selected_index = 0
        self.frame_index = 0
        self.animation_speed = 5
        self.green_rect = self.green_button.get_frect(topleft = (407, 250))
        self.red_rect = self.red_button.get_frect(topleft = (517, 250))
        self.color_txt = self.font.render("Választható színek", True, (0, 0, 0)).convert_alpha()
        self.green_txt = self.font2.render("Páros", True, (0, 0, 0)).convert_alpha()
        self.red_txt = self.font2.render("Páratlan", True, (0, 0, 0)).convert_alpha()
        self.color_rect = self.color_txt.get_frect()
        self.paros_rect = self.green_txt.get_frect()
        self.paratlan_rect = self.red_txt.get_frect()
        self.selected_color = None
        self.color = None
        self.description = None
        
    def update(self, dt):
        if self.selected_color != None:
            self.selected_index += self.animation_speed * dt
            self.selected_image = self.selected_frames[int(self.selected_index % len(self.selected_frames))]
            if self.selected_color == (236, 116, 76):
                self.selected_rect = self.selected_image.get_frect(left = self.red_rect.right + 4, centery = self.red_rect.centery)
            if self.selected_color == (143, 192, 92):
                self.selected_image = pygame.transform.flip(self.selected_image, True, False)
                self.selected_rect = self.selected_image.get_frect(right = self.green_rect.left - 4, centery = self.green_rect.centery)

            screen.blit(self.selected_image, self.selected_rect)

        self.color_rect.centerx, self.color_rect.bottom = screen.get_frect().centerx + 2, self.green_rect.top - 2
        self.paros_rect.center = (self.green_rect.centerx + 1, self.green_rect.centery - 2)
        self.paratlan_rect.center = (self.red_rect.centerx + 1, self.red_rect.centery - 2)

        banner_img = pygame.image.load(join("assets", "GUI", "banner.png")).convert_alpha()
        banner_img = pygame.transform.scale(banner_img, (768, 75)).convert_alpha()
        banner_rect = banner_img.get_frect(centerx = screen.get_frect().centerx, top = task_gui_rect.top + 40)
        screen.blit(banner_img, banner_rect)

        txt_line1 = self.font.render("Kattints az egyik színre! A képen látható", True, (0, 0, 0))
        txt_line2 = self.font.render("gyömülcsök száma alapján szinezd ki a képet.", True, (0, 0, 0))
        line1_rect = txt_line1.get_frect(centerx = banner_rect.centerx, top = banner_rect.top + 5)
        line2_rect = txt_line2.get_frect(centerx = banner_rect.centerx, top = line1_rect.bottom)
        screen.blit(txt_line1, line1_rect)
        screen.blit(txt_line2, line2_rect)

        screen.blit(self.green_button, self.green_rect)
        screen.blit(self.red_button, self.red_rect)
        screen.blit(self.color_txt, self.color_rect)
        screen.blit(self.green_txt, self.paros_rect)
        screen.blit(self.red_txt, self.paratlan_rect)

        screen.blit(self.inner_img, self.inner_rect)

        pos = pygame.mouse.get_pos()
        if self.green_rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            self.selected_color = (143, 192, 92)
            self.selected_index = 5
        if self.red_rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            self.selected_color = (236, 116, 76)
            self.selected_index = 5
        if self.selected_color != None and self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0] and task4button.text == "Ellenőrzés":
            self.color = self.selected_color
            self.image.fill(self.color, (8, 8, 104, 104))
            if self.color == (143, 192, 92):
                self.description = 0
            if self.color == (236, 116, 76):
                self.description = 1

class Task4Button:

    def __init__(self):
        self.image = pygame.image.load("assets/GUI/button.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (180, 70)).convert_alpha()
        self.rect = self.image.get_frect(center = (512, 670))
        self.font = pygame.font.Font("assets/GUI/monogram-extended.ttf", 40)
        self.text = "Ellenőrzés"
        self.warning = ""
        self.bg_color = "red"
    
    def reset(self):
        self.text = "Ellenőrzés"
        self.warning = ""
        self.bg_color = "red"
    
    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_just_pressed()[0]:
            self.list = []
            for sprite in task4_group.sprites():
                if sprite.description != None:
                    self.list.append(bool(int(sprite.text)%2==sprite.description))
                    if bool(int(sprite.text)%2==sprite.description) == False:
                        self.warning = "Valamit nem jól színeztél!"
                if sprite.description == None:
                    self.list.append(None)
                if None in self.list:
                    self.warning = "Maradt még színezetlen kép!"
                
            if self.text == "Tovább":
                return True

            if all(self.list):
                self.text = "Tovább"
                self.bg_color = "green"
                self.warning = "Ügyes vagy! Kattints a 'Tovább' gombra."

    def draw(self):
        self.txt_img = self.font.render(self.text, True, (255, 255, 255)).convert_alpha()
        self.txt_rect = self.txt_img.get_frect(centerx = self.rect.centerx + 2, centery = self.rect.centery - 4)
        self.warning_img = self.font.render(self.warning, True, (0, 0, 0), self.bg_color)
        self.warning_rect = self.warning_img.get_frect(center = (512, 600))
        screen.blit(self.warning_img, self.warning_rect)
        screen.blit(self.image, self.rect)
        screen.blit(self.txt_img, self.txt_rect)

start_button = Button("Indítás", screen.get_frect().centerx, 485, start_img)
exit_button = Button("Kilépés", screen.get_frect().centerx, 600, exit_img)
menu_button = Button("Főmenü", screen.get_frect().centerx, 485, menu_img)
exit2_button = Button("", SCREEN_WIDTH - 20, 5, exit2_img)
task4button = Task4Button()

holly_button = Characters(106, 150, "Holly")
boby_button = Characters(312, 150, "Boby")
lizzy_button = Characters(518, 150, "Lizzy")
tommy_button = Characters(724, 150, "Tommy")
start_end_font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 80)
select_character_img = start_end_font.render("Válassz egy karaktert!", True, (0, 0, 0)).convert_alpha()
select_character_rect = select_character_img.get_frect(centerx = screen.get_frect().centerx + 8, top = 48)

gameover_txt = start_end_font.render("Vége a játéknak", True, (0, 0, 0)).convert_alpha()
gameover_rect = gameover_txt.get_frect(centerx = screen.get_frect().centerx + 8, top = 48)

fruit_font = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 60)
fruit_font2 = pygame.font.Font(join("assets", "GUI", "monogram-extended.ttf"), 120)

main_bg = pygame.image.load(join("assets", "GUI", "main_bg.png")).convert_alpha()

def draw_bg(color):
    img = pygame.image.load(join("assets", "Background", f"{color}.png")).convert_alpha()
    for i in range(SCREEN_WIDTH // TILE_SIZE):
        for j in range(SCREEN_HEIGHT // TILE_SIZE):
            screen.blit(img, (i * TILE_SIZE, j * TILE_SIZE))

control = Control()
npc_tutorial = NPCTutorial()
displaylevel = CurrentLevel()

run = True

while run:

    dt = CLOCK.tick(FPS) / 1000

    draw_bg(COLOR)

    if MAIN_MENU:
        screen.blit(main_bg, (0, 0))
        screen.blit(select_character_img, select_character_rect)
        holly_button.draw(dt)
        boby_button.draw(dt)
        lizzy_button.draw(dt)
        tommy_button.draw(dt)
        if start_button.draw() and PLAYER_NAME != "":
            if path.exists(f"Maps/{LEVEL}.tmx"):
                world = World(f"Maps/{LEVEL}.tmx")
            player = Player(world.player_pos, world.player_surfs)
            world = reset_level(LEVEL)
            GAME_OVER = 0
            MAIN_MENU = False
        if exit_button.draw():
            run = False
    else:
        world.draw()

        screen.blit(live_bar, (5, 5))
        for live in range(HP):
            screen.blit(heart, (54 + live * 33, 38))

        if GAME_OVER == 0:
            displaylevel.draw(LEVEL, MAX_LEVELS)
            if exit2_button.draw():
                run = False
            fruit_group.update(dt)
            collide_group.update(dt)
            octi_group.update(dt)
            npc_group.update(dt)

        GAME_OVER = player.update(GAME_OVER, dt)

        if GAME_OVER == -1:
            pygame.mouse.set_visible(True)
            player.reset(world.player_pos, world.player_surfs)
            GAME_OVER = 0
            player.move = False

        if GAME_OVER == 1:
            LEVEL += 1
            if LEVEL <= MAX_LEVELS:
                COLOR = random.choice(["Blue", "Brown", "Gray", "Green", "Pink", "Purple", "Yellow"])
                world_data = []
                world = reset_level(LEVEL)
                GAME_OVER = 0
                player.move = False

        if LEVEL > MAX_LEVELS or HP <= 0:
            screen.blit(main_bg, (0, 0))
            screen.blit(gameover_txt, gameover_rect)
            fruit_txt2 = fruit_font2.render(f"{player.collected_fruits}", True, (0, 250, 0)).convert_alpha()
            fruit_rect2 = fruit_txt2.get_frect(centerx = screen.get_frect().centerx + 4, top = 260 - 4)
            coll_img = pygame.image.load(join("assets", "GUI", "coll_fruits.png")).convert_alpha()
            coll_rect = coll_img.get_frect(centerx = screen.get_frect().centerx, top = 260)
            fruit_txt1 = fruit_font.render("A kalandod során", True, (0, 0, 0)).convert_alpha()
            fruit_rect1 = fruit_txt1.get_frect(centerx = screen.get_frect().centerx, bottom = fruit_rect2.top - 10)
            fruit_txt3 = fruit_font.render("gyümölcsöt gyűjtöttél!", True, (0, 0, 0)).convert_alpha()
            fruit_rect3 = fruit_txt3.get_frect(centerx = screen.get_frect().centerx, top = fruit_rect2.bottom + 10)
            screen.blit(coll_img, coll_rect)
            screen.blit(fruit_txt1, fruit_rect1)
            screen.blit(fruit_txt2, fruit_rect2)
            screen.blit(fruit_txt3, fruit_rect3)

            if player.collected_fruits >= 25:
                if pygame.time.get_ticks() - last_tick >= 300:
                    spawn_particles2(SCREEN_HEIGHT, random.randint(100, SCREEN_HEIGHT - 300), (random.choice(range(-7, 7)), 10))
                    last_tick = pygame.time.get_ticks()

            particle_group.draw(screen)
            particle_group.update(dt)
            particle2_group.update(dt)
            particle2_group.draw(screen)

            GAME_OVER = -1
            if exit_button.draw():
                run = False
            if menu_button.draw():
                LEVEL = 0
                HP = MAX_HP
                world = reset_level(LEVEL)
                player.collected_fruits = 0
                PLAYER_NAME = ""
                MAIN_MENU = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

