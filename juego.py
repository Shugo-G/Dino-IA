import pygame
import random
from clases import Dinosaurio, Pajaro, Cactus, Bg

pygame.init()

#CONSTANTES
ANCHO = 800
ALTO = 400
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
texto_final = "Juega más, llora menos"

#Pantalla
win = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("DinoRun by Shugo")

#VARIABLES GLOBALES
posDef_X = 100
posDef_Y = 380
puntuacion = 0
game_speed = 12
obstacutlo_timer = 0
obstaculo_cooldown = 1000
spawn_obtaculo = False
game_over = False
clock = pygame.time.Clock()

#FUENTES
consolas = pygame.font.match_font('consolas')

#OBJETOS
dino = Dinosaurio(posDef_X, posDef_Y)
fondo = Bg(0,370)

# GRUPOS DE SPRITES Y OBJETOS
grupo_enemigos = pygame.sprite.Group()
rex = pygame.sprite.GroupSingle()
rex.add(dino)

# Funcion para dibujar elementos
def redraw():
    win.fill(BLANCO)
    fondo.draw(win, game_speed)
    rex.update()
    rex.draw(win)
    grupo_enemigos.update(game_speed)
    grupo_enemigos.draw(win)
    mostrar_texto(win, consolas, str(int(puntuacion)), NEGRO, 40, 700, 50)
    if game_over:
        mostrar_texto(win, consolas, texto_final, NEGRO, 50, ANCHO // 2, ALTO // 2)
    pygame.display.flip()
    pygame.display.update()

def end_game(keys):
    global game_speed    
    game_speed = 0
    if keys[pygame.K_ESCAPE]:
        global game_over, puntuacion
        game_over = False
        grupo_enemigos.empty()
        game_speed = 12
        puntuacion = 0

def mostrar_texto(pantalla,fuente,texto,color, dimensiones, x, y):
    tipo_letra = pygame.font.Font(fuente,dimensiones)
    superficie = tipo_letra.render(texto,True, color)
    rectangulo = superficie.get_rect()
    rectangulo.center = (x, y)
    pantalla.blit(superficie,rectangulo)

run = True
while run:
    keys = pygame.key.get_pressed()
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
    
    print(len(grupo_enemigos))

    if not (dino.isJump):  #mientras no salta
        if  keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            dino.porSaltar()
        if keys[pygame.K_DOWN]:
            dino.agacharse()
        else:
            dino.isDown = False
            dino.rect.bottom = posDef_Y
    else:   # Cuando está saltando 
        dino.saltando()    
        if keys[pygame.K_DOWN]:
            dino.cayendo()
   
    # Detectar Colisiones
    colision = pygame.sprite.spritecollide(dino, grupo_enemigos, False)
    if colision:
        game_over = True
    if game_over:
        end_game(keys)
    else:
        if pygame.time.get_ticks() - obstacutlo_timer >= obstaculo_cooldown:
            spawn_obtaculo = True
    
        if spawn_obtaculo:
            if random.randint(0, 10) == 0:
                ave = Pajaro(posDef_X, posDef_Y)
                grupo_enemigos.add(ave)
                obstacutlo_timer = pygame.time.get_ticks()
                spawn_obtaculo = False
                obstaculo_cooldown = random.randint(700, 1000)
            else:
                cactus = Cactus(posDef_Y)
                grupo_enemigos.add(cactus)
                obstacutlo_timer = pygame.time.get_ticks()
                spawn_obtaculo = False
                obstaculo_cooldown = random.randint(800, 1200)           
        
        game_speed += 0.020
        puntuacion += 0.5
    redraw()

pygame.QUIT()