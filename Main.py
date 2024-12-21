from typing import Any
import pygame, time, os, sys, random, openpyxl
    
# Define 
    # Screen size and title
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shoot out"
FPS = 60

    # Current working directory

cwd = os.path.dirname(__file__)

# Initialize the pygame library
pygame.init()

# Text font
font = pygame.font.SysFont("bahnschrift", 64)
font_Small = pygame.font.SysFont("bahnschrift", 32)

# Timers

static_time     =    0
dynamic_time    =    0
Delta_time      =    0

static_score_time = 0

# Attributes
Reload_time     = 1500 #Millisecs
Bullet_speed    = 7
Player_Speed    = 3.5
Enemy_Speed     = 2
Spawn_Rate      = 1
Score           = 0
scoreadd        = 1

# DICTIONARY

Bullet_Sides    = {'Left to Right': [0, 0, 0, Bullet_speed, 3],
                'Right to Left': [0, 0, Bullet_speed, 0, 4], 
                'Up to Down': [0, Bullet_speed, 0, 0, 1],
                'Down to Up': [Bullet_speed, 0, 0, 0, 2]}

powerups_list = ['heal',
            'superheal',
            'speed',
            'shootspeed',
            'scorex2'
            ]

def Chance(Percentage):
    x = random.randint(1, 100)

    if x <= Percentage:
        return True
    else:
        return False

Enemy_Sides     = ['Left', 'Right', 'Up', 'Down']

# Score

Score_surface = font.render("000", True, (255, 255, 255))
Score_rect = Score_surface.get_rect()
Score_rect.center = (SCREEN_WIDTH/2, 50)

# High_Score

High_Score_surface = font.render("High Score: 000", True, (255, 255, 255))
High_Score_rect = High_Score_surface.get_rect()
High_Score_rect.center = (SCREEN_WIDTH/2 + 50, SCREEN_HEIGHT/2)

# Save Score in Xcel Sheet

Scorebook = openpyxl.load_workbook(os.path.join(cwd ,"Score.xlsx"))
Scoresheet = Scorebook['Sheet1']
def score_save():
    global Score
    last_row = Scoresheet.max_row
    Scoresheet.cell(row=last_row + 1, column=1).value = Score

    # Save the Scoresheet
    Scorebook.save(os.path.join(cwd ,"Score.xlsx"))

score_list = []

for row in Scoresheet['A']:
    if row.value is None:
    # If it is, break out of the loop
        break
    score_list.append(row.value)

score_list.pop(0)

# Time
start_time = time.time()

Time_surface = font.render("00:00", True, (255, 255, 255))
Time_rect = Time_surface.get_rect()
Time_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

Milli_Time_Surface = font_Small.render("000", True, (230, 230, 230))

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Create the screen

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Load background and set background
background_image = pygame.image.load(os.path.join(cwd ,"Background.png"))
background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background_surface.blit(background_image,(0,0))

# Movement
up_speed     = 0
down_speed   = 0
left_speed   = 0
right_speed  = 0

## Sounds

pygame.mixer.init()
Background_Music = pygame.mixer.Sound(os.path.join(cwd,"BackgroundMusic.mp3"))
Background_Music.set_volume(0.1)
Background_Music.play(-1)

Menu_Background_Music = pygame.mixer.Sound(os.path.join(cwd,"BackgroundMusic.mp3"))
Menu_Background_Music.set_volume(0.1)

Shoot_Sound = pygame.mixer.Sound(os.path.join(cwd,"gunshot2.mp3"))
Shoot_Sound.set_volume(0.3)

Player_Hurt = pygame.mixer.Sound(os.path.join(cwd,"Player Hit.wav"))
Player_Hurt.set_volume(0.3)

Enemy_Hurt = pygame.mixer.Sound(os.path.join(cwd,"Enemy Hit.wav"))
Enemy_Hurt.set_volume(0.3)

Power_pickup = pygame.mixer.Sound(os.path.join(cwd,"powerup.wav"))
Power_pickup.set_volume(0.3)

## Making Bullets
# check if You can shoot
def canshoot():
    global static_time, dynamic_time, Delta_time, Reload_time
    if Delta_time > Reload_time:
        return True
    
    else:
        return False
    
