from tkinter import *
from tkinter import ttk
import threading
import sys
from time import sleep
import RPi.GPIO as gpio
from tkinter import messagebox
from math import fabs


from web_part import *

# set values for GUI
root = Tk()
root.title("Crane")

# set pins
left_pin = 29
right_pin = 31
up_pin = 33
down_pin = 35
up_cargo_pin = 37
down_cargo_pin = 38
solenoid_pin = 40

# prepare GPIO board
gpio.setmode(gpio.BOARD)
# left move
gpio.setup(left_pin, gpio.OUT)
# right move
gpio.setup(right_pin, gpio.OUT)
# up
gpio.setup(up_pin, gpio.OUT)
# down
gpio.setup(down_pin, gpio.OUT)
# up cargo
gpio.setup(up_cargo_pin, gpio.OUT)
# down cargo
gpio.setup(down_cargo_pin, gpio.OUT)
# solenoid
gpio.setup(solenoid_pin, gpio.OUT)

# limitations and running parameters
# lr it's left_right
lr = 10
lr_min = 1
lr_max = 10

# ud it's up_down
ud = 7
ud_min = 1
ud_max = 7

# ud_c it's up_down_cargo
ud_c = 5
ud_c_min = 1
ud_c_max = 5

# It exists for check if cargo is under the jib
difference = fabs(ud - ud_c)


# control functions
def left():
    gpio.output(left_pin, 1)
    sleep(0.5)
    gpio.output(left_pin, 0)


def right():
    gpio.output(right_pin, 1)
    sleep(0.5)
    gpio.output(right_pin, 0)


def up():
    gpio.output(up_pin, 1)
    sleep(0.5)
    gpio.output(up_pin, 0)


def down():
    gpio.output(down_pin, 1)
    sleep(0.5)
    gpio.output(down_pin, 0)


def down_cargo():
    gpio.output(down_cargo_pin, 1)
    sleep(0.5)
    gpio.output(down_cargo_pin, 0)


def up_cargo():
    gpio.output(up_cargo_pin, 1)
    sleep(0.5)
    gpio.output(up_cargo_pin, 0)


def solenoid_on():
    gpio.output(solenoid_pin, 1)


def solenoid_off():
    gpio.output(solenoid_pin, 0)


def minimum_check(val, val_min, val_max):
    if val_min <= val < val_max:
        val += 1
        return True
    else:
        messagebox.showinfo("Crane ERROR", "Minimum is over!!!")
        return False


def maximum_check(val, val_min, val_max):
    if val_min < val <= val_max:
        val -= 1
        return True
    else:
        messagebox.showinfo("Crane ERROR", "Maximum is over!!!")
        return False


def do_left():
    global lr, lr_min, lr_max
    if minimum_check(lr, lr_min, lr_max):
        lr += 1
        left()


def do_right():
    global lr, lr_min, lr_max
    if maximum_check(lr, lr_min, lr_max):
        lr -= 1
        right()


def do_up():
    global ud, ud_min, ud_max
    if minimum_check(ud, ud_min, ud_max):
        if ud == ud_c + difference:
            do_down()
        ud += 1
        up()


def do_down():
    global ud, ud_min, ud_max
    if maximum_check(ud, ud_min, ud_max):
        if ud == ud_c + difference:
            do_down_cargo()
        ud -= 1
        down()


def do_up_cargo():
    global ud_c, ud_c_min, ud_c_max
    if maximum_check(ud_c, ud_c_min, ud_c_max):
        if ud == ud_c + difference:
            do_up()
        ud_c += 1
        down_cargo()


def do_down_cargo():
    global ud_c, ud_c_min, ud_c_max
    if maximum_check(ud_c, ud_c_min, ud_c_max):
        ud_c -= 1
        down_cargo()


def return_to_start_position():
    """
    Return to the start position
    """
    global lr, lr_min, ud, ud_max, ud_c, ud_max
    solenoid_off()
    while lr < lr_max:
        lr += 1
        left()
        sleep(0.5)
    sleep(0.5)
    while ud_c < ud_c_max:
        ud_c += 1
        up_cargo()
        sleep(0.2)
    while ud < ud_max:
        ud += 1
        up()
        sleep(0.2)


