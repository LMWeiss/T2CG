# ***********************************************************************************
#   OpenGLBasico3D-V5.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa exibe dois Cubos em OpenGL
#   Para maiores informações, consulte
# 
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Outro exemplo de código em Python, usando OpenGL3D pode ser obtido em
#   http://openglsamples.sourceforge.net/cube_py.html
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
# 
# ***********************************************************************************
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import Ponto
from Linha import Linha
from ListaDeCoresRGB import *
#from PIL import Image
import time
import random
import math

with open('mapa.txt') as mapa_file:
    mapa = [list(line.strip()) for line in mapa_file.readlines()]  # Read lines and remove newline characters

fox = Ponto(3, -1, 3)

enemyPos = []
movelPos = []

for line in range(len(mapa)):
    for i in range(len(mapa[0])):
        if mapa[line][i] == '0':
            mapa[line][i] = '1'
            fox = Ponto(line, -1, i)
        if mapa[line][i] == '5':
            movelPos.append((line, 1, i))
        if mapa[line][i] == '6':
            enemyPos.append((line, -1, i))


nEnergia = 10
walk = True
foxRotacao = 0.0;
foxVetorRotacao = 0.0
foxSpeed = 0.5
energia = 0
obs = Ponto(0,5,10)
neutro = Ponto(0,0,0)
vetorAlvo = neutro - obs

view = 0

class Enemy:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 1
        self.rotacao = 0
        self.vetorRotacao = 0
    def set_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
enemies = []
for p in enemyPos:
    enemies.append(Enemy(p[0], p[1], p[2]))

class Movel:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.rotacao = 0
        self.vetorRotacao = 0

moveis = []
for m in enemyPos:
    moveis.append(Movel(m[0], m[1], m[2]))

for i in range(nEnergia):
    randX = random.randint(0, len(mapa) - 1)
    randZ = random.randint(0, len(mapa[0]) - 1)

    if mapa[randX][randZ] == '1':
        mapa[randX][randZ] = '4'
    else:
        i-=1




Angulo = 0.0
# **********************************************************************
#  init()
#  Inicializa os parÃ¢metros globais de OpenGL
#/ **********************************************************************
def init():
    # Define a cor do fundo da tela (BRANCO) 
    glClearColor(0.68, 0.85, 0.90, 1.0)

    glClearDepth(1.0) 
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable (GL_CULL_FACE )
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #image = Image.open("Tex.png")
    #print ("X:", image.size[0])
    #print ("Y:", image.size[1])
    #image.show()


def UpdatePositions():
    global fox, foxRotacao, foxSpeed, walk, mapa, vetorAlvo, energia, enemies

    # Calculate the direction vector from each enemy towards the player
    player_pos = Ponto(fox.x, fox.y, fox.z)

    for enemy in enemies:
        posInimigo = Ponto(enemy.x, enemy.y, enemy.z)
        vetorX = fox.x - posInimigo.x;
        vetorZ = fox.z - posInimigo.z;
        anguloRad = math.atan2(vetorZ, vetorX);
        anguloGraus = anguloRad * 180.0 / math.pi;
        enemy.rotacao = -anguloGraus;
        enemy.vetorRotacao = -anguloGraus;
        rad = enemy.rotacao * math.pi / 180.0
        EproxX = enemy.x + math.cos(rad) * enemy.speed
        EproxZ = enemy.z - math.sin(rad) * enemy.speed
        enemy.set_position(EproxX, enemy.y, EproxZ)
        if round(posInimigo.x) == round(fox.x) and round(posInimigo.z) == round(fox.z):
            enemy.set_position(random.randint(0, len(mapa) - 1), -1, random.randint(0, len(mapa[0]) - 1))
            energia += 1
            if energia > 100:
               os._exit(0)

    
    rad = foxRotacao * math.pi / 180.0
    proxX = fox.x + math.cos(rad) * foxSpeed
    proxZ = fox.z + math.sin(rad) * foxSpeed

    mapaX = int(round(proxX))
    mapaZ = int(round(proxZ))

    if walk:
        if 0 <= mapaX < len(mapa) and 0 <= mapaZ < len(mapa[0]):
            if mapa[mapaX][mapaZ] != '2':
                if mapa[mapaX][mapaZ] == '4':
                    mapa[mapaX][mapaZ] = '1'
                    randX = random.randint(0, len(mapa) - 1)
                    randZ = random.randint(0, len(mapa[0]) - 1)
                    energia = 0
                    while mapa[randX][randZ] != '1':
                        randX = random.randint(0, len(mapa) - 1)
                        randZ = random.randint(0, len(mapa[0]) - 1)
                        if mapa[randX][randZ] == 1:
                            mapa[randX][randZ] = '4'
                fox.set(proxX, fox.y, proxZ)
                energia+=1

    vetorAlvo.set(math.cos(rad), 0, math.sin(rad))



