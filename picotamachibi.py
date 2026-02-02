# from icons import food_icon
from machine import Pin, PWM
from gui.pico_lcd_1_14 import LCD_1inch14, BL
from gui.animate import Animate
from gui.icon_icon import Icon
from gui.toolbar import Toolbar
from gui.button import Button
from gui.event import Event
from gui.game_state import GameState
from time import sleep, ticks_ms, ticks_diff
import framebuf
from random import randint

# Pico-LCD-1.14 default pinout (SPI1 on GPIO 9-13)
pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)

lcd = LCD_1inch14()
oled = lcd
print(f"display: {oled}")

# load icons
food = Icon('food.pbm', width=32, height=32, name="food", scale=2)
lightbulb = Icon('lightbulb.pbm', width=32, height=32, name="lightbulb", scale=2)
game = Icon('game.pbm', width=32, height=32, name="game", scale=2)
firstaid = Icon('firstaid.pbm', width=32, height=32, name="firstaid", scale=2)
toilet = Icon('toilet.pbm', width=32, height=32, name="toilet", scale=2)
heart = Icon('heart.pbm', width=32, height=32, name="heart", scale=2)
call = Icon('call.pbm', width=32, height=32, name="call", scale=2)

# Game Variables
TIREDNESS = 5 # seconds
POOP_MIN = 5 # seconds
POOP_MAX = 100 # seconds
SLEEP_DURATION = 5 # seconds
SCREEN_W = 240
DEATH_W = 32
DEATH_SPEED = 2

# Set Animations
poopy =    Animate(x=208, y=103, width=32, height=32, filename='poop', scale=2)
baby =     Animate(x=72, y=35, width=96, height=96, animation_type="bounce", filename='baby_bounce', scale=2)
eat =      Animate(x=72, y=35, width=96, height=96, filename='eat', scale=2)
babyzzz =  Animate(x=72, y=35, width=96, height=96, animation_type="loop", filename='baby_zzz', scale=2)
death =    Animate(x=72, y=35, animation_type='bounce', filename="skull", scale=2)
go_potty = Animate(filename="potty", animation_type='bounce',x=72,y=35, width=96, height=96, scale=2)

death_x = death.x
death_dx = DEATH_SPEED

# Set the game state
gamestate = GameState()

# Append states to the states dictionary
gamestate.reset()


def tired():
    gamestate.states["sleepiness"] -= 1
    if gamestate.states["sleepiness"] < 0:
        gamestate.states["sleepiness"] = 0
    tiredness.start(TIREDNESS * 1000)
    
def wakeup():
    gamestate.states["sleepiness"] = 10
    gamestate.states["sleeping"] = False
    gamestate.states["happiness"] += 1
    gamestate.states["health"] += 1
    babyzzz.set = False
    baby.set = True
    print("Waking up")
    
def poop_check():
    if not gamestate.states["sleeping"]:
        go_potty.loop(no=1)
        baby.set = False
        go_potty.set = True
        print("poop time")
    
def clear():
    """ Clear the screen """
    oled.fill_rect(0, 0, 240, 135, 0)

def build_toolbar():
    print("building toolbar")
    toolbar = Toolbar()
    toolbar.spacer = 2
    toolbar.additem(food)    
    toolbar.additem(lightbulb)
    toolbar.additem(game)
    toolbar.additem(firstaid)
    toolbar.additem(toilet)
    toolbar.additem(heart)
    toolbar.additem(call)
    return toolbar

def do_toolbar_stuff():
    if tb.selected_item == "food":
        gamestate.states["feeding_time"] = True
        gamestate.states["sleeping"] = False
        baby.set = False
        babyzzz.set = False
        eat.set = True
            
    if tb.selected_item == "game":
        print("game")
        playtime.message = "He Hee"
        playtime.popup(oled)
        clear()
        gamestate.states["happiness"] += 10
    if tb.selected_item == "toilet":
        toilet.message = "Cleaning..."
        toilet.popup(oled)
        poopy.set = False
        baby.set = True
        clear()
        baby.animate(oled)
        poop_event.start(randint(POOP_MIN * 1000, POOP_MAX * 1000))
    if tb.selected_item == "lightbulb":
        # Sleeping
        if not gamestate.states["sleeping"]:
            gamestate.states["sleeping"] = True
            baby.set = False
            babyzzz.set = True
