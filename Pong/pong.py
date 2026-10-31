import turtle
import random
import threading

try:
    import winsound # Only available on Windows
except ImportError:
    winsound = None

WIDTH = 800
HEIGHT = 600
paddle_speed = 15
start_speed = 15
max_speed = 45
ai_speed = 9 # Max speed of the computer paddle (lower = easier)
win_score = 10 # Points needed to win the game
serve_delay = 50 # Frames the ball waits after a goal (50 x 20 ms = 1 second)



screen = turtle.Screen()
screen.title("Amadeo Pong")
screen.setup(width=WIDTH, height=HEIGHT)
screen.bgcolor("green")
screen.tracer(0) # Turns off the screen updates for better performance

line = turtle.Turtle()
line.hideturtle ()
line.color("white")
line.penup()
line.goto(0, 300) # Move the turtle to the top of the screen
line.setheading(270) # Set the heading to 270 degrees (downwards)

for _ in range(15): # Draw 15 dashes
    line.pendown()
    line.forward(20) # Draw a dash
    line.penup()
    line.forward(20) # Move forward without drawing

def draw_paddle(x):
    paddle = turtle.Turtle()
    paddle.speed(0)
    paddle.shape("square")
    paddle.color("white")
    paddle.shapesize(stretch_wid=5, stretch_len=1)
    paddle.penup()
    paddle.goto(x, y=0)
    return paddle

left_paddle = draw_paddle(-350) # Draw the left paddle at x = -350
right_paddle = draw_paddle(350) # Draw the right paddle at x = 350

ball = turtle.Turtle()
ball.shape("square")
ball.color("white")
ball.penup()
ball.goto(0, y=0)
ball.hideturtle() # Hidden until a game starts
ball.dx = 0 # type: ignore
ball.dy = 0 # type: ignore

left_score = 0
right_score = 0

pen = turtle.Turtle() # Create a turtle for displaying the score
pen.hideturtle()
pen.color("white")
pen.penup()
pen.goto(0, 250)

def update_score():
    pen.clear()
    pen.write(f" {left_score} : {right_score}", align="center", font=("Courier", 32, "bold"))

update_score()

message = turtle.Turtle() # Create a turtle for menu and winner messages
message.hideturtle()
message.color("white")
message.penup()
message.goto(0, -60)

MENU_TEXT = "1 = gegen Computer\n2 = zwei Spieler\nLeertaste = Pause"

def show_message(text):
    message.clear()
    message.write(text, align="center", font=("Courier", 24, "bold"))

def beep(frequency, duration=40):
    if winsound:
        # Play in a thread, because winsound.Beep blocks and would make the game stutter
        threading.Thread(target=winsound.Beep, args=(frequency, duration), daemon=True).start()
    else:
        screen.getcanvas().bell() # Simple system sound on other systems

state = "menu" # "menu", "playing" or "over"
vs_computer = False
paused = False
wait_frames = 0 # Counts down while the ball waits in the middle

keys = {
    "w": False,
    "s": False,
    "Up": False,
    "Down": False
}

def on_key_press(key):
    keys[key] = True

def on_key_release(key):
    keys[key] = False

def reset_ball(direction):
    global wait_frames
    ball.goto(0, 0)
    ball.dx = start_speed * direction # type: ignore
    ball.dy = start_speed * random.choice([-1, -0.5, 0.5, 1]) # type: ignore # At most as fast as dx, so the angle stays at 45 degrees or less
    wait_frames = serve_delay # Let the ball wait in the middle before it starts

def start_game(computer):
    global state, vs_computer, paused, left_score, right_score
    if state == "playing": # Ignore 1 and 2 during a running game
        return
    vs_computer = computer
    paused = False
    left_score = 0
    right_score = 0
    update_score()
    left_paddle.sety(0)
    right_paddle.sety(0)
    message.clear()
    ball.showturtle()
    reset_ball(random.choice([-1, 1]))
    state = "playing"

def toggle_pause():
    global paused
    if state != "playing": # Pause only works during a game
        return
    paused = not paused
    if paused:
        show_message("Pause")
    else:
        message.clear()

screen.listen()
for k in keys:
    screen.onkeypress(lambda k=k: on_key_press(k), k)
    screen.onkeyrelease(lambda k=k: on_key_release(k), k)
