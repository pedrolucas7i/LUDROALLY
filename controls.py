import RPi.GPIO as GPIO
import subprocess
import time

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

# Set the mode of pin numbering
GPIO.setmode(GPIO.BCM)

# Configure rows as output and columns as input with pull-down resistors
for row in ROW_PINS:
    GPIO.setup(row, GPIO.OUT, initial=GPIO.LOW)

for col in COL_PINS:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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

# Function to scan the matrix and identify which button was pressed
def scan_matrix():
    for row_index, row_pin in enumerate(ROW_PINS):
        GPIO.output(row_pin, GPIO.HIGH)  # Activate the current row

        # Check the state of each column
        if GPIO.input(COL_PINS[0]) == 1:  # Column 0 pressed
            GPIO.output(row_pin, GPIO.LOW)      # Deactivate the row before returning
            return (row_index, 0)  # Return the row and column of the pressed button

        if GPIO.input(COL_PINS[1]) == 1:  # Column 1 pressed
            GPIO.output(row_pin, GPIO.LOW)      # Deactivate the row before returning
            return (row_index, 1)  # Return the row and column of the pressed button

        if GPIO.input(COL_PINS[2]) == 1:  # Column 2 pressed
            GPIO.output(row_pin, GPIO.LOW)      # Deactivate the row before returning
            return (row_index, 2)  # Return the row and column of the pressed button

        GPIO.output(row_pin, GPIO.LOW)  # Deactivate the row after checking

    return None  # No button was pressed

# Movement and speed settings
acceleration = 5
max_speed = 20
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
                press_key('XF86AudioRaiseVolume')
            elif action == 'VOL_DOWN':
                press_key('XF86AudioLowerVolume')
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

        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()
