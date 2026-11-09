import RPi.GPIO as GPIO
from keypad import keypad
import time
from lcd import Screen

trigpin = 31 
echopin = 29
servopin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(trigpin,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(echopin,GPIO.IN)
GPIO.setup(servopin, GPIO.OUT)
p_servo = GPIO.PWM(servopin,50)
p_servo.start(0)
time.sleep(2)

mode = 0 
score = 0
started = False

def check_dist(): #returns distance using the ultrasonic sensor
	GPIO.output(trigpin, GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(trigpin, GPIO.LOW)
	while not GPIO.input(echopin):
		pass
	t1 = time.time()
	while GPIO.input(echopin):
		pass
	t2 = time.time()
	return (t2-t1)*340/2

def update_score(): #updates global variable score if distance detected is less than 0.07(diameter of the hoop)
    global score
    if check_dist()<=0.07:
        score = score +1
        print(score)
        time.sleep(0.5) #add delay not to count the same shot many times 
    
def move_hoop():  #sweeping hoop while also updating score 
    while(mode==2):
        for i in range(25, 51):
            p_servo.ChangeDutyCycle(2.5 + 10 * i / 180) 
            update_score()
            time.sleep(0.01) #for no observed delay

        for i in range(50, 24, -1):  #sweeping back 
            p_servo.ChangeDutyCycle(2.5 + 10 * i / 180)
            update_score()
            time.sleep(0.01)
        return
    
def destroy(): #cleanup 
    p_servo.stop()
    screen.display_data("", "")
    time.sleep(0.3)
    GPIO.cleanup()

"""
Main game loop for FlipShot.

- Initializes the screen and keypad.
- Displays a flashing welcome message and prompts the player to enter their name.
- Asks the player to select a game mode (1 = Easy, 2 = Medium).
- Runs a 60-second game session:
    - Displays countdown and live score.
    - Calls update_score() or move_hoop() based on selected mode.
- After the game ends:
    - Displays final score.
    - Appends player name, mode, and score to 'leaderboard.csv'.
    - Resets game state for the next player.
"""

if __name__ == "__main__": 
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2) 
    welcome_line1 = "Hi! Welcome"
    welcome_line2 = "to FlipShot" #initialiZing welcome phrase 
    screen.enable_backlight()
    kp = keypad()
    try: 
        while True:
            if started==False:
                for i in range(3):
                    screen.display_data(welcome_line1, welcome_line2) 
                    time.sleep(0.5)  
                    screen.display_data("", "")
                    time.sleep(0.3) #flashing welcome phrase
                screen.display_data("Enter your name","to play!") 
                time.sleep(0.5)
                player_name = kp.enter_your_nickname(screen)
                screen.display_data("Thank you", player_name+"!")
                time.sleep(2)
                screen.display_data("Now enter", "preferred mode!")
                time.sleep(2) #delay for the player to read
                screen.display_data("1 for Easy", "2 for Medium")
                mode = kp.enter_mode(screen)
                screen.display_data("You are in mode", str(mode)+"!")
                time.sleep(2)
                screen.display_data("Ready?","")
                time.sleep(2)  
                screen.display_data("", "")
                time.sleep(0.3)
                screen.display_data("Set")
                time.sleep(2)  
                screen.display_data("", "")
                time.sleep(0.3)
                screen.display_data("Go!")
                time.sleep(0.8)  
                screen.display_data("", "")
                started = True #start the game
                start_time = time.time() #start counting
            else:
                last_updated_time = 0  #keep track of last time time was updated(update every 1 second)
                elapsed_time = 0 #keep track of elapsed time
                while elapsed_time < 60: #game is 60 seconds long
                    current_time = time.time() #update current time
                    elapsed_time = current_time - start_time #update elapsed time
                    if time.time() - last_updated_time >= 1: #if 1 second was passed, update time left displayed
                        screen.display_data("Time Left: " + str(60-round(elapsed_time)), "Score: " + str(score))
                        last_updated_time = time.time()
                    if (mode==1):
                        update_score()
                        time.sleep(0.01)
                    else:
                        move_hoop()   
                p_servo.start(0) #make servo rest after done moving hoop 
                time.sleep(1)
                screen.display_data("GAME OVER!" , "") #finish game
                time.sleep(2)  
                screen.display_data("Final score: ", str(score)) #display final score
                time.sleep(2)  
                with open('leaderboard.csv', 'a') as file:
                    file.write(f"{player_name},{mode},{score}\n") #update leaderboard each time a player plays
                started = False #reset global values score and mode, and make game stop
                mode = 0 
                score = 0

    except KeyboardInterrupt:
        destroy()
        