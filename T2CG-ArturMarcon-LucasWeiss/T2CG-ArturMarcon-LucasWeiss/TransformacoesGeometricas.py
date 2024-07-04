# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from Instancia import *
from ModeloMatricial import *
from ListaDeCoresRGB import *
from datetime import datetime
import time
from datetime import timedelta
import random
from dotenv import load_dotenv

import os
os.environ['PATH'] += 'C:\MinGW\bin'

# ***********************************************************************************

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()

# Limites da Janela de Seleção

Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [Instancia() for x in range(100)]

AREA_DE_BACKUP = 50 # posicao a partir da qual sao armazenados backups dos personagens

# lista de modelos
Modelos = []

angulo = 0.0
PersonagemAtual = -1
nInstancias = 0

imprimeEnvelope = False

LarguraDoUniverso = 10.0

TempoInicial = time.time()
TempoTotal = time.time()
TempoAnterior = time.time()

load_dotenv()

# define uma funcao de limpeza de tela
from os import system, name
def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        print("*******************")
        print ("PWD: ", os.getcwd()) 
        
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# ***********************************************************************************
def DesenhaMastro():
    Mastro.desenhaPoligono()

# ***********************************************************************************
def DesenhaSeta():
    glPushMatrix()
    MeiaSeta.desenhaPoligono()
    glScaled(1,-1, 1)
    MeiaSeta.desenhaPoligono()
    glPopMatrix()

# ***********************************************************************************
def DesenhaApontador():
    glPushMatrix()
    glTranslated(-4, 0, 0)
    DesenhaSeta()
    glPopMatrix()
# **********************************************************************
def DesenhaHelice():
    glPushMatrix()
    for i in range (4):   
        glRotatef(90, 0, 0, 1)
        DesenhaApontador()
    glPopMatrix()

# ***********************************************************************************
def DesenhaHelicesGirando():
    global angulo
    #print ("angulo:", angulo)
    glPushMatrix()
    glRotatef(angulo, 0, 0, 1)
    DesenhaHelice()
    glPopMatrix()

# ***********************************************************************************
def DesenhaCatavento():
    #glLineWidth(3)
    glPushMatrix()
    DesenhaMastro()
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslated(0,3,0)
    glScaled(0.2, 0.2, 1)
    DesenhaHelicesGirando()
    glPopMatrix()
    glPopMatrix()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# ***********************************************************************************
def TestaColisao(P1, P2) -> bool:
    # existing collision testing code...

    for i in range(4):
        A = Personagens[P1].Envelope[i]
        B = Personagens[P1].Envelope[(i + 1) % 4]
        for j in range(4):
            C = Personagens[P2].Envelope[j]
            D = Personagens[P2].Envelope[(j + 1) % 4]
            if HaInterseccao(A, B, C, D):
                return True
    return False

def colideLimite(P1, size):
    for i in range(4):
        x = Personagens[P1].Envelope[i].getX()
        y = Personagens[P1].Envelope[i].getY()
        if x < -size:
            Personagens[P1].Posicao = Ponto(size - 12, y)
            return True
        elif x > size:
            Personagens[P1].Posicao = Ponto(-size + 12, y)
            return True
        elif y < -size:
            Personagens[P1].Posicao = Ponto(x, size - 12)
            return True
        elif y > size:
            Personagens[P1].Posicao = Ponto(x, -size + 12)
            return True
    return False


# ***********************************************************************************
def AtualizaEnvelope(i):
    global Personagens, imprimeEnvelope
    id = Personagens[i].IdDoModelo
    MM = Modelos[id]

    P = Personagens[i]
    V = P.Direcao * (MM.nColunas/2.0)
    V.rotacionaZ(90)
    A = P.PosicaoDoPersonagem + V
    B = A + P.Direcao*MM.nLinhas
    
    V = P.Direcao * MM.nColunas
    V.rotacionaZ(-90)
    C = B + V

    V = P.Direcao * -1 * MM.nLinhas
    D = C + V

    # Desenha o envelope
 
    SetColor(Red)
    glBegin(GL_LINE_LOOP)
    glVertex2f(A.x, A.y)
    glVertex2f(B.x, B.y)
    glVertex2f(C.x, C.y)
    glVertex2f(D.x, D.y)
    glEnd()
    
    # if (imprimeEnvelope):
    #     A.imprime("A:");
    #     B.imprime("B:");
    #     C.imprime("C:");
    #     D.imprime("D:");
    #     print("");

    Personagens[i].Envelope = [A, B, C, D]

# ***********************************************************************************
# Gera sempre uma posicao na metade de baixo da tela
def GeraPosicaoAleatoria():
    x = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
    y = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
    return Ponto(x, y)

