import RPi.GPIO as GPIO
import time
from lcd import Screen

class keypad():
    # CONSTANTS   
    KEYPAD = [
    [1,2,3,"A"],
    [4,5,6,"B"],
    [7,8,9,"C"],
    ["*",0,"#","D"]
    ]
    
    special_keys = { #dictionnary that holds tuple as key (main digit, amount pressed), value is the final digit displayed
    (1, 2): 'E',
    (1, 3): 'F',
    (2, 2): 'G',
    (2, 3): 'H',
    (3, 2): 'I',
    (3, 3): 'J',
    (4, 2): 'K',
    (4, 3): 'L',
    (5, 2): 'M',
    (5, 3): 'N',
    (6, 2): 'O',
    (6, 3): 'P',
    (7, 2): 'Q',
    (7, 3): 'R',
    (8, 2): 'S',
    (8, 3): 'T',
    (9, 2): 'U',
    (9, 3): 'V',
    ('*', 2): 'W',
    ('*', 3): 'X',
    (0, 2): 'Y',
    (0, 3): 'Z',
    ('A',2):'Del'
    }

    
    ROW         = [11,36,13,15]
    COLUMN      = [16,18,22,7]
    
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
    
    def getKey(self):
        
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
        
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
                
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return
        
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal < 0 or colVal > 3:
            self.exit()
            return

        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
        
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    """
    Prompts the user to enter a nickname using a keypad with multi-press detection (like on old mobile phones).

    The function captures key presses, allowing for repeated presses of the same key to cycle through
    different characters (e.g., pressing '2' multiple times to get 'D', 'E'). It uses a timeout
    window (2 secs) to determine when the user has finished pressing a key. The nickname entry
    ends when the '#' key is pressed. The user can delete the last entered character by pressing a key 
    mapped to 'Del'.

    Parameters:
        screen (object): the lcd display with display_data(line1, line2) method

    Returns:
        str: The completed nickname as a string, assembled from the interpreted key presses.
    """
    def enter_your_nickname(self, screen):
        timeout = 2 #period of time you can repress a button 
        nickname = []
        digit = None
        while (digit != "#"):
            count = 1
            digit1 = None
            while digit1 == None:
                digit1 = self.getKey() #get key while nothing has been pressed
            screen.display_data(f"First press: {digit1}","")
            last_time = time.time()
            while(time.time()-last_time<timeout): #while less than 2 seconds have elapsed
                time.sleep(0.2)
                digit2 = self.getKey() #get key 
                if  digit2==digit1: #if its same key being repressed
                    count = count +1 #increase count 
                    screen.display_data("Pressed again!", "Count = "+ str(count)) 
                    last_time = time.time() #update time
            if count >= 2:
                digit = self.special_keys.get((digit1, count)) #get the digit from the dictionnary 
                if digit is None:
                    digit = digit1  #fallback if no special mapping
            else:
                digit = digit1 #if count is one then digit is just the fist digit pressed 
            screen.display_data("Final detected: ", str(digit)) #display final digit 
            time.sleep(0.5)  # Small delay before next loop
            if digit != "#" and digit!= 'Del':
                nickname.append(str(digit))  #convert to string and append to nickname 
            elif digit == 'Del' and nickname:
                nickname.pop() #allow to delete last entered character
        return ''.join(nickname) 
    
    def enter_mode(self,screen): #get mode from player 
        digit = None
        while digit == None:
            digit = self.getKey()    
        if digit ==1 or digit==2: #only 1,2,3 allowed as legit modes
            return digit
        else:
            screen.display_data("Not a valid mode")