def mLoader(filename):
    vertices = []
    faces = []

    try:
        with open(filename, 'r') as obj_file:
            for line in obj_file:
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith('f '):
                    face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                    faces.append(face)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

    return vertices, faces


def Desenhafox():
    global fox, foxVetorRotacao, energia

    # Example loading an OBJ model named 'Lowpoly_Fox.obj'
    obj_vertices, obj_faces = mLoader('Lowpoly_Fox.obj')

    if obj_vertices is None:
        return

    # Calculate color based on energy (transition from orange to black)
    # Example of linear interpolation (lerp) from orange to black
    initial_color = [1.0, 0.5, 0.0]  # Orange
    final_color = [0.0, 0.0, 0.0]    # Black
    lerp_factor = energia / 100.0    # Assuming energia ranges from 0 to 100

    # Interpolate color
    current_color = [
        initial_color[0] * (1 - lerp_factor) + final_color[0] * lerp_factor,
        initial_color[1] * (1 - lerp_factor) + final_color[1] * lerp_factor,
        initial_color[2] * (1 - lerp_factor) + final_color[2] * lerp_factor
    ]

    glPushMatrix()
    glTranslatef(fox.x, fox.y, fox.z)
    glRotatef(foxVetorRotacao + 90.0, 0.0, 1.0, 0.0)

    glScalef(0.009, 0.009, 0.009)

    # Disable lighting to ensure solid color rendering
    glDisable(GL_LIGHTING)

    # Apply calculated color
    glColor3f(current_color[0], current_color[1], current_color[2])

    # Render the player's body from the loaded OBJ model
    glBegin(GL_TRIANGLES)
    for face in obj_faces:
        for vertex_id in face:
            vertex = obj_vertices[vertex_id]
            glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()

    glPopMatrix()

    # Re-enable lighting if needed for other objects
    glEnable(GL_LIGHTING)

def DesenhaEnemies():
    global enemies, energia
    for enemie in enemies:
        # Example loading an OBJ model named 'Lowpoly_Fox.obj'
        obj_vertices, obj_faces = mLoader('Lowpoly_Fox.obj')

        if obj_vertices is None:
            return

        glPushMatrix()
        glTranslatef(enemie.x, enemie.y, enemie.z)
        glRotatef(enemie.vetorRotacao + 90.0, 0.0, 1.0, 0.0)

        glScalef(0.009, 0.009, 0.009)

        glDisable(GL_LIGHTING)

        SetColor(Black)

        # Render the player's body from the loaded OBJ model
        glBegin(GL_TRIANGLES)
        for face in obj_faces:
            for vertex_id in face:
                vertex = obj_vertices[vertex_id]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

        glPopMatrix()

        # Re-enable lighting if needed for other objects
        glEnable(GL_LIGHTING)

def DesenhaMoveis():
    global moveis
    for movel in moveis:
        # Example loading an OBJ model named 'Lowpoly_Fox.obj'
        obj_vertices, obj_faces = mLoader('lowpoly_tree.obj')

        if obj_vertices is None:
            return

        glPushMatrix()
        glTranslatef(movel.x, movel.y, movel.z)
        glRotatef(movel.vetorRotacao + 90.0, 0.0, 1.0, 0.0)

        glScalef(0.05, 0.05, 0.05)

        glDisable(GL_LIGHTING)

        SetColor(DarkGreen)
        glBegin(GL_TRIANGLES)
        for face in obj_faces:
            for vertex_id in face:
                vertex = obj_vertices[vertex_id]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

        glPopMatrix()

        # Re-enable lighting if needed for other objects
        glEnable(GL_LIGHTING)

# **********************************************************************
#  reshape( w: int, h: int )
#  trata o redimensionamento da janela OpenGL
#
# **********************************************************************
def reshape(w: int, h: int):
    global AspectRatio
	# Evita divisÃ£o por zero, no caso de uam janela com largura 0.
    if h == 0:
        h = 1
    # Ajusta a relacao entre largura e altura para evitar distorcao na imagem.
    # Veja funcao "PosicUser".
    AspectRatio = w / h
	# Reset the coordinate system before modifying
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Seta a viewport para ocupar toda a janela
    glViewport(0, 0, w, h)
    
    PosicUser()
