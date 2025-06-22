import pygame
import os
import random
import csv

pygame.init() 


screen_width = 800
screen_height = 640

screen = pygame.display.set_mode((screen_width, screen_height))   
pygame.display.set_caption("Shooter")     

# częstotliwość wyświetlenia klatek
clock = pygame.time.Clock()
FPS = 60

# zmienne gry
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = screen_height // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3

screen_scroll = 0
bg_scroll = 0
level = 1

step_index = 1

start_game = False
start_intro = False


# zmienne aktywności gracza:
moving_left = False
moving_right = False
shoot = False
grenade = False     # в начале игры граната False, и не будет изменена пока не будет кинута
grenade_thrown = False 

# muzyka i dźwięki
pygame.mixer.music.load("PygameShooter/audio/music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

enemy_death_fx = pygame.mixer.Sound("PygameShooter/audio/enemy_death.mp3")
death_fx = pygame.mixer.Sound("PygameShooter/audio/death.mp3")


step1_fx = pygame.mixer.Sound("PygameShooter/audio/step1.wav")
step1_fx.set_volume(0.5)
step2_fx = pygame.mixer.Sound("PygameShooter/audio/step2.wav")
step2_fx.set_volume(0.5)
step3_fx = pygame.mixer.Sound("PygameShooter/audio/step3.wav")
step3_fx.set_volume(0.5)        
step4_fx = pygame.mixer.Sound("PygameShooter/audio/step4.wav")
step4_fx.set_volume(0.5)

jump_fx = pygame.mixer.Sound("PygameShooter/audio/jump.mp3")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("PygameShooter/audio/shot.mp3")
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound("PygameShooter/audio/grenade.wav")
grenade_fx.set_volume(0.5)
ping_fx = pygame.mixer.Sound("PygameShooter/audio/ping.mp3")
reload_fx = pygame.mixer.Sound("PygameShooter/audio/reload.mp3")

# pobieranie obrazków
start_img = pygame.image.load("PygameShooter/img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("PygameShooter/img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("PygameShooter/img/restart_btn.png").convert_alpha()

pine1_img = pygame.image.load("PygameShooter/img/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("PygameShooter/img/Background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("PygameShooter/img/Background/mountain.png").convert_alpha()
mountain_img.set_colorkey((0,0,0))
sky_img = pygame.image.load("PygameShooter/img/Background/sky_cloud.png").convert_alpha()

bullet_img = pygame.image.load("PygameShooter/img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("PygameShooter/img/icons/grenade.png").convert_alpha()

# lista zawierająca płytki
img_list = []
for x in range (TILE_TYPES):
    img = pygame.image.load(f"PygameShooter/img/Tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img) 

# pudełka do zdobycia
health_box_img = pygame.image.load("PygameShooter/img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("PygameShooter/img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("PygameShooter/img/icons/grenade_box.png").convert_alpha()

item_boxes = {
    "Health" : health_box_img,
    "Ammo"   : ammo_box_img,
    "Grenade" : grenade_box_img
}


# kolory
BG = ("#98a02a")
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# czcionka
font = pygame.font.SysFont("Futura", 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range (5):
        screen.blit(sky_img, ((x*width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x*width) - bg_scroll * 0.6, screen_height - mountain_img.get_height() - 180))
        screen.blit(pine1_img, ((x*width) - bg_scroll * 0.7, screen_height - pine1_img.get_height() - 60))
        screen.blit(pine2_img, ((x*width) - bg_scroll * 0.8, screen_height - pine2_img.get_height()))


# funkcja reserująca poziom
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # pusta lista płytek
    data = []

    for row in range (ROWS):
        r = [-1] * COLS         # wypełniamy css -jedynkami czyli pustymi płytkami
        data.append(r)

    return data


class Button:

    def __init__(self, x, y, image, scale):
        
        self.image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        self.clicked = False

    def draw(self, surface):

        action = False

        # współrzędne myszy
        pos = pygame.mouse.get_pos()

        # sprawdzamy warunki czy mysz znajduje się na przycisku i czy jest kliknięta
        if self.rect.collidepoint(pos):     # столкновение с точкой
            if pygame.mouse.get_pressed()[0] and not self.clicked:        # 0 lewy, 1 średni, 2 prawy
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action
    

class Soldier(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        
        # audio
        self.step_index = 1

        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades

        self.health = 100
        self.max_health = self.health

        self.jump = False
        self.vel_y = 0
        self.in_air = True

        self.direction = 1
        self.flip = False

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()      # время прошедшее с создания объекта

        # zmienne dla przeciwników
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # pobieranie obrazków gracza
        animation_types = ["Idle", "Run", "Jump", "Death"]

        for animation in animation_types:

            # resetujemy tymczasową listę klatek
            temp_list = []

            # liczymy ilość plików w folderze
            num_of_frames = len(os.listdir(f"PygameShooter/img/{self.char_type}/{animation}"))  # узнаём сколько файлов в папке

            for i in range (num_of_frames):
                img = pygame.image.load(f'PygameShooter/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)   # добавляем временный список в постоянный, получаем список из списков   

        self.image = self.animation_list[self.action][self.frame_index]

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.rect = self.image.get_rect()

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        
        self.rect.center = (x,y)

    def update(self):

        self.update_animation()
        self.check_alive()
        
        # aktualizujemy cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        

        

    def move(self, moving_left, moving_right):
        # resetujemy zmienne ruchu
        screen_scroll = 0
        

        dx = 0
        dy = 0
        
        
        # nadajemy znaczenie zmiennych w zależności od kierunku ruchu
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        # skok
        if self.jump and self.in_air == False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        # grawitacja
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        

        # sprawdzamy kollizje
        for tile in world.obstacle_list:
            # kolizja w kierunku x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y - 0.1, self.width, self.height):
                dx = 0
                

            # kolizja w kierunku y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # sprawdzamy czy pod ziemią czyli skok
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
            
                # sprawdzamy czy nad ziemią
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
       
        # kolizja z wodą
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            


        # kolizja z wyjściem
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True


        # sprawdzamy czy gracz spadł za granicy pozioma
        if self.rect.bottom > screen_height:
            self.health = 0
            


        # sprawdzamy czy wyszedł poza ekran
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
                dx = 0

        # aktualizujemy pozycje prostokąta
        self.rect.x += dx
        self.rect.y += dy

        # aktualizujemy scroll zgodnie z pozycją gracza
        if self.char_type == "player":
            if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - screen_width) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * 0.6 * self.direction), self.rect.centery + 4, self.direction)
            bullet_group.add(bullet)

            # redukujemy ammunicje
            self.ammo -= 1
            shot_fx.play()
            print(self.ammo)

            if self.ammo == 0:
                print("AAA")
                ping_fx.play()

    def ai(self):
        if self.alive and player.alive:

            # ruch
            if random.randint(1, 200) == 1 and not self.idling:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            # ai obok gracza
            if self.vision.colliderect(player.rect):
                # przestaje biec
                self.update_action(0)   # 0 = idle
                # strzela
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False

                    ai_moving_left = not ai_moving_right    # принимает противоположное значение
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)   # 1 = run
                    self.move_counter += 1

                    # aktualizujemy pole widzenia 
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll
            



    def update_animation(self):
        # aktualizujemy animacje
        ANIMATION_COOLDOWN1 = 120
        ANIMATION_COOLDOWN2 = 55
        ANIMATION_COOLDOWN3 = 70

        # ładujemy obrazek zgodnie z odpowiednią klatką
        self.image = self.animation_list[self.action][self.frame_index]
        

        # sprawdzamy czy wystarczjąco czasu minęło z poprzedniej zmiany klatki
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN1 and self.action == 0:
            self.update_time = pygame.time.get_ticks()      # обновляем время последнего обновления
            self.frame_index += 1 
                    

        
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN2 and self.action == 1:
            self.update_time = pygame.time.get_ticks()      # обновляем время последнего обновления
            self.frame_index += 1 
            if self.action == 1 and self.char_type == "player" and (self.frame_index  == 1 or self.frame_index == 5 or self.frame_index == 9):

                if self.step_index == 1:
                    step1_fx.play()
                elif self.step_index == 2:
                    step2_fx.play()
                elif self.step_index == 3:
                    step3_fx.play()
                elif self.step_index == 4:
                    step4_fx.play()

                self.step_index += 1

                if self.step_index > 4:
                    self.step_index = 1


        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN3 and self.action == 3:
            self.update_time = pygame.time.get_ticks()      # обновляем время последнего обновления
            self.frame_index += 1 



        # resetujemy animacje jeżeli zabrakło indexów
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:    
                self.frame_index = 0

        

    def update_action(self, new_action):
        # sprawdzamu czy nowa aktywność różni się od poprzedniej
        if new_action != self.action:
            self.action = new_action
            
            # aktualizujemy index animacji
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0

            self.speed = 0
            self.update_action(3)   # 3 = deathd

            if self.action == 3 and self.alive:
                if self.char_type == "player":
                    death_fx.play()
                    print("AAA")
                elif self.char_type == "enemy":
                    enemy_death_fx.play()
                    print("BBB")

            self.alive = False


            


    def draw(self):
        
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        
        
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = TILE_SIZE * x
                    img_rect.y = TILE_SIZE * y
                    tile_data = (img, img_rect) 

                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)                    
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)                         # dekoracje
                    elif tile == 15:    # gracz
                        player = Soldier("player", x*TILE_SIZE, y*TILE_SIZE, 0.035, 4, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:    # przeciwnicy
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 0.035, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: # ammunicja
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: # granaty
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:    # zdrowie
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:    # wyjście
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)   

        return player, health_bar                     

    def draw(self):

        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):

    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):

    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):

    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):

    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type

        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):

        # scroll
        self.rect.x += screen_scroll

        # sprawdzamy czy gracz zdobył pudełko
        if pygame.sprite.collide_rect(self, player):
            
            # sprawdzamy rodzaj pudełka
            if self.item_type == "Health":
                player.health += 25
                if player.health >= player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
                reload_fx.play()
            elif self.item_type == "Grenade":
                player.grenades += 3
        
            # usunąć pudełko
            self.kill()