game_over = False

recent_death = datetime.now()
death_cd = 2

initialize = datetime.now()

lifes = 3

# ***********************************************************************************
def AtualizaJogo():
    global imprimeEnvelope, nInstancias, Personagens, enemies_killed, lifes, game_over, recent_death, death_cd
    #  Esta funcao deverá atualizar todos os elementos do jogo
    #  em funcao das novas posicoes dos personagens
    #  Entre outras coisas, deve-se:
    
    #   - calcular colisões
    #  Para calcular as colisoes eh preciso fazer o calculo do envelopes de
    #  todos os personagens
    if lifes == 0:
        game_over = True
    for i in range (0, nInstancias):
        AtualizaEnvelope(i) 
        if (imprimeEnvelope): # pressione E para alterar esta flag
            print("Envelope ", i)
            Personagens[i].ImprimeEnvelope("","")
    imprimeEnvelope = False

    # Feito o calculo, eh preciso testar todos os tiros e
    # demais personagens contra o jogador

    for i in range(nInstancias):
        if Personagens[i].IdDoModelo != 1 and Personagens[i].IdDoModelo != 5:
            colideLimite(i, LarguraDoUniverso)

    current_time = datetime.now()

    for i in range (nInstancias):
        if (current_time - initialize).total_seconds() <= 0.2 and Personagens[i].IdDoModelo in [2,3,4]:
            Personagens[i] = copy.deepcopy(Personagens[i+AREA_DE_BACKUP]) 
            Personagens[i].Posicao = GeraPosicaoAleatoria()
            Personagens[i].Posicao.imprime("Nova posicao:")
            ang = random.randint(0, 360)
            Personagens[i].Rotacao = ang
            Personagens[i].Direcao = Ponto(0,1)
            Personagens[i].Direcao.rotacionaZ(ang)
            print ("Nova Orientacao: ", ang)
        for j in range(nInstancias):
            if TestaColisao(0, i) and i != 0:
                if (current_time - recent_death).total_seconds() >= death_cd:
                    lifes-=1
                    recent_death = current_time
                    # neste exemplo, a posicao do tiro é gerada aleatoriamente apos a colisao
                    Personagens[0] = copy.deepcopy(Personagens[0+AREA_DE_BACKUP]) 
                    Personagens[0].Posicao = GeraPosicaoAleatoria()
                    Personagens[0].Posicao.imprime("Nova posicao:")
                    ang = random.randint(0, 360)
                    Personagens[0].Rotacao = ang
                    Personagens[0].Direcao = Ponto(0,1)
                    Personagens[0].Direcao.rotacionaZ(ang)
                    print ("Nova Orientacao: ", ang)
            if Personagens[i].IdDoModelo in [2,3,4] and Personagens[j].IdDoModelo == 1:
                if TestaColisao(i, j):
                    enemies_killed+=1
                    # neste exemplo, a posicao do tiro é gerada aleatoriamente apos a colisao
                    Personagens[i] = copy.deepcopy(Personagens[i+AREA_DE_BACKUP]) 
                    Personagens[i].Posicao = GeraPosicaoAleatoria()
                    Personagens[i].Posicao.imprime("Nova posicao:")
                    ang = random.randint(0, 360)
                    Personagens[i].Rotacao = ang
                    Personagens[i].Direcao = Ponto(0,1)
                    Personagens[i].Direcao.rotacionaZ(ang)
                    print ("Nova Orientacao: ", ang)

        else:
            pass
            # print ("SEM Colisao")
        


# ***********************************************************************************
def AtualizaPersonagens(tempoDecorrido):
    global nInstancias
    for i in range (0, nInstancias):
       Personagens[i].AtualizaPosicao(tempoDecorrido) #(tempoDecorrido)
    AtualizaJogo()

# ***********************************************************************************
def DesenhaPersonagens():
    global PersonagemAtual, nInstancias
    
    for i in range (0, nInstancias):
        PersonagemAtual = i
        Personagens[i].Desenha()
        
