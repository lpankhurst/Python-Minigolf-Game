#   A Python Game made by Lewis Pankhurst using tkinter. Nov 2022
#   This game is a 2D golf game comprised of three levels with scaling difficulty
#   A Window resolution of 1366x768 has been used
#   Custom font used - but not necessary for game to function - installable here https://www.dafont.com/volleyball.font

import tkinter as tk
import math as m
from PIL import ImageTk

class Window(tk.Tk): # Inherit an empty window

    def __init__(self, colour, level, score):
        super().__init__() # This initialises our empty window, allowing us to call it self
        self.colour = colour

        #Specifying what the window should look like
        self.title("2D Golf Game")
        self.geometry("1366x768") #One of the standard sizes
        self.resizable(width=False, height=False)

        #Some parameters with starting values
        self.ball_pos_x = 5 
        self.ball_pos_y = 720 # 0,768 is bottom left
        self.relative_x = 150
        self.relative_y = 720 - 150
        self.theta = m.pi/2
        self.num_shots = 0
        self.total_num_shots = score
        self.current_level = level
        self.max_hyp = 280

        #Creating a canvas
        self.canvas = tk.Canvas(self, width="1366", height="768", bg="lightblue")
        self.canvas.grid() # We can use pack since it fills the entire window
        self.format_general()
        if self.current_level == 1: #In case we are loading a saved game
            self.format_level1()
        elif self.current_level == 2:
            self.format_level2()
        elif self.current_level == 3:
            self.format_level3()


        #Launch the key bindings
        self.start()
        # Cheat codes and boss- key needs to be always enabled
        self.boss_key_bind = self.bind("1", self.boss_key)
        self.bind("2", self.reduce_score)
        self.bind("3", self.skip_level)
        self.bind("4", self.increase_max_power)
        self.focus_force() # Focus onto this window
        self.mainloop()

    #-- Methods --
    def format_general(self):
        #Basic layout of any level
        #Creating the ball
        self.ball = Ball(self.canvas, self.restart_pointer, self.level_passed, self.current_level, self.colour)
        #Creating the floor
        self.canvas.create_rectangle(0,720,1366,768,fill="lime")
        #Creating the hole
        self.canvas.create_arc(1200,700,1240,740,start=180,extent=180,fill="black")
        #Creating shot counter label
        self.shot_label = self.canvas.create_text(120,60,text="Shot number "+ str(self.num_shots),font="Volleyball")
        self.canvas.create_text(1020,60,text="Level "+ str(self.current_level),font="Volleyball")

    def format_level1(self):
        self.canvas.create_arc(400,700,600,740,start=180,extent=180,fill="yellow") #Creating a bunker
        self.ice_floor = ImageTk.PhotoImage(file="ice_texture.jpg")
        self.canvas.create_image(800,735, image = self.ice_floor) #Image free to use https://pxhere.com/en/photo/830142?utm_content=shareClip&utm_medium=referral&utm_source=pxhere 

    def format_level2(self):
        self.building = ImageTk.PhotoImage(file = "building.png") #Image free to use from https://www.cleanpng.com/png-building-png-64617/
        self.canvas.create_image(600,620,image = self.building) 
        self.max_hyp = 350 #Setting the max power for this level

    def format_level3(self):
        self.wall = self.canvas.create_rectangle(500,0,530,768,fill="black",width=0)
        self.canvas.tag_lower(self.wall) # Dropping this down a layer so the slit goes over it
        self.max_hyp = 400


    def aim_cursor(self, event): # Follow the pointer to where the mouse is aiming
        x,y = event.x, event.y #x and y are the coordinates of where we aimed
        self.relative_x = x - self.ball_pos_x #Relative distance x direction from ball to where we aimed
        self.relative_y = self.ball_pos_y - y #Relative distance y direction from ball to where we aimed
        if self.relative_x > 0: #Use only positive values for theta
            self.theta = m.atan(self.relative_y/self.relative_x)
        elif self.relative_x < 0:
            self.theta = m.pi + m.atan(self.relative_y/self.relative_x)
        else:
            self.theta = m.pi/2 # And have boundary for if we shoot straight up
        
        hyp = m.sqrt(self.relative_x**2 + self.relative_y**2) # Calculate the hypotenuse
        if hyp > self.max_hyp: #If we are shooting too hard, instead shoot at predetermined power
            x = (self.max_hyp * m.cos(self.theta)) + self.ball_pos_x
            y = (self.ball_pos_y - (self.max_hyp * m.sin(self.theta)))
            #Need to set relativex and y so that there is a limit of power
            self.relative_x = x - self.ball_pos_x
            self.relative_y = self.ball_pos_y - y

        #Updating the coords of the line
        self.canvas.coords(self.pointer,self.ball_pos_x+15,self.ball_pos_y-15,x,y)#Pointer starts in center of ball
    
    def fire(self, event): #Prepare the values before firing the ballc
        self.ball.x_velocity = (self.relative_x)/40 #Lowering the value of the velocity before passing them
        self.ball.y_velocity = (-self.relative_y)/40
        self.canvas.unbind("<Motion>", self.aim_bind) #Unbind so we cant aim while shooting
        self.canvas.unbind("<Button-1>", self.shoot_bind) # Unbind so we cant shoot again until ball has stopped moving
        self.canvas.delete(self.pointer)
        self.num_shots += 1
        self.canvas.itemconfigure(self.shot_label, text="Shot number "+ str(self.num_shots))
        self.ball.animate_ball()

    def start(self): #Rebinding binds after they have been unbound
        self.aim_bind = self.canvas.bind("<Motion>", self.aim_cursor)
        self.shoot_bind = self.canvas.bind("<Button-1>", self.fire)
        self.pause_bind = self.bind("<space>", self.pause)
        self.pointer = self.canvas.create_line(self.ball_pos_x+15,self.ball_pos_y-15,self.ball_pos_x+100,self.ball_pos_y-100,fill="black",dash=(5,5),arrow=tk.LAST) #Re-create the pointer, in the center of the ball

    def restart_pointer(self): # Restart the pointer after the ball has landed
        left_pos, bottom_pos = self.ball.get_coordinates() #Get the coordinates of the ball 
        self.ball_pos_x = left_pos #Update the ball_pos_x and y
        self.ball_pos_y = bottom_pos
        self.start()
    
    def pause(self, event): # Call the ball pause method and bind a save key to the window
        self.ball.pause()
        self.save_bind = self.bind("<s>", self.save)
    
    def level_passed(self): # If we enter the hole
        self.canvas.create_text(650,350,text="LEVEL COMPLETE",font=("Volleyball",20)) # Display a message
        self.total_num_shots += self.num_shots # Increase the total score
        self.num_shots = 0 # Reset level score
        if self.current_level < 3: # Reset the ball and ask if they want to proceed
            self.current_level += 1
            self.ball_pos_x = 5 
            self.ball_pos_y = 720
            self.canvas.create_text(650,400,text="Press Enter for next level",font=("Volleyball",12))
            self.next_level_bind = self.bind("<Return>", self.next_level)
            self.save_bind = self.bind("<s>", self.save)
        else: # If we just finsihed level 3 then end the game
            self.game_finished()

    def save(self, event): # If we save our game - get the user to enter their name
        self.unbind("<s>", self.save_bind)
        self.canvas.delete("all") # The ball movement does not kill cleanly like this
        # Allowing the user to enter their name to save the level they are on
        self.name_entry = tk.Entry(self, width=30)
        self.name_label = tk.Label(self, text="Enter your name", bg="lightblue")
        self.name_label2 = tk.Label(self, text="press enter to save", bg="lightblue")
        self.name_label.config(font=("Volleyball",15))
        self.name_label2.config(font=("Volleyball",12))
        self.canvas.create_window(680,400, window=self.name_entry) # Creating a space for the widgets to be placed
        self.canvas.create_window(680,300, window=self.name_label)
        self.canvas.create_window(680,500, window=self.name_label2)

        self.save_exit_bind = self.bind("<Return>", self.save_exit)

    def save_exit(self, event): # Save and exit
        self.unbind("<Return>", self.save_exit_bind) 
        self.file = open("scores.txt", "a")
        data = self.name_entry.get() + " " + str(self.total_num_shots) + " " + str(self.current_level) +"\n" 
        self.file.write(data) # Write the save data to the file
        self.file.close()
        self.destroy()
        Home() # Re-initiate our game

    def next_level(self, event): # Trigger the next level
        self.unbind("<Return>", self.next_level_bind) # Resetting the canvas and binds
        self.unbind("<s>", self.save_bind)
        self.canvas.delete("all") 
        self.format_general() # Reformatting
        # Adding to this layout depending on the current level
        if self.current_level == 2:
            self.format_level2()
        elif self.current_level == 3:
            self.format_level3()
        self.start()

    def game_finished(self): # If the game is over, display appropriate messages
        self.canvas.delete("all")
        self.canvas.create_text(650,350,text="CONGRATULATIONS",font=("Volleyball",30))
        #Tkinter prompts to get their name
        self.name_entry = tk.Entry(self, width=30) # Ask them to enter their name 
        self.name_label = tk.Label(self, text="Enter your name", bg="lightblue")
        self.name_label2 = tk.Label(self, text="press enter to save", bg="lightblue")
        self.name_label.config(font=("Volleyball",15))
        self.name_label2.config(font=("Volleyball",12))
        self.canvas.create_window(680,400, window=self.name_entry) # Creating windows to store the tk widgets inside the canvas
        self.canvas.create_window(680,300, window=self.name_label)
        self.canvas.create_window(680,500, window=self.name_label2)
        self.current_level = "Completed" # Change the level to Completed
        self.save_exit_bind = self.bind("<Return>", self.save_exit) # Re-use the save_exit method

    def boss_key(self, event): # A boss key to make it look like we are working
        self.canvas.delete("all") # Remove all elements from the canvas
        self.boss_image = ImageTk.PhotoImage(file = "boss_key.png") # Image made by myself
        self.canvas.create_image(675,384,image = self.boss_image)
        self.title("VS Code ") # Make it seem like we are in VS Code doing work
        self.unbind("1", self.boss_key_bind)
        self.bind("1", self.undo_boss_key) # Create an undo bind so we can return to our game
    
    def undo_boss_key(self, event): # A way to undo the boss key, and return to our current level
        self.destroy() 
        Window(self.colour,self.current_level,self.total_num_shots) # Reinitiate our game at the current level

    def reduce_score(self, event): # A cheat to reduce the score
        if self.num_shots >= 1: # So we can't have negative scores
            self.num_shots -= 1
            self.canvas.itemconfigure(self.shot_label, text="Shot number "+ str(self.num_shots)) # Update the label

    def skip_level(self, event): # A cheat to skip the current level
        self.current_level += 1
        self.canvas.delete("all")
        self.format_general()
        self.ball_pos_x = 5 # Reset ball position so, pointer loads correctly
        self.ball_pos_y = 720
        # Adding to this layout depending on the current level
        if self.current_level == 2:
            self.format_level2()
        elif self.current_level == 3:
            self.format_level3()
        self.start()

    def increase_max_power(self, event): # A cheat to increase how hard we can shoot the ball
        self.max_hyp += 100