#             babyzzz.load()
            sleep_time.message = "Night Night"
            sleep_time.popup(oled)
            clear()
            sleep_time.start(SLEEP_DURATION * 1000) # sleep for 1 second

            # need to add an event that increases energy level after sleeping for 1 minute
        else:
            gamestate.states["sleeping"] = False
            babyzzz.set = False
            baby.set = True
            sleep_time.message = "Morning"
            sleep_time.popup(oled)
            clear()
        print("lightbulb")
    if tb.selected_item == "firstaid":
        firstaid.message = "Vitamins"
        firstaid.popup(oled)
        gamestate.states["health"] += 1
        clear()
    if tb.selected_item == "heart":
        print("heart")
        gamestate.states["happiness"] += 10

    if tb.selected_item == "call":
        print("Tamagotchi status:", gamestate)

def unhealthy_environment():
    gamestate.states["health"] -= 1
    gamestate.states["happiness"] -= 1
    print("Unhealthy Environment")
    if gamestate.states["health"] <= 0:
        gamestate.states["health"] = 0
        death.set = True
    if gamestate.states["happiness"] < 0:
        gamestate.states["happiness"] = 0
    gamestate.states["unwell"] = False 

def update_gamestate():
    # Avoid per-frame logging to keep input responsive.
    if gamestate.states["health"] == 0:
        global death_x, death_dx
        death.set = True
        baby.set = False
        babyzzz.set = False
        poopy.set = False
        go_potty.set = False
        eat.set = False
        death.x = death_x
        death_x += death_dx
        if death_x <= 0 or death_x >= (SCREEN_W - DEATH_W):
            death_dx = -death_dx
            if death_x < 0:
                death_x = 0
            elif death_x > (SCREEN_W - DEATH_W):
                death_x = SCREEN_W - DEATH_W
        death.animate(oled)
        oled.text("GAME OVER", 80, 10, 0xFFFF)
        return
    if gamestate.states["feeding_time"]:
        babyzzz.set = False
        baby.set = False
        eat.set = True
        eat.animate(oled)
        if not eat.done:
            eat.animate(oled)
        if gamestate.states["feeding_time"] and eat.done:
            gamestate.states["feeding_time"] = False
            energy_increase.message = "ENERGY + 1"
            energy_increase.popup(oled)
            gamestate.states["health"] += 10
            gamestate.states["happiness"] += 2
            
            clear()
#             eat.unload()
            eat.set = False
            baby.set = True
        
    if gamestate.states["sleeping"]:
#             babyzzz.load()
        babyzzz.set = True
        babyzzz.animate(oled)
            
    if go_potty.set:
#         baby.set = False
        go_potty.animate(oled)

    if go_potty.done:
        go_potty.set = False
        poopy.set = True
        baby.set = True
        
    if baby.set:
        baby.animate(oled)

    if poopy.set:
        poopy.animate(oled)
        # Check for the poop and if there is poop, decrease the health every 5 seconds
        if not gamestate.states["unwell"]:
            gamestate.states["unwell"] = True    
            decrease_health.start(5000)
        
    if death.set:
        death.animate(oled)
    
    if gamestate.states["health"] >= 1:
        death.set = False
    
    if not gamestate.states["tired"]:
        gamestate.states["tired"] = True
        tiredness.start(5000)
    if gamestate.states["sleepiness"] == 0:
        if not go_potty.set:
            baby.set = False
            babyzzz.set = True
            babyzzz.animate(oled)
tb = build_toolbar()