# ***********************************************************************************
def display():
    global TempoInicial, TempoTotal, TempoAnterior, game_over, enemies_killed

    TempoAtual = time.time()
    TempoTotal = TempoAtual - TempoInicial
    DiferencaDeTempo = TempoAtual - TempoAnterior

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(1, 1, 1)  # R, G, B [0..1]

    DesenhaPersonagens()
    AtualizaPersonagens(DiferencaDeTempo)
    enemy_shoot()

    # Render the enemies killed counter
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 0)  # Red color for the counter
    drawText((-100, 100), f'Enemies killed: {enemies_killed}')
    drawText((90, 100), f'Lifes: {lifes}')
    glPopMatrix()

    glutSwapBuffers()
    TempoAnterior = TempoAtual

    if game_over:
        # Render the "Game Over" message
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 0, 0)  # Red color for the text
        drawText((-50, 0), "Game Over")
        glPopMatrix()
        glutSwapBuffers()
        
        # Add a delay before exiting
        time.sleep(2)
        os._exit(0)
    
    if enemies_killed >= int(os.getenv('ENEMIES_KILLED')):
                # Render the "Game Over" message
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1, 1, 1)  # Red color for the text
        drawText((-50, 0), "You win!")
        glPopMatrix()
        
        glutSwapBuffers()
        
        # Add a delay before exiting
        time.sleep(2)
        os._exit(0)
        

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    global imprimeEnvelope
    # If escape is pressed, kill everything.
    if args[0] == b'q' or args[0] == ESCAPE:
        os._exit(0)
    elif args[0] == b'e':
        if imprimeEnvelope == False:
            imprimeEnvelope = True
        if imprimeEnvelope == True:
            imprimeEnvelope = False
    elif args[0] == b' ':  # Spacebar pressed
        shoot_bullet()
    # Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        Personagens[0].AtualizaPosicao(0.05)
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        pass
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        Personagens[0].Rotacao += 10
        Personagens[0].Direcao.rotacionaZ(+10)
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        Personagens[0].Rotacao -= 10
        Personagens[0].Direcao.rotacionaZ(-10)

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

# ***********************************************************************************
def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    Mastro.LePontosDeArquivo("Mastro.txt")

    Modelos.append(ModeloMatricial())
    Modelos[0].leModelo("Spaceship.txt")
    Modelos.append(ModeloMatricial())
    Modelos[1].leModelo("Projetil.txt")
    Modelos.append(ModeloMatricial())
    Modelos[2].leModelo("inimigo1.txt")
    Modelos.append(ModeloMatricial())
    Modelos[3].leModelo("inimigo2.txt")
    Modelos.append(ModeloMatricial())
    Modelos[4].leModelo("inimigo3.txt")
    Modelos.append(ModeloMatricial())
    Modelos[5].leModelo("ProjetilHostil.txt")

    print ("Modelo 0")
    Modelos[0].Imprime()
    print ("Modelo 1")
    Modelos[1].Imprime()


def DesenhaCelula():
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()
    pass

def DesenhaBorda():
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagemMatricial():
    global PersonagemAtual, count

    MM = ModeloMatricial()
    
    ModeloDoPersonagem = Personagens[PersonagemAtual].IdDoModelo
        
    MM = Modelos[ModeloDoPersonagem]
    # MM.Imprime("Matriz:")
      
    glPushMatrix()
    larg = MM.nColunas
    alt = MM.nLinhas
    # print (alt, " LINHAS e ", larg, " COLUNAS")
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt-1-i,j)
            if cor != -1: # nao desenha celulas com -1 (transparentes)
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                #DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()



# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
bulletN = 1

bulletN = 1
reload_start_time = 0
is_reloading = False

shoot_interval = 0.1
last_shot = datetime.now()
reload_time = 2
last_reload = datetime.now()

def shoot_bullet():
    global bulletN, shoot_interval, last_shot, reload_time, last_reload
    current_time = datetime.now()
    if (current_time - last_shot).total_seconds() >= shoot_interval and (current_time - last_reload).total_seconds() >= reload_time:
        Personagens[bulletN].Posicao = Personagens[0].Posicao + (Personagens[0].Direcao * (Modelos[Personagens[0].IdDoModelo].nLinhas+0.1)) + Personagens[0].Pivot - Ponto(0.5,0)
        Personagens[bulletN].Escala = Ponto (1,1)
        Personagens[bulletN].Rotacao = copy.deepcopy(Personagens[0].Rotacao)
        Personagens[bulletN].IdDoModelo = 1
        Personagens[bulletN].Modelo = DesenhaPersonagemMatricial
        Personagens[bulletN].Pivot = Ponto(0.5,0)
        Personagens[bulletN].Direcao = copy.deepcopy(Personagens[0].Direcao) # direcao do movimento para a cima
        Personagens[bulletN].Velocidade = 120   # move-se a 3 m/s

        last_shot = current_time
        if bulletN > 10:
            bulletN = 1
            last_reload = current_time
        else:
            bulletN+=1