class Ball:

    def __init__(self, canvas, restart_pointer, level_passed, level, colour= "black"):
        
        self.ball_colour = colour
        self.x_velocity = 5.0 #Initial values for testing, are changed when fired
        self.y_velocity = -5.0
        self.canvas = canvas
        self.ball = self.canvas.create_oval(5,720,35,690,fill=self.ball_colour)#Radius 15px
        self.interval = 0.012 #Delay between frames of the ball moving
        self.restart = restart_pointer #Methods from the other class, so we can call them
        self.level_passed = level_passed
        self.is_paused = False
        self.level = level
        self.on_ice = False # We don't want to exponentially increase speed on a slippery surface
        if self.level == 3:
            self.slit = self.canvas.create_rectangle(500,500,530,400,fill="lightblue",width=0)
            self.slit_velocity = 3
            self.move_slit()
        self.canvas.tag_raise(self.ball) # Bring our ball to the top layer, so it is always visible

    def pause(self):
        self.is_paused = not self.is_paused # Toggle paused state
        if self.is_paused: # If paused display appropriate message
            self.paused_label = self.canvas.create_text(650,350,text="GAME PAUSED",font=("Volleyball",20))
            self.pause_label1 = self.canvas.create_text(700,400,text="Press S to save and exit",font=("Volleyball",12))
            self.pause_label2 = self.canvas.create_text(700,450,text=". . . Or Space to unpause",font=("Volleyball",12))
        else: # If unpaused, destroy the message
            self.canvas.delete(self.paused_label,self.pause_label1,self.pause_label2)
    
    def animate_ball(self): # This will run in the background once we shoot
        if not self.is_paused: # So only move if we are paused
            try: # Since we dont destroy our ball cleanly and this runs constantly
                self.canvas.move(self.ball,self.x_velocity,self.y_velocity)
            except:
                pass
            (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
            self.collision_detection_general() # Do collision detection depending on level
            if self.level == 1:
                self.collision_detection1()
            elif self.level == 2:
                self.collision_detection2()
            elif self.level == 3:
                self.collision_detection3()

            self.y_velocity = self.y_velocity + 9.5*self.interval # suvat equations, g = 9.5, since it looks better
            self.x_velocity *= 0.999 # Simulate air resistance

        if self.is_moving(): #If we are still moving
            try: # Since we dont destroy our ball cleanly and this runs constantly
                (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
                if 1190 < left_pos < 1225 and 719 <= bottom_pos <= 721 and self.x_velocity < 5: #Check if we are in the hole, not going too fast
                    self.canvas.delete(self.ball)
                    self.level_passed()
                else: # Otherwise keep moving
                    self.canvas.after(int(self.interval*1000), self.animate_ball)
            except: # Since we dont destroy our ball cleanly and this runs constantly
                pass
        else: #If we are not moving call our restart function
            self.restart()

    def collision_detection_general(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        # The ball may be detected when it is inside the wall so we need to move it back to the wall occasionally
        if right_pos >= 1366:#Right wall collision detection
            gap = right_pos - 1366 # Figure out where the ball is
            self.x_velocity *= -0.7
            self.canvas.coords(self.ball, left_pos-gap, top_pos,1366,bottom_pos)# Move the ball to where it was when it collided with wall
        elif left_pos <= 0: # Left wall collision detection
            gap = left_pos
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, 0, top_pos,right_pos-gap,bottom_pos)
        elif bottom_pos >= 720: # Floor collision detection
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - 720
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif top_pos <= 0: # Ceiling collision detection
            self.y_velocity *= -0.8
            self.x_velocity *= 0.9
            gap = top_pos
            self.canvas.coords(self.ball, left_pos, 0,right_pos,bottom_pos-gap)

    def collision_detection1(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if bottom_pos >= 720 and right_pos >= 415 and left_pos <= 585: # If in bunker
            self.y_velocity *= -0.4
            self.x_velocity *= 0.4 # Decrease velocity dramatically
            gap = bottom_pos - 720
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif bottom_pos >= 720 and right_pos >= 724 and left_pos <= 905 and not self.on_ice: # If on ice
            self.x_velocity *= 1.5 # Increase our x speed if we land on ice 
            gap = bottom_pos - 720
            self.on_ice = True # But we only increase once each time we are on the ice
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif bottom_pos >= 720 and not(right_pos >= 724 and left_pos <= 905):
            self.on_ice = False # If we don't land on ice, allow the speed if we do to increase again

    def collision_detection2(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if 550 >= right_pos >= 511 and 484 <= bottom_pos <= 720: #Left wall of building
            gap = right_pos - 511
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, left_pos-gap, top_pos,511,bottom_pos)
        elif 680 <= left_pos <= 687 and 484 <= bottom_pos <= 720:  # Right wall of building
            gap = left_pos - 687
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, 687, top_pos,right_pos-gap,bottom_pos)
        elif 470 <= bottom_pos <= 490 and 511 <= right_pos <= 687: # Roof of building
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - 470
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,470)

    def collision_detection3(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if 514 >= right_pos >= 500 and (bottom_pos >= self.bottom_slit or top_pos <= self.top_slit): # Left walls of not the slit
            gap = right_pos - 500
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, left_pos-gap, top_pos,500,bottom_pos)
        elif 530 >= left_pos >= 516 and (bottom_pos >= self.bottom_slit or top_pos <= self.top_slit): # right walls of not the slit
            gap = left_pos - 530
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball,530, top_pos,right_pos-gap,bottom_pos)
        elif 500 >= left_pos+15 >= 530 and self.bottom_slit <= bottom_pos <= self.bottom_slit+2: # Bottom of slit
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - self.bottom_slit
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,self.bottom_slit)
        elif 500 >= left_pos+15 >= 530 and self.top_slit >= top_pos >= self.top_slit-2: # Top of slit
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - self.top_slit
            self.canvas.coords(self.ball, left_pos, self.top_slit,right_pos,bottom_pos-gap)

    def is_moving(self): # Find out if we are moving
        return not (-0.02 < float(self.x_velocity) < 0.02 and -0.02 < float(self.y_velocity) < 0.2) #We can disregard tiny velocities

    def get_coordinates(self): # Return the coordinates, so x_pos and y_pos can be found by other class
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        return left_pos, bottom_pos

    def move_slit(self):
        if not self.is_paused: # If we are not paused then move the slit
            self.canvas.move(self.slit,0,self.slit_velocity)
            try: # Since we dont destroy our slit cleanly and this runs constantly
                (left_slit,self.top_slit,right_slit,self.bottom_slit) = self.canvas.coords(self.slit)
            except:
                pass
            if self.bottom_slit >= 550 or self.top_slit <= 300:
                self.slit_velocity *= -1

        self.canvas.after(150, self.move_slit)
                 

