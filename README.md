# 🟠 FlipShot

**A Raspberry Pi adaptation of the basketball arcade game, played with ping pong balls, that I designed, built, 3D printed and coded by myself from start to finish.**

FlipShot was my final project for **ECE 350 (Embedded Systems and Hardware Interfaces) at George Mason University, Spring 2025**. It's an adaptation of the basketball arcade game, played with **ping pong balls**. Players type their name on a keypad, pick a difficulty, and get 60 seconds to score as many shots as they can. In the harder mode a servo sweeps the hoop back and forth. Every game is saved to a leaderboard that is served live on a web page.

I did all of it: the mechanical design, the 3D printing, the wiring, and every line of code. I wrote the code by hand, including the keypad name-entry system and the debouncing logic described below.

---

## 📸 Media

I don't have a video of the finished game. These two clips are from development, **before** I painted it and hid the wiring underneath the board:

- [Development footage #1](https://drive.google.com/file/d/1NWxAIhsdhWKeE1KrGYN5FgWryAN02utY/view?usp=sharing)
- [Development footage #2](https://drive.google.com/file/d/1su-7fFoGHoOe0lRoBnYKaPWs_5KGec4c/view?usp=sharing)

---

## 🔧 Hardware & Components

| Component | Role | Interface / Pins (physical `BOARD` numbering) |
|---|---|---|
| **Raspberry Pi** | Main controller: runs the game, drives every peripheral, hosts the leaderboard site | — |
| **Ultrasonic distance sensor** (trigger/echo type) | Detects the ball passing through the hoop | TRIG → pin 31, ECHO → pin 29 |
| **Servo motor** | Sweeps the hoop left and right in Medium mode | PWM signal → pin 12 (50 Hz) |
| **4×4 matrix keypad** | Name entry and mode selection | Rows → 11, 36, 13, 15 · Columns → 16, 18, 22, 7 |
| **16×2 character LCD with I²C backpack** | Shows prompts, countdown, live score and final score | I²C bus 1, address `0x27` |
| **Custom 3D-printed structure** | Hoop, backboard and mounting, designed and printed by me | — |

In the finished version all the cables run underneath the board so you can't see them, and the whole build is painted.

---

## 🎮 How the Game Plays

1. **Welcome:** the LCD flashes *"Hi! Welcome to FlipShot"* three times.
2. **Enter your name** on the keypad (see [Name Entry](#️-name-entry-two-ways-to-type) below), then press `#` to confirm.
3. **Choose a mode:** `1` = **Easy** (fixed hoop), `2` = **Medium** (moving hoop).
4. **Ready… Set… Go!** A countdown on the LCD starts the round.
5. **60 seconds of play.** The screen shows `Time Left` and `Score` and updates once per second.
6. **Game over:** the final score is displayed, and the player's name, mode and score are appended to `leaderboard.csv`.
7. The game resets on its own for the next player.

---

## 🗂️ Code Structure

```
FinalProject/
├── main_code.py          # Game loop, ultrasonic scoring, servo hoop motion
├── keypad_class.py       # 4x4 keypad driver + multi-press name entry + mode selection
├── lcd_class.py          # 16x2 I2C LCD driver written at the register/nibble level
├── leaderboard.csv       # Real scores from playtesting (name, mode, score)
└── webapp/
    ├── app.py            # Flask leaderboard server
    ├── templates/
    │   └── leaderboard.html
    ├── templates.zip
    └── static/
        └── style.css
```

---

## 🧠 How It Works & the Decisions Behind It

### 1. Detecting a basket: `check_dist()` / `update_score()`

The ultrasonic sensor points across the hoop. To take a reading I send a **15 µs pulse** on TRIG, time how long ECHO stays high, and convert that time to distance:

```
distance = (t2 - t1) × 340 m/s ÷ 2
```

The division by 2 is there because the sound goes out and comes back. If the measured distance is **≤ 0.07 m (the diameter of the hoop)**, something is inside the hoop, so it counts as a basket.

**Debouncing the score:** one ball takes a moment to fall through the hoop, and the sensor would pick it up on several readings in a row and count one basket many times. I fixed this with a **0.5 s lockout** after each basket. A single shot is counted exactly once, and real follow-up shots still register.

### 2. The moving hoop (Medium mode): `move_hoop()`

The servo runs on a 50 Hz PWM signal. I convert an angle to a duty cycle with:

```
duty = 2.5 + 10 × angle / 180
```

The hoop sweeps from **25° to 50° and back**, one degree at a time with a 10 ms step. I chose a narrow sweep on purpose: it makes the game harder without carrying the hoop out of reach.

The key decision here: **`update_score()` runs at every step of the sweep**, not only between sweeps. The motion and the scoring are interleaved in the same loop, so a shot is never missed while the hoop is moving, and I didn't need threads. When the round ends the servo is put back to rest.

### 3. Keypad driver: `getKey()`

The keypad is a 4×4 matrix, so I scan it in two phases:

1. Drive every **column LOW**, set the rows as inputs with pull-ups, and find the row that reads `0`.
2. Flip the direction: set the columns as inputs with pull-downs, drive **only that row HIGH**, and find the column that reads `1`.

The row and column together pick one entry in the key map. After every scan `exit()` puts all the pins back into a safe input state, so no pin stays driven between reads.

### 4. ✍️ Name entry: two ways to type

The keypad has only 16 keys, but players need the whole alphabet. I designed a scheme with **two ways to type a character**:

**Way 1: single press.** One press types the key exactly as printed: digits `0–9`, the letters **A, B, C, D**, and `*`.

**Way 2: multi-press, like old phone keyboards.** Pressing the same key again within the time window gives the rest of the alphabet. **E through Z** are spread across the number keys and `*`:

| Key | ×1 | ×2 | ×3 |
|---|---|---|---|
| 1 | 1 | E | F |
| 2 | 2 | G | H |
| 3 | 3 | I | J |
| 4 | 4 | K | L |
| 5 | 5 | M | N |
| 6 | 6 | O | P |
| 7 | 7 | Q | R |
| 8 | 8 | S | T |
| 9 | 9 | U | V |
| * | * | W | X |
| 0 | 0 | Y | Z |
| A | A | **Del** | |
| # | **Submit name** | | |

The mapping is stored in a dictionary keyed by **`(key, press_count)` tuples**, so finding the right character is a single lookup. If a combination has no mapping, the code falls back to the original key so input is never lost. Pressing `A` twice **deletes** the last character, and `#` submits the name.

**My debouncing / multi-press timing logic:**
- After the first press, a **2-second window** opens.
- The keypad is polled every **0.2 s**. Each repeat press of the same key increases the count **and restarts the 2-second window**, so a player can tap at their own pace.
- When the window runs out with no new press, the character is locked in.
- The 0.2 s polling interval also works as the debounce: a single physical press is not read as many presses.
- The LCD shows live feedback at every step (*"First press: 2"*, *"Pressed again! Count = 2"*, *"Final detected: G"*), so the player always knows what the keypad registered.

### 5. LCD driver: `lcd_class.py`

The LCD driver works directly at the register level over I²C:
- It runs the HD44780 **4-bit initialization sequence** (`0x30` three times, then `0x20`) with the required timing delays.
- Each byte is split into two **nibbles**, and the **Enable** bit is pulsed for each one through the I²C expander.
- It uses bit masks for **RS, RW, Enable and Backlight**. The backlight bit is kept in a persistent `data_mask` so it stays on across every write.
- `display_data(line1, line2)` clears the screen, places the cursor on each row, and **trims or pads each line to 16 characters** so text from an earlier screen never stays behind.

### 6. Game timing: `main_code.py`

- The round is timed with `time.time()` rather than by counting loop iterations, so it lasts **60 seconds** whatever the mode or loop speed.
- The LCD is redrawn **only once per second**. Redrawing on every loop pass would slow the scoring loop and make the screen flicker.
- A clean `destroy()` on `Ctrl+C` stops the PWM, clears the screen and releases the GPIO pins.

### 7. Live leaderboard: `webapp/`

Each game adds a row (`name,mode,score`) to `leaderboard.csv`. A **Flask** app reads that file, **groups the players by mode**, sorts each group by score from highest to lowest, and shows ranked tables. The page **refreshes itself every 5 seconds**, so with the server running on the Pi (`0.0.0.0:5000`), anyone on the same network can watch the standings change live. The CSV in this repo holds real scores from people who played FlipShot.

---

## ▶️ Running It

On a Raspberry Pi with I²C enabled:

```bash
pip install RPi.GPIO smbus flask
```

> **Note:** `main_code.py` imports `from keypad import keypad` and `from lcd import Screen`. On the Pi the driver files were named `keypad.py` and `lcd.py`, so rename or copy `keypad_class.py` → `keypad.py` and `lcd_class.py` → `lcd.py` before running. The files in this repo are exactly as I submitted them.

```bash
python3 main_code.py          # start the game
cd webapp && python3 app.py   # start the leaderboard → http://<pi-ip>:5000
```