## POWER UPS

class powerups(pygame.sprite.Sprite):
    def __init__(self, powerup_Cords, power):
        super().__init__()

        self.image = pygame.image.load(os.path.join(cwd, f"{power}.png"))
        self.assinged_power = power
        # Get bullet rectangle
        self.rect = self.image.get_rect()
        self.rect.center = powerup_Cords

    def heal():
        if player.Health < 3:
            player.Health += 1

    def Superheal():
        if player.Health < 3:
            player.Health = 3

    def speed():
        global Player_Speed
        Player_Speed += .5

    def shootspeed():
        global Reload_time
        if Reload_time > 100:
            Reload_time -= 250

    def scorex2():
        global static_score_time, dynamic_score_time
        static_score_time = dynamic_score_time


    def update(self):
        if self.rect.colliderect(player.rect):
            Power_pickup.play()
            if self.assinged_power == "heal":
                powerups.heal()
                self.kill()
            if self.assinged_power == "superheal":
                powerups.Superheal()
                self.kill()
            if self.assinged_power == "speed":
                powerups.speed()
                self.kill()
            if self.assinged_power == "shootspeed":
                powerups.shootspeed()
                self.kill()
            if self.assinged_power == "scorex2":
                powerups.scorex2()
                self.kill()

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, Bposx, Bposy, side ):
        super().__init__()


        # Get bullet speed based on side
        [self.bullet_up_speed ,
         self.bullet_down_speed ,
         self.bullet_left_speed ,
         self.bullet_right_speed ,
         self.image_png
         ] = Bullet_Sides.get(side)

        # Load bullet image
        self.image = pygame.image.load(os.path.join(cwd, f"Bullet{self.image_png}.png"))
        # Get bullet rectangle
        self.rect = self.image.get_rect()
        self.rect.center = (Bposx, Bposy)
        
        Shoot_Sound.play()

    def update(self):

        global Score

        # Update bullet position
        self.rect.centerx += (self.bullet_right_speed - self.bullet_left_speed)* dt
        self.rect.centery += (self.bullet_down_speed - self.bullet_up_speed)* dt

        # Check if u can shoot
        canshoot()

        # Check if bullet is out of screen
        if (self.rect.centery > SCREEN_HEIGHT + 100 or
             self.rect.centery <  -100 or
             self.rect.centerx > SCREEN_WIDTH + 100 or
             self.rect.centerx < -100
             ):
            self.kill()

        if pygame.sprite.spritecollide(self, enemy_Group, True):
            powerup_Cords = self.rect.center
            self.kill()
            Enemy_Hurt.play()
            Score += scoreadd

            if Chance(45) is True:
                power = random.choice(powerups_list)

                powerups_group.add(powerups(powerup_Cords, power))

## MAKING THE PLAYER SPRITE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()

        # Health
        self.Health = 3

        self.image = pygame.image.load(os.path.join(cwd, "player.png"))

            #Make Object
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


    def update(self):
        self.rect.centerx += (right_speed - left_speed)* dt
        self.rect.centery += (down_speed - up_speed)* dt

                # Borders
        if self.rect.bottom >= 590: 
            self.rect.bottom = 590

        if self.rect.top <= 10:
            self.rect.top = 10

        if self.rect.left <= 10:
            self.rect.left = 10

        if self.rect.right >=790:
            self.rect.right = 790

        if self.Health < 0:
            self.kill()
            pygame.quit()
            sys.exit()

    
# Put player into a Variable
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

