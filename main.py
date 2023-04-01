import pygame
import random
import os

# constant
FPS = 60
WIDTH = 1200
HEIGHT = 600
BORDER = 40
BALL_SIZE = 55
ANIMATION_SPEED = 8

# color 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# initialize all imported pygame modules
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Volleyball Game")
clock = pygame.time.Clock()

# upload pictures
background_img = pygame.image.load(os.path.join("img", "VBbackground.png")).convert_alpha()
balls_img = [
    pygame.image.load(os.path.join("img", "Volleyball0.png")).convert_alpha(),
    pygame.image.load(os.path.join("img", "Volleyball1.png")).convert_alpha(),
    pygame.image.load(os.path.join("img", "Volleyball2.png")).convert_alpha()
] 
ball_mini_img = pygame.transform.scale(balls_img[0], (30, 30))
pygame.display.set_icon(balls_img[0])

# upload music
bounce_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "VbBounce01.wav")),
    pygame.mixer.Sound(os.path.join("sound", "VbBounce02.wav"))
]

# functions
font_name = pygame.font.match_font("arial")
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True , WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface, text_rect)

def draw_init():
    screen.blit(pygame.transform.scale(background_img, (WIDTH, HEIGHT)), (0, 0) )
    draw_text(screen, "Volleyball Game", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Arrow keys control the player", 22, WIDTH/2, HEIGHT/2 - 20)
    draw_text(screen, "Press any button to start.", 18, WIDTH/2, HEIGHT * 5/6)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYUP:
                waiting = False
                return False
                
def new_ball():
    ball = Ball()
    all_sprites.add(ball)
    balls.add(ball)

def draw_lifes(surface, lifes, img, x, y):
    for i in range(lifes):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surface.blit(img, img_rect)

def draw_sp(surface, sp, x, y):
    if sp > 100:
        sp = 100
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (sp/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, YELLOW, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Player                
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join("img", "PlayerCowB.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.player_animations()

        self.rect = self.image.get_rect()
        self.radius = 15  # for hit judgment
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # see the circle

        # start position
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        
        # setting
        self.facing = "front"
        self.status = "on_floor"
        self.gravity = 0        
        self.lifes = 3
        self.speedx = 8
        self.jump = False
        self.using_skill = False
        self.sp = 100
        self.cd_time = 0

        # animatation
        self.delay = 100
        self.frame = 0
        self.jump_frame = 0
        self.last_update = pygame.time.get_ticks()

    def player_animations(self):
        self.animations = {}

        self.animations["front"] = []
        self.animations["left"] = []
        self.animations["right"] = []
        self.animations["jump"] = []
        self.animations["using_skill"] = []

        img = pygame.image.load(os.path.join("img", "PlayerCowB.png")).convert_alpha()
        for i in range(4):
            self.animations["front"].append(pygame.transform.scale(img, (120, 120)))
            self.animations["using_skill"].append(pygame.transform.scale(img, (120, 120)))
        for i in range(4):
            img = pygame.image.load(os.path.join("img", f"PlayerCowLeft{i}.png")).convert_alpha()
            self.animations["left"].append(pygame.transform.scale(img, (120, 120)))
        for i in range(4):
            img = pygame.image.load(os.path.join("img", f"PlayerCowRight{i}.png")).convert_alpha()
            self.animations["right"].append(pygame.transform.scale(img, (120, 120)))
        for i in range(8):
            img = pygame.image.load(os.path.join("img", f"PlayerCowJump{i}.png")).convert_alpha()
            self.animations["jump"].append(pygame.transform.scale(img, (120, 120)))
    
    def get_status(self):
        if self.rect.bottom < HEIGHT - 10:
            self.status = "jump"
        else:
            self.status = "on_floor"
        
    def player_input(self):
        key_pressed = pygame.key.get_pressed()
        # movement
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
            self.facing = "right"  
        elif key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
            self.facing = "left"
        else:
            self.facing = "front"
        
        # jump and suing skill
        if key_pressed[pygame.K_UP] and self.rect.bottom >= HEIGHT - 10 and not self.jump:
            # self.facing = "jump"
            self.gravity = -20
            self.jump = True
            self.sp = 0
            self.cd_time = pygame.time.get_ticks()
            # self.jump_sound.play()

        if key_pressed[pygame.K_SPACE] and not self.using_skill:
            self.using_skill = True
            self.skill()
            self.sp = 0
            self.cd_time = pygame.time.get_ticks()  

        # limitation
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10
        
    def skill(self):
        pass
        
    def update(self):
        self.get_status()
        self.player_input()
        self.apply_gravity()
        if self.sp <= 100:
            self.sp += 1
        
        now = pygame.time.get_ticks()
        if self.jump and (now - self.cd_time > 1600):
            self.jump = False
        if self.using_skill and (now - self.cd_time > 800):
            self.using_skill = False

        if self.using_skill:
            self.speedx = 16
        else:
            self.speedx = 8

        if self.status == "jump":
            if now - self.last_update > self.delay:
                self.jump_frame += 1
                self.last_update = now
                if self.jump_frame == len(self.animations["jump"]):
                    self.jump_frame = len(self.animations["jump"]) - 1
                self.image = self.animations["jump"][self.jump_frame]
                
        else:
            if now - self.last_update > self.delay:
                self.jump_frame = 0
                self.frame += 1
                self.last_update = now
                if self.frame == len(self.animations[self.facing]):
                    self.frame = 0
                    self.image = self.animations[self.facing][self.frame]
                else:
                    self.image = self.animations[self.facing][self.frame]

# class: Ball
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = pygame.transform.scale(random.choice(balls_img), (BALL_SIZE, BALL_SIZE))
        self.image = self.image_original.copy()
        
        # self.image = pygame.Surface((40, 40))
        # self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.9 / 2)  # for hit judgment
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)  # see the circle

        self.rect.centerx = WIDTH / 4
        self.rect.centery = -20
        self.speedy = random.randrange(7, 10)
        self.speedx = random.randrange(-2, 8)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-10, 10)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360 
        self.image = pygame.transform.rotate(self.image_original, self.total_degree)
        
        # to fix the center
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):       
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.top > HEIGHT + 60 or self.rect.bottom < -60 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()
            new_ball()
            