class HealthBar():
    
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health =  health
        self.max_health = max_health

    def draw(self, health):
        # aktualizujemy z nowym zdrowiem
        self.health = health

        # liczymy proporcje
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24 ))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.speed = 10

        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.direction = direction

    def update(self):

        # ruch
        self.rect.x += (self.direction * self.speed) + screen_scroll

        # czy poza ekranem
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        # czy koliduje z płytkami poziomu
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # czy coliduje z graczem bądź przeciwnikami
        if pygame.sprite.spritecollide(player, bullet_group, False): 
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()



class Grenade(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.timer = 100
        self.vel_y =  -11
        self.speed = 7

        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.direction = direction

    def update(self):       # метода обновления положения
        self.vel_y += GRAVITY   # тормозим вертикальное движение гранаты
        dx = self.speed * self.direction
        dy = self.vel_y

        # cczy koliduje z płytkami poziomu
        for tile in world.obstacle_list:

            # kolizja ze ścianami
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.speed * self.direction

            # kolizja w kierunku y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # czy pod ziemią
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # czy ponad ziemią
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom


        # aktualizujemy pozycje
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # odlicznie czasu do wybuchu
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()

            explosion = Explosion(self.rect.x, self.rect.y, 0.75)
            explosion_group.add(explosion)

            # szkodzi wszystkim stającym obok
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and\
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:  # модуль
                player.health -= 50

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:  # модуль
                    enemy.health -= 50




        

class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        self.frame_index = 0

        for num in range (1,6):
            img = pygame.image.load(f"PygameShooter/img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            self.images.append(img)

        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4

        # animacja wybuchu
        self.counter += 1

        if self.counter >=EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            
            # jeśli animacja się skończyła, usunąć wybuch
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():

    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0


    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:     
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, screen_width//2, screen_height))
            pygame.draw.rect(screen, self.color, (screen_width//2 + self.fade_counter, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, screen_width, screen_height // 2)) 
            pygame.draw.rect(screen, self.color, (0, screen_height // 2 + self.fade_counter, screen_width, screen_height))

        if self.direction == 2:     
            pygame.draw.rect(screen, self.color, (0,0, screen_width, 0 + self.fade_counter) )
        if self.fade_counter >= screen_width:
            fade_complete = True
            
        return fade_complete 


# kurtyny
intro_fade = ScreenFade(1, BLACK, 8)
death_fade = ScreenFade(2, PINK, 8)



# przyciski
start_button = Button(screen_width // 2 - 130, screen_height // 2 - 150, start_img, 1)
exit_button = Button(screen_width // 2 - 110, screen_height // 2 + 50, exit_img, 1)
restart_button = Button(screen_width // 2 - 100, screen_height // 2 - 50, restart_img, 2)


# grupy sprite'ów
bullet_group = pygame.sprite.Group()        # даёт возможность использовать методы спрайта
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

        
        





# pusta lista płytek
world_data = []

for row in range (ROWS):
    r = [-1] * COLS
    world_data.append(r)

# ładukemy poziom i tworzymy world
with open(f"PygameShooter/level{level}_data.csv", newline = "") as csvfile:
    reader = csv.reader(csvfile, delimiter = ",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)


run = True

while run:

    clock.tick(FPS)
    

    if not start_game:
        # menu
        screen.fill(BG)
        # przyciski
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False

    else:
        
        # aktualizujemy tło
        draw_bg()

        # wyświetlamy płytki
        world.draw()

        # zdrowie gracza
        health_bar.draw(player.health)

        # ammunicja
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range (player.ammo):
            screen.blit(bullet_img, (90 + (x*10), 40))

                
        # granaty
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range (player.grenades):
            screen.blit(grenade_img, (135 + (x*15), 60))

        
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

            
        

        # aktualizujemy i wyświetlamy grupy
        bullet_group.update()
        grenade_group.update()      # обновляем положение гранаты
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        explosion_group.draw(screen)
        bullet_group.draw(screen)
        grenade_group.draw(screen)  # рисуем гранату на экране
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)


        # intro czołówka
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        

        # aktualizujemy aktywności gracza
        if player.alive:
            # strzelanie kuli
            if shoot:
                player.shoot()
            # rzucanie granatów
            elif grenade and not grenade_thrown and player.grenades > 0: # гранаты кидает только игрок, поэтому можно не создавать отдельную функцию для их броска
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                            player.rect.top, player.direction)       # создаём объект граната
                grenade_group.add(grenade)      # добавляем в группу
                # zmiejszenie ilości granatów
                player.grenades -= 1
                grenade_thrown = True


            # skok
            if player.in_air:
                player.update_action(2)     # 2 = jump
            elif moving_left or moving_right:
                player.update_action(1)     # 1 = run
            else:
                player.update_action(0)     # 0 = idle

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # czy gracz skończył poziom
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f"PygameShooter/level{level}_data.csv", newline = "") as csvfile:
                        reader = csv.reader(csvfile, delimiter = ",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)

                    
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # ładujemy dane pozioma i tworzymy world
                    with open(f"PygameShooter/level{level}_data.csv", newline = "") as csvfile:
                        reader = csv.reader(csvfile, delimiter = ",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():

        # wyjście z gry
        if event.type == pygame.QUIT:
            run = False

        # przyciski klawiatury
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                if not player.jump:
                    jump_fx.play()
                player.jump = True
                
            if event.key == pygame.K_f:
                grenade = True

            if event.key == pygame.K_ESCAPE:
                run = False

        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

            if event.key == pygame.K_f:
                grenade = False
                grenade_thrown = False

    
    pygame.display.update()
    
    

pygame.quit()