eBullet = 10
enemy_shoot_intervals = {}
enemy_last_shot_time = {}
def enemy_shoot():
    global enemy_last_shot_time, enemy_shoot_intervals, eBullet
    current_time = datetime.now()
    
    for i in range(21, nInstancias):
        if (current_time - enemy_last_shot_time[i]).total_seconds() >= enemy_shoot_intervals[i]:
            Personagens[eBullet].Posicao = Personagens[i].Posicao + (Personagens[i].Direcao * (Modelos[Personagens[i].IdDoModelo].nLinhas+0.1)) + Personagens[i].Pivot - Ponto(0.5,0)
            Personagens[eBullet].Escala = Ponto (1,1)
            Personagens[eBullet].Rotacao = copy.deepcopy(Personagens[i].Rotacao)
            Personagens[eBullet].IdDoModelo = 5
            Personagens[eBullet].Modelo = DesenhaPersonagemMatricial
            Personagens[eBullet].Pivot = Ponto(0.5,0)
            Personagens[eBullet].Direcao = copy.deepcopy(Personagens[i].Direcao) # direcao do movimento
            Personagens[eBullet].Velocidade = 60  # move-se a 6 m/s

            # Reset shooting timer
            enemy_last_shot_time[i] = current_time
            enemy_shoot_intervals[i] = random.uniform(1, 5)

            if eBullet > 20:
                eBullet = 10
            else:
                eBullet += 1
    

def CriaInstancias():
    global Personagens, nInstancias, enemy_shoot_intervals, enemy_last_shot_time

    i = 0
    ang = -90.0
    #Personagens.append(Instancia())
    Personagens[i].Posicao = Ponto (-2.5,0)
    Personagens[i].Escala = Ponto (1,1)
    Personagens[i].Rotacao = ang
    Personagens[i].IdDoModelo = 0
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = Ponto(6,2)
    Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
    Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
    Personagens[i].Velocidade = 0 # move-se a 5 m/s

    # Salva os dados iniciais do personagem i na area de backup
    Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i]) 

    i = 20

    while i < 20 + int(os.getenv('N_INIMIGOS')):
        i+=1
        Personagens[i].Posicao = GeraPosicaoAleatoria()
        Personagens[i].Escala = Ponto (1,1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = 2
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = Ponto(6,0)
        Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
        Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
        Personagens[i].Velocidade = 1 # move-se a 5 m/s 

        # Initialize shooting interval and last shot time
        enemy_shoot_intervals[i] = random.uniform(1, 5)  # Random interval between 1 and 5 seconds
        enemy_last_shot_time[i] = datetime.now()

        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])

    while i < 20 + (2*int(os.getenv('N_INIMIGOS'))):
        i+=1
        Personagens[i].Posicao = GeraPosicaoAleatoria()
        Personagens[i].Escala = Ponto (1,1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = 3
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = Ponto(4,0)
        Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
        Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
        Personagens[i].Velocidade = 1 # move-se a 5 m/s 

        # Initialize shooting interval and last shot time
        enemy_shoot_intervals[i] = random.uniform(1, 5)  # Random interval between 1 and 5 seconds
        enemy_last_shot_time[i] = datetime.now()

        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])

    while i < 20 + (3*int(os.getenv('N_INIMIGOS'))):
        i+=1
        Personagens[i].Posicao = GeraPosicaoAleatoria()
        Personagens[i].Escala = Ponto (1,1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = 4
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = Ponto(6,0)
        Personagens[i].Direcao = Ponto(0,1) # direcao do movimento para a cima
        Personagens[i].Direcao.rotacionaZ(ang) # direcao alterada para a direita
        Personagens[i].Velocidade = 1 # move-se a 5 m/s 

        # Initialize shooting interval and last shot time
        enemy_shoot_intervals[i] = random.uniform(1, 5)  # Random interval between 1 and 5 seconds
        enemy_last_shot_time[i] = datetime.now()

        Personagens[i+AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])

    nInstancias = i+1


    nInstancias = i+1

enemies_killed = 0

def drawText(position, textString):
    glRasterPos2f(position[0], position[1])
    for c in textString:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))


# ***********************************************************************************
def init():
    load_dotenv()
    global Min, Max
    global TempoInicial, LarguraDoUniverso
    
    # Define a cor do fundo da tela (AZUL)
    background_color_str = os.getenv('BACKGROUND_COLOR')
    background_color = tuple(map(float, background_color_str.split(',')))
    glClearColor(*background_color)
    
    clear() # limpa o console
    CarregaModelos()
    CriaInstancias()

    LarguraDoUniverso = int(os.getenv('TAMANHO_TELA'))

    Min = Ponto(-LarguraDoUniverso,-LarguraDoUniverso)
    Max = Ponto(LarguraDoUniverso,LarguraDoUniverso)

    TempoInicial = time.time()
    print("Inicio: ", datetime.now())
    print("TempoInicial", TempoInicial)

def animate():
    global angulo
    angulo = angulo + 1
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(800, 800)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("Exemplo de Criacao de Instancias")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
