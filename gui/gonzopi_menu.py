import pydispmanx, time, pygame
import os

os.environ["DISPLAY"] = ":0" 
pygame.display.init()
pygame.font.init()

print(pydispmanx.getDisplays())
display_size=pydispmanx.getDisplaySize()
print(display_size)
print(str(round(pydispmanx.getFrameRate(),2))+"Hz")
print(pydispmanx.getPixelAspectRatio())

display_width=display_size[0]
display_height=display_size[1]

print("display width:"+str(display_width))
print("display height:"+str(display_height))

menulayer = pydispmanx.dispmanxLayer(10);
vumenulayer = pydispmanx.dispmanxLayer(11);
print("Layer successfully created")
pygame_surface = pygame.image.frombuffer(menulayer, menulayer.size, 'RGBA')
pygame_surface2 = pygame.image.frombuffer(vumenulayer, vumenulayer.size, 'RGBA')
pygame_surface.set_alpha(150) 
pygame_surface2.set_alpha(150) 
WHITE = (255, 255, 255)
WHITEOPAC = (255, 255, 0)
OPAC = (255, 255, 255, 0)
BLACK = (0, 0, 0, 120)
YELLOW = (0, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (255, 255, 0)
bakg=BLACK
linenr = 0;
selected = 0 
showmenu = 0
header = 0
menuadd = 1
y_offset2 = 0
y_offset3 = 21
y_offset4 = 42
y_offset5 = 421
y_offset6 = 442
y_offset = 466
text_size = 15
text_size_selected = 16
space = 10
morespace = 12
rectime = 700
color = 3
row1 = 0
row2 = 0
row3 = 0
row4 = 0
row5 = 0
moverow = 0
oldmenu=""
oldvumeter=""
hidemenu=False
#font='VTV323'
#font='VeraMono'
#font='fixedsys'
font='firacode'

if display_width == 1920:
    y_offset2 = 5
    y_offset3 = 45
    y_offset4 = 85
    y_offset5 = 960
    y_offset6 = 1000
    y_offset = 1040
    rectime = 1600
    text_size = 30
    text_size_selected = 32
    space = 23
    morespace = 27    
if display_width == 800:
    y_offset2 = 0
    y_offset3 = 15
    y_offset4 = 30
    y_offset5 = 435
    y_offset6 = 450
    y_offset = 465
    rectime = 700
    if font == 'VeraMono':
        text_size = 15
        text_size_selected = 11
        space = 10
        morespace = 5
    if font == 'VTV323':
        text_size = 19
        text_size_selected = 15
        space = 9
        morespace = 5
    else:
        text_size = 15
        text_size_selected = 11
        space = 10
        morespace = 5
    moverow = 0

fontObj = pygame.font.Font("/home/pi/gonzopi/gui/"+font+'.ttf', text_size,bold=True)

def render_menu(text, size, row, y_offset, color, bakg):
    t = fontObj.render(text, True, color)
    rect = t.get_rect().move(row,y_offset).inflate(0,-4)
    #print(rect)
    pygame.draw.rect(pygame_surface, bakg, rect)
    #pygame_surface.set_alpha(55)
    pygame_surface.blit(t, (row, y_offset))

def render_vumenu(text, size, row, y_offset, color, bakg):
    t = fontObj.render(text, True, color)
    #rect = t.get_rect()
    #pygame.draw.rect(pygame_surface, BLUE, rect)
    #pygame_surface2.set_alpha(55)
    pygame_surface2.blit(t, (row, y_offset))

while True:
    try:
        with open('/dev/shm/interface', 'r') as f:
            if f:
                menu = [line.rstrip() for line in f]
        with open('/dev/shm/vumeter', 'r') as f:
            if f:
                vumeter = f.read()
    except:
        menu=''
        vumeter=''
    if vumeter != oldvumeter: 
        pygame_surface2.fill((0,0,0,0))
        try:
            s_vol1 = vumeter[85]
            s_vol2 = vumeter[86]
            vol=s_vol1+s_vol2
            vol = int(vol)
            if vol >= 0 and vol < 35:
                color = WHITE
            if vol >= 35 and vol < 99:
                color = GREEN
            if vol >= 99:
                color = RED
        except:
            color=WHITE
        bakg=BLACK
        render_vumenu(vumeter, text_size, 0, y_offset, color, bakg)
        oldvumeter = vumeter
        vumenulayer.updateLayer()
    if menu != oldmenu and len(str(menu)) > 3:
        pygame_surface.fill((0,0,0,0))
        #print(menu)
        #text1 = fontObj.render(menu[3], True, WHITE, BLUE)
        #text2 = fontObj.render(menu[4], True, WHITE, BLUE)
        #text3 = fontObj.render(menu[5], True, WHITE, BLUE)
        #text4 = fontObj.render(menu[6], True, WHITE, BLUE)
        #text5 = fontObj.render(menu[7], True, WHITE, BLUE)
        #rect = text1.get_rect()
        #pygame.draw.rect(pygame_surface, BLUE, rect)

        linenr=0
        color = WHITE
        row1 = 0
        row2 = 0
        row3 = 0
        row4 = 0
        row5 = 0

        for i in menu:
            #print(i)
            read = len(i)
            if linenr == 0:
                try:
                    selected = int(i.strip())
                except:
                    selected = 0
            if linenr == 1:
                try:
                    showmenu = int(i.strip())
                except:
                    showmenu = 1
            if linenr == selected + 2 + menuadd:
                color = BLACK ##selected color
                bakg = WHITEOPAC
                hidemenu=False
            else:
                if showmenu == 1:
                    color = WHITE ##unselected;
                    bakg=BLACK
                    hidemenu=False
                if showmenu == 2:
                    color = BLUE
                    bakg=BLACK
                if showmenu == 0:
                    color = OPAC
                    bakg=OPAC
                    hidemenu=True
            if linenr == 2 and i == '':
                header = 0
            if linenr == 2 and i != '':
                header = 1
            if selected == 420:
                if linenr == 1:
                    render_menu(i, text_size, moverow, y_offset2, WHITE, bakg)
                if linenr > 1:
                    text1 = fontObj.render(i, True, WHITE, BLUE)
                    render_menu(i, text_size, row1, y_offset3, WHITE, bakg)
                    row1 += read * space + morespace
            if header == 0 and selected < 420:
                if linenr == 7+menuadd and i != '': ##show recording time if there is any
                    #render_subtitle(img, line, text_size, text_size_selected, rectime, y_offset2, 3);
                    color = RED
                    render_menu(i, text_size, rectime, y_offset2, color, bakg)
                if linenr >= 2+menuadd and linenr <= 6+menuadd:
                    render_menu(i, text_size, row1, y_offset2, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row1, y_offset2, color);
                    row1 += read * space + morespace
                    #print(str(row1))
                if linenr >= 8+menuadd and linenr <= 13+menuadd:
                    if hidemenu == False:
                        render_menu(i, text_size, row2, y_offset3, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row2, y_offset3, color);
                    row2 += read * space + morespace
                    #print(str(row2))
                if linenr >= 14+menuadd and linenr <= 20+menuadd:
                    if hidemenu == False:
                        render_menu(i, text_size, row3, y_offset4, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row3, y_offset4, color);
                    row3 += read * space + morespace
                    #print(str(row3))
                if linenr >= 21+menuadd and linenr <= 29+menuadd:
                    if hidemenu == False:
                        render_menu(i, text_size, row4, y_offset5, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row4, y_offset5, color);
                    row4 += read * space + morespace
                if linenr >= 30+menuadd and linenr <= 41+menuadd:
                    if hidemenu == False:
                        render_menu(i, text_size, row5, y_offset6, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row5, y_offset6, color);
                    row5 += read * space + morespace;
            if header == 1:
                if linenr == 1+menuadd:
                    render_menu(i, text_size, 0, y_offset2, color, bakg)
                    #render_subtitl(img, line, text_size, text_size_selected, moverow, y_offset2, 5);
                if linenr > 1+menuadd:
                    render_menu(i, text_size, row1, y_offset3, color, bakg)
                    #render_subtitle(img, line, text_size, text_size_selected, row1, y_offset3, color);
                    row1 += read * space + morespace;
            linenr+=1

        #render_subtitle(img, vumeter, text_size, text_size_selected , moverow, y_offset, vucolor);
        menulayer.updateLayer()
        oldmenu = menu
    time.sleep(0.05)