# loop music
# pygame.mixer.music.play(-1)

# Game loop
running = True
show_init = True

while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False

        # sprites and groups
        all_sprites = pygame.sprite.Group()
        foreground = pygame.sprite.Group()
        player = Player()
        foreground.add(player)
        ball = Ball()
        balls = pygame.sprite.Group()
        all_sprites.add(ball)
        balls.add(ball)

        score = 0

    clock.tick(FPS)

    # get input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # update
    
    all_sprites.update()
    foreground.update()

    for ball in balls:
        # player miss the ball
        if not pygame.sprite.collide_circle(player, ball):
            if HEIGHT - 30 > ball.rect.centery > HEIGHT - 40:
                if BORDER <= ball.rect.centerx <= WIDTH - BORDER:
                    score -= 1
                    player.lifes -= 1
                    if player.lifes == 0:
                        show_init = True
                else:
                    score += 1
        else:
            score += 1
            random.choice(bounce_sounds).play()
            ball.speedy *= -1
            ball.radius = 0  # to avoid judging again
            if player.rect.centerx < WIDTH / 2:
                ball.speedx = random.randrange(1, 6)
            else:
                ball.speedx = random.randrange(-8, 2)
    
    # display
    # screen.fill(BLACK)
    screen.blit(pygame.transform.scale(background_img, (WIDTH, HEIGHT)), (0, 0))  # put background_img at (0, 0)
    all_sprites.draw(screen)  # show all sprties on the screen
    foreground.draw(screen)
    draw_text(screen, str(score), 24, WIDTH/2, 10)
    draw_sp(screen, player.sp, 7, 10)
    draw_lifes(screen, player.lifes, ball_mini_img, WIDTH -130, 15)
    pygame.display.update()  #this is must be in the end!! 

pygame.quit()