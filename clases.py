import pygame
import random

#VARIABLES GLOBALES
ANCHO = 800
ALTO = 400
BLANCO = (255, 255, 255)

class Dinosaurio(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.correr = [pygame.image.load('Assets/DinoRun1.png').convert(),
                       pygame.image.load('Assets/DinoRun2.png').convert()]

        self.saltar = pygame.image.load('Assets/DinoJump.png').convert()

        self.agachado = [pygame.image.load('Assets/DinoDown1.png').convert(),
                         pygame.image.load('Assets/DinoDown2.png').convert()]

        self.numSprite = 0
        self.x = x
        self.y = y
        self.image = self.correr[self.numSprite]
        self.image.set_colorkey(BLANCO)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.x = x
        self.isJump = False
        self.isDown = False
        self.jumpCount = 10
        
    def porSaltar(self):
        self.isJump = True
        self.isDown = False
        self.numSprite = 0
    def agacharse(self):
        self.isDown = True
        self.rect.bottom = self.y + 20
    def saltando(self):
        if self.jumpCount >= -10:
            self.rect.bottom -= (self.jumpCount * abs(self.jumpCount)) * 0.3
            self.jumpCount -= 1.5
        else:
            self.jumpCount = 10
            self.isJump = False
            self.isDown = False
    def cayendo(self):
            if self.jumpCount >= -10:
                self.rect.bottom = self.y
                self.isJump = False
                self.jumpCount = 10

    def update(self):
        self.numSprite += 0.25
        if self.numSprite >= 2:
            self.numSprite = 0
        if self.isJump:
            self.image = self.saltar
        elif self.isDown:
            self.image = self.agachado[int(self.numSprite)]
        else:
            self.image = self.correr[int(self.numSprite)]

class Cactus (pygame.sprite.Sprite):
    def __init__(self, y):
        super().__init__()
        self.grupo_cactus = [pygame.image.load('Assets/cactus1.png').convert(),
                            pygame.image.load('Assets/cactus2.png').convert(),
                            pygame.image.load('Assets/cactus3.png').convert(),
                            pygame.image.load('Assets/cactus4.png').convert(),
                            pygame.image.load('Assets/cactus5.png').convert(),
                            pygame.image.load('Assets/cactus6.png').convert()]
        self.y = y
        self.tipoCactus = random.randint(0, 5)
        self.image = self.grupo_cactus[self.tipoCactus]
        self.image.set_colorkey(BLANCO)
        self.rect = self.image.get_rect()
        self.rect.bottom = self.y
        self.rect.x = ANCHO
    
    def update (self, game_speed):
        self.rect.x -= game_speed
        if self.rect.right < 0:
            self.kill()

class Pajaro (pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.grupo_aves = [pygame.image.load('Assets/pajaro1.png').convert(),
                      pygame.image.load('Assets/pajaro2.png').convert()]
        self.x = x
        self.y = y
        self.numSprite = 0
        self.image = self.grupo_aves[self.numSprite]
        self.image.set_colorkey(BLANCO)
        self.rect = self.image.get_rect()
        self.rect.x = ANCHO
        self.rect.bottom = random.choice([y, y -30, y -100])

    
    def update (self, game_speed):
        self.numSprite += 0.25
        if self.numSprite >= 2:
            self.numSprite = 0
        self.rect.x -= game_speed
        self.image = self.grupo_aves[int(self.numSprite)]
        if self.rect.right < 0:
            self.kill()

class Bg(object):
    suelo = pygame.image.load('Assets/bg.png')

    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw (self, win, game_speed):
        self.x -= game_speed
        win.blit(self.suelo, (self.x, self.y))
        win.blit(self.suelo, (self.x + 1202, self.y))
        if self.x <= -1202:
            self.x = 0