import pygame, sys, random

pygame.init()
pygame.mixer.init()

# === SETUP LAYAR ===
SCREEN = pygame.display.set_mode((288, 512))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 120

# === ASSET GAMBAR ===
bg_surface = pygame.image.load('assets/background-day.png').convert()

# --- Burung (3 frame animasi) ---
bird_downflap = pygame.image.load('assets/bluebird-downflap.png').convert_alpha()
bird_midflap = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
bird_upflap  = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(50, 256))

BIRDFLAP = pygame.USEREVENT
pygame.time.set_timer(BIRDFLAP, 200)

# --- Lantai ---
floor_surface = pygame.image.load('assets/base.png').convert()
floor_x_pos = 0
def draw_floor():
    SCREEN.blit(floor_surface, (floor_x_pos, 450))
    SCREEN.blit(floor_surface, (floor_x_pos + 288, 450))

# --- Pipa ---
pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_list = []
pipe_height = [200, 250, 300, 350, 400]

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(300, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(300, random_pipe_pos - 150))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    return [pipe for pipe in pipes if pipe.right > -25]

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512:
            SCREEN.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            SCREEN.blit(flip_pipe, pipe)

SPAWNPIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, 1200)

# --- FISIKA BURUNG ---
gravity = 0.1
bird_movement = 0
game_active = False
start = False

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_rect = new_bird.get_rect(center=(50, bird_rect.centery))
    return new_bird, new_rect

# --- TITLE SCREEN ---
title_surface = pygame.image.load('assets/message.png').convert_alpha()
title_rect = title_surface.get_rect(center=(144, 256))

# --- SUARA ---
flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
point_sound = pygame.mixer.Sound('sound/sfx_point.wav')

# --- SKOR ---
game_font = pygame.font.Font(None, 40)
score = 0
high_score = 0
can_score = True

def display_score(state):
    if state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(144, 50))
        SCREEN.blit(score_surface, score_rect)
    elif state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(144, 50))
        SCREEN.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(144, 100))
        SCREEN.blit(high_score_surface, high_score_rect)

def update_score():
    global score, can_score
    for pipe in pipe_list:
        if 45 < pipe.centerx < 55 and can_score:
            score += 1
            point_sound.play()
            can_score = False
        if pipe.centerx < 0:
            can_score = True

# --- CEK TABRAKAN ---
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= 450:
        hit_sound.play()
        return False
    return True

# === GAME LOOP ===
while True:
    clock.tick(FPS)
    clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # --- KEYBOARD dan MOUSE ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                clicked = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                clicked = True

        # --- EVENT BURUNG & PIPA ---
        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird_surface, bird_rect = bird_animation()

        # --- MULAI & RESTART GAME ---
        if clicked and not game_active:
            game_active = True
            pipe_list.clear()
            bird_rect.center = (50, 256)
            bird_movement = 0
            score = 0
            start = False
        if clicked and game_active:
            start = True
            bird_movement = -5
            flap_sound.play()

    # === RENDER LAYAR ===
    SCREEN.blit(bg_surface, (0, 0))

    if game_active:
        if start:
            bird_movement += gravity
            bird_rect.centery += bird_movement
            game_active = check_collision(pipe_list)
        SCREEN.blit(bird_surface, bird_rect)
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        update_score()
        display_score('main_game')
    else:
        SCREEN.blit(title_surface, title_rect)
        display_score('game_over')

    # --- LANTAI BERGERAK ---
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -288:
        floor_x_pos = 0

    if score > high_score:
        high_score = score

    pygame.display.update()