# **********************************************************************
def DefineLuz():
    # Define cores para um objeto dourado
    LuzAmbiente = [0.4, 0.4, 0.4] 
    LuzDifusa   = [0.7, 0.7, 0.7]
    LuzEspecular = [0.9, 0.9, 0.9]
    PosicaoLuz0  = [2.0, 3.0, 0.0 ]  # PosiÃ§Ã£o da Luz
    Especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable ( GL_COLOR_MATERIAL )

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, LuzAmbiente)
    # Define os parametros da luz numero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, LuzAmbiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LuzDifusa  )
    glLightfv(GL_LIGHT0, GL_SPECULAR, LuzEspecular  )
    glLightfv(GL_LIGHT0, GL_POSITION, PosicaoLuz0 )
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT,GL_SPECULAR, Especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT,GL_SHININESS,51)



# **********************************************************************
# DesenhaCubos()
# Desenha o cenario
#
# **********************************************************************
def DesenhaCubo():
    glutSolidCube(1)
    
def PosicUser():

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60,AspectRatio,0.01,50) # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if view == 0:

        distancia = 3


        obsX = fox.x  - vetorAlvo.x * distancia
        obsY = fox.y + distancia
        obsZ = fox.z - vetorAlvo.z * distancia

        gluLookAt(obsX, obsY, obsZ,
                    fox.x, fox.y + 1.5, fox.z,
                    0.0, 1.0, 0.0)
    elif view == 1:

        gluLookAt(10, 40, 50,
                  10, 0, 50,
                  1, 0.0, 0)

    if view == 2:

                gluLookAt(fox.x, fox.y + 1, fox.z,
                  fox.x + vetorAlvo.x, fox.y + 1 + vetorAlvo.y, fox.z + vetorAlvo.z,
                  0.0, 1.0, 0.0)