screen.onkeypress(lambda: start_game(True), "1")
screen.onkeypress(lambda: start_game(False), "2")
screen.onkeypress(toggle_pause, "space")

def move_paddles():
    if keys["Up"] and right_paddle.ycor() < 250:
        right_paddle.sety(right_paddle.ycor() + paddle_speed)
    if keys["Down"] and right_paddle.ycor() > -250:
        right_paddle.sety(right_paddle.ycor() - paddle_speed)
    if vs_computer:
        return # The computer moves the left paddle
    if keys["w"] and left_paddle.ycor() < 250:
        left_paddle.sety(left_paddle.ycor() + paddle_speed)
    if keys["s"] and left_paddle.ycor() > -250:
        left_paddle.sety(left_paddle.ycor() - paddle_speed)

def move_computer():
    # Follow the ball when it comes towards the computer, otherwise return to the middle
    target = ball.ycor() if ball.dx < 0 else 0 # type: ignore
    diff = target - left_paddle.ycor()
    if abs(diff) > 10: # Small dead zone so the paddle does not jitter
        step = min(ai_speed, abs(diff))
        new_y = left_paddle.ycor() + (step if diff > 0 else -step)
        left_paddle.sety(max(-250, min(250, new_y)))

def check_winner():
    global state
    if left_score < win_score and right_score < win_score:
        return
    if vs_computer:
        winner = "Du gewinnst!" if right_score > left_score else "Der Computer gewinnt!"
    else:
        winner = "Links gewinnt!" if left_score > right_score else "Rechts gewinnt!"
    state = "over"
    ball.hideturtle()
    show_message(f"{winner}\n\nNochmal?\n{MENU_TEXT}")

def move_ball():
    global left_score, right_score

    ball.setx(ball.xcor() + ball.dx) # type: ignore
    ball.sety(ball.ycor() + ball.dy) # type: ignore

    # Ball collision with top and bottom walls
    if ball.ycor() > 290:
        ball.sety(290)
        ball.dy *= -1 # type: ignore
        beep(500) # Low beep for walls

    if ball.ycor() < -290:
        ball.sety(-290)
        ball.dy *= -1 # type: ignore
        beep(500) # Low beep for walls

    # Ball collision with paddles
    # Checks whether the ball crossed the paddle line in this frame, so a fast ball cannot skip it
    if ball.dx > 0 and ball.xcor() > 340 and ball.xcor() - ball.dx <= 340 and abs(ball.ycor() - right_paddle.ycor()) < 50: # type: ignore
        ball.setx(340)
        ball.dx *= -1 # type: ignore
        beep(1000) # High beep for paddles
        if abs(ball.dx) < max_speed: # type: ignore
            ball.dx *= 1.1 # type: ignore # Increase speed by 10%
            ball.dy *= 1.1 # type: ignore # Increase speed by 10%

    if ball.dx < 0 and ball.xcor() < -340 and ball.xcor() - ball.dx >= -340 and abs(ball.ycor() - left_paddle.ycor()) < 50: # type: ignore
        ball.setx(-340)
        ball.dx *= -1 # type: ignore
        beep(1000) # High beep for paddles
        if abs(ball.dx) < max_speed: # type: ignore
            ball.dx *= 1.1 # type: ignore # Increase speed by 10%
            ball.dy *= 1.1 # type: ignore # Increase speed by 10%

    # Ball goes out of bounds
    if ball.xcor() > 390:
        left_score += 1
        update_score()
        beep(250, 300) # Long, deep beep for a goal
        reset_ball(direction=-1)
        check_winner()

    if ball.xcor() < -390:
        right_score += 1
        update_score()
        beep(250, 300) # Long, deep beep for a goal
        reset_ball(direction=1)
        check_winner()

def game_loop(): # Spielschleife
    global wait_frames

    if state == "playing" and not paused:
        move_paddles()
        if vs_computer:
            move_computer()

        if wait_frames > 0: # Ball waits in the middle, paddles can still move
            wait_frames -= 1
        else:
            move_ball()

    screen.update() # Update the screen
    screen.ontimer(game_loop, 20) # Call game_loop again after 20 milliseconds

show_message(MENU_TEXT)
game_loop() # Start the game loop
screen.mainloop() # Start the main loop of the turtle graphics
