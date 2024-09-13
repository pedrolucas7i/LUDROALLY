import gpiozero
import subprocess
import time
import os

env = os.environ.copy()
env['PULSE_SERVER'] = 'unix:/run/user/1000/pulse/native'.format(uid=os.getuid())

# Definition of GPIO pins for rows and columns of the button matrix (4x3)
ROW_PINS = [20, 5, 6, 19]   # Columns (physical), now are rows (logical)
COL_PINS = [26, 21, 16]  # Rows (physical), now are columns (logical)

# Mapping functions to each row and column combination
BUTTON_FUNCTIONS = {
    (0, 2): 'SUPER',
    (0, 1): 'LEFT',
    (1, 2): 'UP',
    (0, 0): 'DOWN',
    (1, 1): 'RIGHT',
    (1, 0): 'VOL_DOWN',
    (2, 0): 'VOL_UP',
    (2, 1): 'RIGHT_CLICK',
    (3, 0): 'LEFT_CLICK',
    (2, 2): 'COPY',
    (3, 1): 'PASTE',
    (3, 2): 'TAB'
}

# Initialize row pins as output and column pins as input
row_outputs = [gpiozero.OutputDevice(pin, active_high=True, initial_value=False) for pin in ROW_PINS]
col_inputs = [gpiozero.Button(pin, pull_up=False) for pin in COL_PINS]

# Function to move the mouse cursor
def move_mouse(x, y):
    try:
        subprocess.run(["xdotool", "mousemove_relative", "--", str(x), str(y)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error moving mouse: {e}")

# Function to click with the mouse
def click_mouse(button=1):
    try:
        subprocess.run(["xdotool", "click", str(button)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error clicking mouse: {e}")

# Function to press a key
def press_key(key):
    try:
        subprocess.run(["xdotool", "key", key], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error pressing key {key}: {e}")

def run(command):
    try:
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error runnning command {command}: {e}")

def vol_up():
    try:
        subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '5%+'], env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def vol_down():
    try:
        subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '5%-'], env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Function to scan the matrix and identify which button was pressed
def scan_matrix():
    for row_index, row in enumerate(row_outputs):
        row.on()  # Activate the current row

        for col_index, col in enumerate(col_inputs):
            if col.is_pressed:  # Column pressed
                row.off()  # Deactivate the row before returning
                return (row_index, col_index)

        row.off()  # Deactivate the row after checking

    return None  # No button was pressed

# Movement and speed settings
acceleration = 7
max_speed = 40
x_speed = 0
y_speed = 0

try:
    while True:
        pressed_button = scan_matrix()

        if pressed_button:
            #print(f"Button pressed: {pressed_button}")  # Debug: Print the coordinate of the button
            action = BUTTON_FUNCTIONS.get(pressed_button)
            #print(f"Action executed: {action}")  # Debug: Print the associated action

            if action == 'LEFT':
                x_speed = -acceleration
            elif action == 'RIGHT':
                x_speed = acceleration
            elif action == 'UP':
                y_speed = -acceleration
            elif action == 'DOWN':
                y_speed = acceleration
            elif action == 'LEFT_CLICK':
                click_mouse(button=1)
            elif action == 'RIGHT_CLICK':
                click_mouse(button=3)
            elif action == 'SUPER':
                press_key('Super_L')
            elif action == 'VOL_UP':
                vol_up()
            elif action == 'VOL_DOWN':
                vol_down()
            elif action == 'COPY':
                press_key('ctrl+shift+c')
            elif action == 'PASTE':
                press_key('ctrl+shift+v')
            elif action == 'TAB':
                press_key('Tab')

        else:
            x_speed = 0
            y_speed = 0

        x_speed = max(min(x_speed, max_speed), -max_speed)
        y_speed = max(min(y_speed, max_speed), -max_speed)

        if x_speed != 0 or y_speed != 0:
            move_mouse(x_speed, y_speed)

        time.sleep(0.1)

except KeyboardInterrupt:
    for row in row_outputs:
        row.off()  # Ensure all rows are off