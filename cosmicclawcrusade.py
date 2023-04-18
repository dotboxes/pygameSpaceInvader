import pygame
import pygame.mixer
import random
import time

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("song.mp3")
pygame.mixer.music.play(-1)

won = False
lost = False

players_fighting = False

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Claw Crusade")

# Load images
player_img = pygame.image.load("spaceCat1.png")
enemy_img = pygame.image.load("Alien1.png")
bg_img = pygame.image.load("background2.png")
bg_img = pygame.transform.scale(bg_img, (800, 800))  # Resize the background image to the desired dimensions
bunker_img = pygame.image.load("bunker.png")

# Colors
WHITE = (255, 255, 255)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("spaceCat1.png")  # Load the first player image
        self.image = pygame.transform.scale(self.image, (82, 82))  # Resize the image to the desired dimensions
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))

class Player2(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("spaceCat2.png")  # Load the second player image
        self.image = pygame.transform.scale(self.image, (82, 82))  # Resize the image to the desired dimensions
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        #self.image = pygame.transform.rotate(player_img, 180)  # Rotate the sprite
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5

        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        
# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.image = pygame.transform.scale(self.image, (64, 64))  # Resize the image to the desired dimensions
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.move_speed = 7

    def update(self):
        self.rect.x += self.direction * self.move_speed
        if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
            self.direction *= -1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((2, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direction = direction
    
    def update(self):
        self.rect.y += self.direction * 10
        if self.rect.y < -self.rect.height or self.rect.y > HEIGHT:
            self.kill()

# class for the Bunker (the walls to protect the ship)
class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bunker_img
        self.image = pygame.transform.scale(self.image, (100, 100))  # Resize the image to the desired dimensions
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hit_count = 0  # Add hit_count attribute

    def update(self):
        damage_points = pygame.sprite.spritecollide(self, player_bullets, False)
        damage_points += pygame.sprite.spritecollide(self, enemy_bullets, False)

        for damage_point in damage_points:
            x_offset = damage_point.rect.x - self.rect.x
            y_offset = damage_point.rect.y - self.rect.y
            if y_offset < 0: y_offset = 0

            self.image.set_at((x_offset, y_offset), (0,0,0))
            damage_point.kill()

            self.hit_count += 1  # Update the hit_count
            if self.hit_count >= 10:  # Remove bunker after 3 hits
                self.kill()
                
def check_collision(group1, group2):
    collided_pairs = {}
    for sprite1 in group1:
        for sprite2 in group2:
            if pygame.sprite.collide_rect(sprite1, sprite2):
                sprite1.kill()
                sprite2.kill()
                collided_pairs[sprite1] = sprite2
    return collided_pairs


# Main game loop


running = True
clock = pygame.time.Clock()
player = Player(WIDTH // 2, HEIGHT - 100)
player2 = Player2(WIDTH // 2, 50)
player_sprites = pygame.sprite.Group()
player_sprites.add(player)
player_sprites.add(player2)
enemy_sprites = pygame.sprite.Group()
for i in range(10):
    enemy = Enemy(random.randint(0, WIDTH - enemy_img.get_width()), random.randint(HEIGHT//2 - 100, HEIGHT//2 + 50))
    enemy_sprites.add(enemy)
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player_lives = 3
player2_lives = 3
shoot_cooldown = 0
shoot_cooldown2 = 0
enemy_shoot_cooldown = 1

bunker_sprites = pygame.sprite.Group()
bunker_sprites2 = pygame.sprite.Group()
for i in range(4):
    bunker = Bunker(75 + i * 200, HEIGHT - 250)
    bunker2 = Bunker(75 + i * 200, 150)
    bunker_sprites.add(bunker)
    bunker_sprites2.add(bunker2)

score = 0
score2 = 0

font = pygame.font.Font(None, 36)


while running:

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic
    player_sprites.update()
    enemy_sprites.update()

    # Change the game state to players_fighting when all aliens are killed
    if not players_fighting and len(enemy_sprites) == 0:
        players_fighting = True
        score_text = font.render("Aliens defeated! Fight each other!", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - 200, HEIGHT // 2 - 20))
        pygame.display.flip()
        pygame.time.delay(2000)

    ##########################################################
    # Shooting logic
    ##########################################################
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and shoot_cooldown <= 0 and player_lives > 0:
        bullet = Bullet(player.rect.centerx, player.rect.top, -1)
        player_bullets.add(bullet)
        shoot_cooldown = 10
    shoot_cooldown -= 1

    if keys[pygame.K_w] and shoot_cooldown2 <= 0 and player2_lives > 0:
        bullet = Bullet(player2.rect.centerx, player2.rect.bottom, 1)  # Changed to player2.rect.bottom
        player_bullets.add(bullet)
        shoot_cooldown2 = 10
    shoot_cooldown2 -= 1


    if enemy_shoot_cooldown <= 0 and len(enemy_sprites) > 0:
        random_enemy = random.choice(enemy_sprites.sprites())
        if random_enemy is not None:
            bullet_up = Bullet(random_enemy.rect.centerx, random_enemy.rect.top, -1)
            bullet_down = Bullet(random_enemy.rect.centerx, random_enemy.rect.bottom, 1)
            enemy_bullets.add(bullet_up)
            enemy_bullets.add(bullet_down)
        enemy_shoot_cooldown = 100
    enemy_shoot_cooldown -= 1
    
    player_bullets.update()
    enemy_bullets.update()

    collided_pairs = check_collision(player_bullets, enemy_sprites)
    if collided_pairs:
        for bullet, enemy in collided_pairs.items():
            if bullet.direction == -1:  # Bullet shot by Player 1
                score += 10
            else:  # Bullet shot by Player 2
                score2 += 10

    #test who wins
    if players_fighting:
        player1_hit = pygame.sprite.spritecollide(player, player_bullets, False)
        player2_hit = pygame.sprite.spritecollide(player2, player_bullets, False)

        if player1_hit:
            player_lives -= 1
            player1_hit[0].kill()

        if player2_hit:
            player2_lives -= 1
            player2_hit[0].kill()

    else:
        player_hit = pygame.sprite.spritecollide(player, enemy_bullets, True) or pygame.sprite.spritecollide(player, enemy_sprites, False)
        player2_hit = pygame.sprite.spritecollide(player2, enemy_bullets, True) or pygame.sprite.spritecollide(player2, enemy_sprites, False)

        if player_hit and player_lives > 0:
            player_lives -= 1
        if player2_hit and player2_lives > 0:
            player2_lives -= 1

            
    player_hit = pygame.sprite.spritecollide(player, enemy_bullets, True) or pygame.sprite.spritecollide(player, enemy_sprites, False)
    player2_hit = pygame.sprite.spritecollide(player2, enemy_bullets, True) or pygame.sprite.spritecollide(player2, enemy_sprites, False)
    
    if player_hit and player_lives > 0:
        player_lives -= 1
    if player2_hit and player2_lives > 0:
        player2_lives -= 1

    if player_lives <= 0:
        player.kill()
    if player2_lives <= 0:
        player2.kill()

    
    if player_lives <= 0:
        player.kill()
        won = True
        break
    if player2_lives <= 0:
        player2.kill()
        won = True
        break

    # Refresh rate
    clock.tick(60)

    # Drawing on the screen
    screen.fill((0, 0, 0))
    screen.blit(bg_img, (0, 0))
    player_sprites.draw(screen)
    enemy_sprites.draw(screen)
    player_bullets.draw(screen)
    enemy_bullets.draw(screen)
    bunker_sprites.draw(screen)
    bunker_sprites2.draw(screen)
    
    bunker_sprites.update()  # Add this line to make the bunkers protect the players
    bunker_sprites2.update()  # Add this line to make the bunkers protect the players


    score_text = font.render(f'Score P1: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    score_text2 = font.render(f'Score P2: {score2}', True, WHITE)
    screen.blit(score_text2, (10, 35))

    lives_text = font.render(f'Lives P1: {player_lives}', True, WHITE)
    screen.blit(lives_text, (WIDTH - 150, 10))  # Modified width offset
    lives_text2 = font.render(f'Lives P2: {player2_lives}', True, WHITE)
    screen.blit(lives_text2, (WIDTH - 150, 35))  # Modified width offset

    pygame.display.flip()
    
if won:
    win_text = "Player1 Wins!" if player_lives > 0 else "Player2 Wins!"
else:
    win_text = "Both Lost! :("


win_screen = pygame.display.set_mode((WIDTH, HEIGHT))
win_screen.fill((0, 0, 0))
win_text = font.render(win_text, True, WHITE)
win_screen.blit(win_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:  # Wait for input before ending the screen
            running = False
            break

time.sleep(3)

pygame.quit()