## Make an Enemy
class enemy(pygame.sprite.pygame.sprite.Sprite):
    def __init__ (self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(cwd, "enemy.png"))

            #Make Object
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)

    def update(self):

        # Movement

        self.DistanceX = player.rect.centerx - self.rect.centerx
        self.DistanceY = player.rect.centery - self.rect.centery

        if abs(self.DistanceY) > abs(self.DistanceX):
            if self.DistanceY < 0:
                self.rect.centery -= Enemy_Speed* dt
            else:
                self.rect.centery += Enemy_Speed* dt

        elif abs(self.DistanceX) > abs(self.DistanceY):
            if self.DistanceX < 0:
                self.rect.centerx -= Enemy_Speed* dt
            else:
                self.rect.centerx += Enemy_Speed* dt

        else:
            if self.DistanceX < 0 and self.DistanceY < 0:
                self.rect.centerx -= Enemy_Speed* dt
                self.rect.centery -= Enemy_Speed* dt

            elif self.DistanceY < 0 and self.DistanceX > 0:
                self.rect.centery -= Enemy_Speed* dt
                self.rect.centerx += Enemy_Speed* dt

            elif self.DistanceY > 0 and self.DistanceX < 0:
                self.rect.centery += Enemy_Speed* dt
                self.rect.centerx -= Enemy_Speed* dt

            else:
                self.rect.centery += Enemy_Speed* dt
                self.rect.centerx += Enemy_Speed* dt

        # Player collision

        if self.rect.colliderect(player.rect):
            Player_Hurt.play()

            player.Health -= 1

            self.kill()

# Make a group for Sprites
player_Group = pygame.sprite.Group()
player_Group.add(player)

enemy_Group = pygame.sprite.Group()

Bullet_group = pygame.sprite.Group()

powerups_group = pygame.sprite.Group()

# Delta time
last_time = time.time()