def config_buttons(state_of_button):
    """
    Method for enable and disable buttons
    """
    btn_left.config(state=state_of_button)
    btn_left.grid(row=0, column=0)

    btn_right.config(state=state_of_button)
    btn_right.grid(row=1, column=0)

    btn_up.config(state=state_of_button)
    btn_up.grid(row=0, column=1)

    btn_down.config(state=state_of_button)
    btn_down.grid(row=1, column=1)

    btn_up_cargo.config(state=state_of_button)
    btn_up_cargo.grid(row=0, column=2)

    btn_down_cargo.config(state=state_of_button)
    btn_down_cargo.grid(row=1, column=2)

    btn_solenoid_on.config(state=state_of_button)
    btn_solenoid_on.grid(row=0, column=3)

    btn_solenoid_off.config(state=state_of_button)
    btn_solenoid_off.grid(row=1, column=3)


def auto():
    """
    Automatic mode method
    """
    # disable buttons
    state_of_button = DISABLED
    config_buttons(state_of_button)
    
    commands = []
    file = open('auto.txt', 'r')
    for line in file:
        commands.append(line)
    file.close()

    i = 0
    # sleep_time = 0
    while i != len(commands):
        command = commands[i]
        str(command)
        if command == "left" or command == "left\n":
            do_left()
        elif command == "right" or command == "right\n":
            do_right()
        elif command == "up" or command == "up\n":
            do_up()
        elif command == "down" or command == "down\n":
            do_down()
        elif command == "up_cargo" or command == "up_cargo\n":
            do_up_cargo()
        elif command == "down_cargo" or command == "down_cargo\n":
            do_down_cargo()
        elif command == "s_on" or command == "s_on\n":
            solenoid_on()
        elif command == "s_off" or command == "s_off\n":
            solenoid_off()
        else:
            try:
                sleep_time = float(command)
                sleep(sleep_time)
            except ValueError:
                print("Check you file")
                break
        i += 1
        sleep(0.5)

    # enable buttons
    state_of_button = NORMAL
    config_buttons(state_of_button)


def on_closing():
    """
    Closing method
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        # model return to start position
        return_to_start_position()
        # cleanup pins for normal work after closing program
        gpio.cleanup()
        # close interface of managing model
        root.destroy()
        # stop video translation
        close_web()
        # close program window
        sys.exit()


def run_gui():
    """
    Run GUI
    """
    global btn_left, btn_right, btn_up, btn_down, btn_up_cargo, btn_down_cargo, btn_solenoid_on, btn_solenoid_off
    btn_left = ttk.Button(root, text='Left', command=do_left)
    btn_left.grid(row=0, column=0)
    btn_right = ttk.Button(root, text='Right', command=do_right)
    btn_right.grid(row=1, column=0)
    btn_up = ttk.Button(root, text='Up', command=do_up)
    btn_up.grid(row=0, column=1)
    btn_down = ttk.Button(root, text='Down', command=do_down)
    btn_down.grid(row=1, column=1)
    btn_up_cargo = ttk.Button(root, text='Up cargo', command=do_up_cargo)
    btn_up_cargo.grid(row=0, column=2)
    btn_down_cargo = ttk.Button(root, text='Down cargo', command=do_down_cargo)
    btn_down_cargo.grid(row=1, column=2)
    btn_solenoid_on = ttk.Button(root, text='Solenoid ON', command=solenoid_on)
    btn_solenoid_on.grid(row=0, column=3)
    btn_solenoid_off = ttk.Button(root, text='Solenoid OFF', command=solenoid_off)
    btn_solenoid_off.grid(row=1, column=3)
    btn_auto = ttk.Button(root, text='AUTO', command=auto)
    btn_auto.grid(row=0, column=4)
    btn_auto = ttk.Button(root, text='RETURN', command=return_to_start_position)
    btn_auto.grid(row=1, column=4)


# create a thread for video translation
vid_tr = threading.Thread(target=go_web)
vid_tr.start()

run_gui()

# create features for work with GUI
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