# Setup buttons (Pico-LCD-1.14 key binding)
# keyA=15, keyB=17, key2=2(up), key3=3(center), key4=16(left), key5=18(down), key6=20(right)
button_a = Button(15, active_low=True)
button_b = Button(17, active_low=True)
button_up = Button(2, active_low=True)
button_center = Button(3, active_low=True)
button_left = Button(16, active_low=True)
button_down = Button(18, active_low=True)
button_right = Button(20, active_low=True)

# Set toolbar index
index = 0
TOOLBAR_ITEMS = 7

# Set the toolbar
tb.select(index, oled)

# Set up Events
energy_increase = Event(name="Increase Energy", sprite=heart, value=1)
firstaid = Event(name="First Aid", sprite=firstaid, value=0)
toilet = Event(name="Toilet", sprite=toilet, value=0)
poop_event = Event(name="poop time", sprite=toilet, callback=poop_check)
poop_event.start(randint(POOP_MIN * 1000, POOP_MAX * 1000))
sleep_time = Event(name="sleep time", sprite=lightbulb, value=1, callback=wakeup)
decrease_health = Event(name="decrease health", callback=unhealthy_environment)
tiredness = Event(name="tiredness", callback=tired)
playtime = Event(name="Game", sprite=game)
# poop_event.timer = 3
# poop_event.timer_ms = 1

baby.loop(no=-1)
poopy.bounce()
death.loop(no=-1)
death.speed='very slow'
babyzzz.speed = 'normal'
babyzzz.loop(no=-1)
# go_potty.loop(no=1)
# go_potty.set = True
poopy.set = False
# go_potty.load() # duplicate if go_potty.set is True

# death.set = True
baby.set = True

# Main Game Loop
last_a = False
last_b = False
last_center = False
last_left = False
last_right = False
last_nav_time = 0
NAV_REPEAT_MS = 80
last_render_time = 0
RENDER_MS = 50
while True:
    key = ' '
#     baby.animate(oled)

    center_now = button_center.is_pressed

    if gamestate.states["health"] == 0:
        clear()
        if center_now and not last_center:
            gamestate.reset()
            death.set = False
            death_x = 72
            death_dx = DEATH_SPEED
            death.x = death_x
            baby.set = True
            babyzzz.set = False
            poopy.set = False
            go_potty.set = False
            eat.set = False
            index = 0
            tb.select(index, oled)
            tb.show(oled)
            poop_event.start(randint(POOP_MIN * 1000, POOP_MAX * 1000))
        update_gamestate()
        oled.show()
        last_center = center_now
        sleep(0.02)
        continue

    if not gamestate.states["cancel"]:
        tb.unselect(index, oled)
        
    a_now = button_a.is_pressed
    b_now = button_b.is_pressed
    center_now = button_center.is_pressed
    left_now = button_left.is_pressed
    right_now = button_right.is_pressed

    now = ticks_ms()
    right_repeat = right_now and (not last_right or ticks_diff(now, last_nav_time) >= NAV_REPEAT_MS)
    left_repeat = left_now and (not last_left or ticks_diff(now, last_nav_time) >= NAV_REPEAT_MS)

    if right_repeat:
        if index < 0:
            index = 0
        else:
            index += 1
            if index >= TOOLBAR_ITEMS:
                index = 0
        gamestate.states["cancel"] = False
        last_nav_time = now

    if left_repeat:
        if index < 0:
            index = TOOLBAR_ITEMS - 1
        else:
            index -= 1
            if index < 0:
                index = TOOLBAR_ITEMS - 1
        gamestate.states["cancel"] = False
        last_nav_time = now
        
    if center_now and not last_center:
        gamestate.states["cancel"] = True
        index = -1
    
    if not gamestate.states["cancel"]:
        tb.select(index, oled)

    if b_now and not last_b:
        do_toolbar_stuff()

    last_a = a_now
    last_b = b_now
    last_center = center_now
    last_left = left_now
    last_right = right_now
    
    now = ticks_ms()
    if ticks_diff(now, last_render_time) >= RENDER_MS:
        tb.show(oled)
        update_gamestate()
        oled.show()
        last_render_time = now
    sleep(0.01)
    