# **********************************************************************
# void DesenhaLadrilho(int corBorda, int corDentro)
# Desenha uma cÃ©lula do piso.
# O ladrilho tem largula 1, centro no (0,0,0) e estÃ¡ sobre o plano XZ
# **********************************************************************
def DesenhaLadrilho(corBorda, corDentro):
    glColor3f(0,0,1) # desenha QUAD preenchido
    SetColor(corDentro)
    glBegin ( GL_QUADS )
    glNormal3f(0,1,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glVertex3f(-0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()

    
    glColor3f(1,1,1) # desenha a borda da QUAD 
    SetColor(corBorda)
    glBegin ( GL_LINE_STRIP )
    glNormal3f(0,1,0)
    glVertex3f(-0.5,  0.0, -0.5)
    glVertex3f(-0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0,  0.5)
    glVertex3f( 0.5,  0.0, -0.5)
    glEnd()
    
# **********************************************************************
def DesenharMapa():
    glEnable(GL_LIGHTING)
    global mapa
    
    glPushMatrix()
    glTranslated(0, -1, 0)
    for x in range(len(mapa)):
        glPushMatrix()
        for z in range(len(mapa[x])):
            if mapa[x][z] == '1' or mapa[x][z] == '5' or mapa[x][z] == '6':
                DesenhaLadrilho(Green, Green)
            elif mapa[x][z] == '2':
                alturaParede = 2.7
                glPushMatrix()
                glTranslatef(0, alturaParede / 2, 0)
                SetColor(Gray)
                gira = False

                if z-1 > 0 and z+1 < len(mapa[0]):
                    if mapa[x][z-1] == '2' or mapa[x][z-1] == '3':
                        gira = True

                if gira:
                    glRotatef(90, 0, 1, 0)
                
                glScalef(1, alturaParede, 0.25)
                glutSolidCube(1)

                glColor3f(0, 0, 0)
                glScalef(1, 1, 1)
                glutWireCube(1)
                
                glPopMatrix()
                DesenhaLadrilho(Black, Gray)
            elif mapa[x][z] == '3':
                alturaParede = 2.7
                alturaPorta = 2.1
                espessuraParede = 0.25
                larguraPorta = 1
                SetColor(DarkBrown)
                glPushMatrix()
                glTranslatef(x, 0 + alturaPorta / 2, z)
                glPopMatrix()
                glPushMatrix()
                glTranslatef(0, 0 + alturaPorta + (alturaParede - alturaPorta) / 2, 0)
                gira = False
                if mapa[x][z-1] == '3' or  mapa[x][z-1] == '2':
                    gira = True
                if gira:
                    glRotatef(90, 0, 1, 0)
                glScalef(1, alturaParede - alturaPorta, espessuraParede)
                glutSolidCube(1)
                glColor3f(0, 0, 0)
                glutWireCube(1)
                glPopMatrix()
                DesenhaLadrilho(Brown, DarkBrown)
            elif mapa[x][z] == '4':
                SetColor(Orange)
                altura = 0.75
                glPushMatrix()

                glTranslatef(0, altura / 2, 0)
                glScalef(altura, altura, altura)

                glutSolidCube(1)

                glColor3f(0, 0, 0)
                glScalef(1, 1, 1)
                glutWireCube(1)

                glPopMatrix();
                DesenhaLadrilho(Yellow, Yellow)
            
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()


    


# **********************************************************************
# display()
# Funcao que exibe os desenhos na tela
#
# **********************************************************************
def display():
    global Angulo, energia

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    DefineLuz()
    PosicUser()

    glMatrixMode(GL_MODELVIEW)
    
    # Draw the floor and other elements
    DesenharMapa() 
    Desenhafox()
    DesenhaEnemies()
    DesenhaMoveis()

    # Draw the energy bar
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 700, 500, 0)  
    glMatrixMode(GL_MODELVIEW)
    
    energy_bar_width = int(energia * 6) 

    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2i(10, 10)  
    glVertex2i(10 + energy_bar_width, 10) 
    glVertex2i(10 + energy_bar_width, 30)  
    glVertex2i(10, 30)       
    glEnd()

    glColor3f(1.0, 0.0, 0.0) 
    glBegin(GL_QUADS)
    glVertex2i(10, 10)       
    glVertex2i(10 + energy_bar_width, 10)  
    glVertex2i(10 + energy_bar_width, 30) 
    glVertex2i(10, 30)  
    glEnd()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Swap buffers to display the rendered image
    glutSwapBuffers()

    # Increment animation angle
    Angulo = Angulo + 1





last_time = time.time()
AccumDeltaT = 0.0
TempoTotal = 0.0
nFrames = 0
def animate():
    global last_time, AccumDeltaT, TempoTotal, nFrames

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    AccumDeltaT += dt
    TempoTotal += dt
    nFrames += 1

    if AccumDeltaT > 1.0 / 30:
        AccumDeltaT = 0
        UpdatePositions()
        glutPostRedisplay()

    

# **********************************************************************
#  keyboard ( key: int, x: int, y: int )
#
# **********************************************************************
def keyboard(key, x, y):
    global walk, view

    if key == b'\x1b':  # ASCII para ESC
        os._exit(0)
    elif key == b' ':
        walk = not walk
    elif key == b'f':
        if view < 2:
            view += 1
        else:
            view = 0
        glutPostRedisplay()
    else:
        pass

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************

def arrow_keys(a_keys, x, y):
    global foxRotacao, foxVetorRotacao
    if a_keys == GLUT_KEY_UP:
        pass
    if a_keys == GLUT_KEY_RIGHT:
        foxRotacao += 12.0
        foxVetorRotacao -= 12.0
        if foxRotacao >= 360.0:
            foxRotacao -= 360.0
    elif a_keys == GLUT_KEY_LEFT:
        foxRotacao -= 12.0
        foxVetorRotacao += 12.0
        if foxRotacao < 0.0:
            foxRotacao += 360.0
    if a_keys == GLUT_KEY_RIGHT:
        pass

    glutPostRedisplay()



def mouse(button: int, state: int, x: int, y: int):
    glutPostRedisplay()

def mouseMove(x: int, y: int):
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA|GLUT_DEPTH | GLUT_RGB)
glutInitWindowPosition(0, 0)

# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(1200, 500)
# Cria a janela na tela, definindo o nome da
# que aparecera na barra de tÃ­tulo da janela.
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("OpenGL 3D")

# executa algumas inicializaÃ§Ãµes
init ()
glutDisplayFunc(display)
glutIdleFunc (animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)


try:
    # inicia o tratamento dos eventos
    glutMainLoop()
except SystemExit:
    pass