class Home(tk.Tk):
    def __init__(self):
        super().__init__() # This initialises our empty window, allowing us to call it self
        #Specifying what the window should look like
        self.title("2D Golf Game")
        self.geometry("1366x768") #One of the standard sizes
        self.resizable(width=False, height=False)

        #Defining default ball colour
        self.colour = "White"
        #And other default values
        self.start_level = 1
        self.current_score = 0

        #Making the background, using an image
        self.bg = tk.PhotoImage(file = "background.png") # Image made by me
        self.label = tk.Label(self,image=self.bg).place(x=0,y=0)#The background goes inside a label

        #Creating a frame to store the buttons
        self.button_frame = tk.Frame(self,width=600,height=300,bg="#99D9EA")
        self.button_frame.place(x=330,y=134)
        #Creating a frame to store the leaderboard
        self.leaderboard_frame = tk.Frame(self,width=300,height=400,bg="#99D9EA")
        self.leaderboard_frame.place(x=1066,y=3)#y=3 since there is a weird border gap at the top

        #Creating our buttons
        self.play_button = tk.Button(self.button_frame, text="PLAY GAME", bg="#99D9EA",command=self.start_game)
        self.play_button.config(font=("Volleyball",20))
        self.play_button.grid(padx=150,pady=10)
        self.load_button = tk.Button(self.button_frame, text="LOAD GAME", bg="#99D9EA",command=self.load_game_message)
        self.load_button.config(font=("Volleyball",20))
        self.load_button.grid(row=1,padx=150,pady=10)
        self.customise_button = tk.Button(self.button_frame, text="CUSTOMISE COLOUR", bg="#99D9EA", command=self.customise_colour)
        self.customise_button.config(font=("Volleyball",20))
        self.customise_button.grid(row=2,padx=150,pady=10)

        #Leaderboard header
        self.leaderboard_label = tk.Label(self.leaderboard_frame, text="HIGHSCORES", bg="#99D9EA")
        self.leaderboard_label.config(font=("Volleyball",12))
        self.leaderboard_label.grid(row=0,padx=10,pady=10)

        self.fill_leaderboard()
        self.mainloop()

    def start_game(self):
        self.destroy() # Destroy this tkinter window 
        Window(self.colour,self.start_level,self.current_score) # Create the game tkinter window
    
    def customise_colour(self):
        # widgets to allow user to enter colour
        self.colour_entry = tk.Entry(self.button_frame, width=30)
        self.colour_label = tk.Label(self.button_frame, text="Enter ball colour", bg="#99D9EA")
        self.colour_label2 = tk.Label(self.button_frame, text="press enter to save", bg="#99D9EA")
        self.colour_label.config(font=("Volleyball",12))
        self.colour_label2.config(font=("Volleyball",10))
        self.colour_entry.grid(row=4,padx=150,pady=10)
        self.colour_label.grid(row=3,padx=150,pady=10)
        self.colour_label2.grid(row=5,padx=150,pady=10)
        self.colour_bind = self.bind("<Return>", self.set_colour) # bind return to set this colour
    
    def set_colour(self, event):
        self.unbind("<Return>", self.colour_bind) # unbind return
        self.colour = self.colour_entry.get() # Get what the user entered
        self.colour_entry.destroy() # Destroy the widgets
        self.colour_label.destroy()
        self.colour_label2.destroy()
        self.saved_colour_label = tk.Label(self.button_frame, text="Saved!", bg="#99D9EA") # Display Saved message
        self.saved_colour_label.config(font=("Volleyball",10))
        self.saved_colour_label.grid(row=3,padx=150,pady=10)  

    def fill_leaderboard(self): # Open our scores file and fill the leaderboard
        file = open("scores.txt", "r")
        unsorted = []
        for line in file:
            record = line.split()
            if record[2] == "Completed": # If that player actually completed the game
                record[1] = int(record[1]) # Cast the score to int
                unsorted.append(record) # Add this record to array to be sorted
        sorted_leaderboard = sorted(unsorted, key=lambda x: x[1]) # Sort the array by lowest score first
        for i in range(len(sorted_leaderboard)): # Display these scores
            leaderboard_data = tk.Label(self.leaderboard_frame, text=sorted_leaderboard[i][0], bg="#99D9EA")
            leaderboard_data.config(font=("Volleyball",12))
            leaderboard_data.grid(row=i+1,padx=10,pady=10,sticky="W")
            leaderboard_data2 = tk.Label(self.leaderboard_frame, text=str(sorted_leaderboard[i][1]), bg="#99D9EA")
            leaderboard_data2.config(font=("Volleyball",12))
            leaderboard_data2.grid(row=i+1,column=1,padx=10,pady=10,sticky="W")
            if i >= 9:
                break # We dont want the leaderboard to be too big, only the top scores

    def load_game_message(self):
        # widgets to allow user to enter their name
        self.load_entry = tk.Entry(self.button_frame, width=30)
        self.load_label = tk.Label(self.button_frame, text="Enter your name", bg="#99D9EA")
        self.load_label2 = tk.Label(self.button_frame, text="press enter to load your last saved game", bg="#99D9EA")
        self.load_label.config(font=("Volleyball",12))
        self.load_label2.config(font=("Volleyball",10))
        self.load_entry.grid(row=4,padx=150,pady=10)
        self.load_label.grid(row=3,padx=150,pady=10)
        self.load_label2.grid(row=5,padx=150,pady=10)
        self.load_bind = self.bind("<Return>", self.load_game) # Bind return to load last saved game

    def load_game(self, event):
        self.unbind("<Return>", self.load_bind) # unbind return
        self.name = self.load_entry.get() # Get the name they entered
        self.load_entry.destroy() # Destroy our widgets
        self.load_label.destroy()
        self.load_label2.destroy()
        for line in reversed(open("scores.txt").readlines()): #Open the file in reversed order, to read the latest save in that name
            record = line.split()

            if record[0] == self.name and record[2] != "Completed": # If we find a match, that hasnt completed the game
                self.current_score = int(record[1])
                self.start_level = int(record[2])
                self.start_game() # Start the game at that level
                break # Break so we don't start more than one game
        
        not_found_label = tk.Label(self.button_frame, text="User not found", bg="#99D9EA") # Create a label if that user is not found
        not_found_label.config(font=("Volleyball",12))
        not_found_label.grid(row=3,padx=150,pady=10)


if __name__ == "__main__":
    Home()