# Create Game state
class gamestate():
    def __init__(self):
        self.state = 'Main_Menu'

    def main_game(self):
            # Amount of seconds between each loop

        global static_time, dynamic_time, Delta_time, last_time, Reload_time, dt,  up_speed, down_speed, left_speed, right_speed, static_score_time, dynamic_score_time, Delta_score_time, scoreadd, Score, Score_surface, Score_rect
        
        dt = time.time() - last_time
        dt *= 60
        last_time = time.time()

        # Timer for shooting
        dynamic_time = pygame.time.get_ticks()
        Delta_time = dynamic_time - static_time

        # Timer for scorex2
        dynamic_score_time = pygame.time.get_ticks()
        Delta_score_time = dynamic_score_time - static_score_time

        # Score system
        if Delta_score_time < 5000 and static_score_time > 0:
            scoreadd = 2

        else:
            scoreadd = 1

        # Indicator for the shooting

        if Delta_time < Reload_time/4:
            Indicator_State = 1

        elif Delta_time >= Reload_time/4 and Delta_time < Reload_time/4 * 2:
            Indicator_State = 2

        elif Delta_time >= Reload_time/4 * 2 and Delta_time < Reload_time/4 * 3:
            Indicator_State =  3 

        elif Delta_time >= Reload_time/4 * 3 :
            Indicator_State = 4

        else:
            Indicator_State = 1

        Indicator_image = pygame.image.load(os.path.join(cwd, f"indicator{Indicator_State}.png"))
        Indicator_rect = Indicator_image.get_rect()
        Indicator_rect.center = [70, SCREEN_HEIGHT - 70]

        # Health Indicator

        Health_Indicator_image = pygame.image.load(os.path.join(cwd, f"Health{abs(player.Health)}.png"))
        Health_Indicator_rect = Health_Indicator_image.get_rect()
        Health_Indicator_rect.topleft = [20, 20]

        # Get the current time
        current_time = time.time()

        # Calculate the elapsed time
        elapsed_time = current_time - start_time

        def _format_time(elapsed_time):
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            milliseconds = int((elapsed_time % 1) * 1000)
            return minutes, seconds, milliseconds
        
        # Format the elapsed time
        minutes, seconds, milliseconds = _format_time(elapsed_time)

        Time_surface = font.render(f"{minutes:02}:{seconds:02}", True, (230, 230, 230))
        Milli_Time_Surface = font_Small.render(f"{milliseconds}", True, (230, 230, 230))

        Milli_Time_Rect = Milli_Time_Surface.get_rect()

        # Score
        Score_Display = str(Score)
        Score_Display = Score_Display.zfill(3)
        Score_surface = font.render(f"{Score_Display}", True, (230, 230, 230))

        # unpack Cords
        [Milli_Time_Rect_BottomRightx , Milli_Time_Rect_BottomRighty] = Time_rect.bottomright

        Milli_Time_Rect.bottomleft = (Milli_Time_Rect_BottomRightx + 5 , Milli_Time_Rect_BottomRighty - 5)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                score_save()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    score_save()
                    pygame.quit()
                    sys.exit()


                if event.key == pygame.K_w:
                    up_speed = Player_Speed
                
                if event.key == pygame.K_s:
                    down_speed = Player_Speed

                if event.key == pygame.K_a:
                    left_speed = Player_Speed

                if event.key == pygame.K_d:
                    right_speed = Player_Speed

                if event.key == pygame.K_UP and canshoot() is True or event.key == pygame.K_UP and static_time == 0:
                    Bullet_group.add(Bullet(player.rect.centerx, player.rect.centery, 'Down to Up'))
                    static_time = pygame.time.get_ticks()
                
                if event.key == pygame.K_DOWN and canshoot() is True or event.key == pygame.K_DOWN and static_time == 0:
                    Bullet_group.add(Bullet(player.rect.centerx, player.rect.centery, 'Up to Down'))
                    static_time = pygame.time.get_ticks()

                if event.key == pygame.K_LEFT and canshoot() is True or event.key == pygame.K_LEFT and static_time == 0:
                    Bullet_group.add(Bullet(player.rect.centerx, player.rect.centery, 'Right to Left'))
                    static_time = pygame.time.get_ticks()

                if event.key == pygame.K_RIGHT and canshoot() is True  or event.key == pygame.K_RIGHT and static_time == 0:
                    Bullet_group.add(Bullet(player.rect.centerx, player.rect.centery, 'Left to Right'))
                    static_time = pygame.time.get_ticks()

                if event.key == pygame.K_e:
                    powerups.scorex2()
                

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_w:
                    up_speed = 0
                
                if event.key == pygame.K_s:
                    down_speed = 0

                if event.key == pygame.K_a:
                    left_speed = 0

                if event.key == pygame.K_d:
                    right_speed = 0

        ## UPDATE GAME

        if Chance(Spawn_Rate) is True:
            side = random.choice(Enemy_Sides)

            if side == 'Left':
                enemy_Group.add(enemy(-40, random.randint(0, SCREEN_HEIGHT)))
            
            if side == 'Right':
                enemy_Group.add(enemy(SCREEN_WIDTH + 40, random.randint(0, SCREEN_HEIGHT)))

            if side == 'Up':
                enemy_Group.add(enemy(random.randint(0, SCREEN_WIDTH), - 40))

            if side == 'Down':
                enemy_Group.add(enemy(random.randint(0, SCREEN_WIDTH), - 40))

        player_Group.update()
        powerups_group.update()
        Bullet_group.update()
        enemy_Group.update()
        
        # Draw the game 
        screen.blit(background_surface,[0,0]) , 
        screen.blit(Time_surface, Time_rect), 
        screen.blit(Milli_Time_Surface , Milli_Time_Rect)
        screen.blit(Score_surface, Score_rect)
        powerups_group.draw(screen)
        player_Group.draw(screen)
        enemy_Group.draw(screen)
        Bullet_group.draw(screen)
        screen.blit(Indicator_image, Indicator_rect)
        screen.blit(Health_Indicator_image, Health_Indicator_rect)

        # Flip the display
        pygame.display.flip()

    def Main_Menu(self):

        global High_Score_surface, High_Score_rect, score_list

        High_Score = max(score_list)

        High_Score_Display = str(High_Score)
        High_Score_Display = High_Score_Display.zfill(3)
        High_Score_surface = font_Small.render(f"High Score: {High_Score_Display}", True, (230, 230, 230))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    self.state = 'main_game'
                    self.gamestate_manager()

        menu_Background = pygame.image.load(os.path.join(cwd, f"MenuBackground.png"))
        screen.blit(menu_Background, (0,0))
        screen.blit(High_Score_surface, High_Score_rect)
    
        pygame.display.flip()

    def Death_Screen():
        pass
    
    def gamestate_manager(self):
        if self.state == 'main_game':
            self.main_game()

        if self.state == 'Main_Menu':
            self.Main_Menu()

game_state = gamestate()

## Create a game loop

while True:
    game_state.gamestate_manager()

    clock.tick(FPS)
