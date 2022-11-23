#   A Python Game made by Lewis Pankhurst using tkinter. Nov 2022
#   This game is a 2D golf game comprised of three levels with scaling difficulty
#   A Window resolution of 1366x768 has been used
#   Custom font used - but not necessary for game to function - installable here https://www.dafont.com/volleyball.font

import tkinter as tk
from tkinter import messagebox
import math as m
from PIL import ImageTk
import time

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
        self.ball_pos_y = 720 #0,0 is the top left, 0,768 is bottom left
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
        if self.current_level == 1: #In case we are loading a saved game we may not start at level 1
            self.format_level1()
        elif self.current_level == 2:
            self.format_level2()
        elif self.current_level == 3:
            self.format_level3()


        #Bind moving the cursor to call the aim_cursor method
        self.start()
        self.mainloop()

    #-- Methods --
    def format_general(self):
        #Basic layout of any level
        #Creating the target arrow
        self.pointer = self.canvas.create_line(20,705,100,720-100,fill="black",dash=(5,5),arrow=tk.LAST)
        #Creating the ball
        self.ball = Ball(self.canvas, self.restart, self.level_passed, self.current_level, self.colour)
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
        self.building = ImageTk.PhotoImage(file = "building.png")
        self.canvas.create_image(600,620,image = self.building) #Image free to use from https://www.cleanpng.com/png-building-png-64617/
        self.max_hyp = 350

    def format_level3(self):
        pass

    def aim_cursor(self, event):
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
            x = (self.max_hyp * m.cos(self.theta)) + self.ball_pos_x # Trig to preserve direction
            y = (self.ball_pos_y - (self.max_hyp * m.sin(self.theta))) # But new hypotenuse is the max it can be
            #Need to set relativex and y so that there is a limit of power
            self.relative_x = x - self.ball_pos_x #Relative distance x direction from ball to where we aimed
            self.relative_y = self.ball_pos_y - y #Relative distance y direction from ball to where we aimed

        #Updating the coords of the line
        self.canvas.coords(self.pointer,self.ball_pos_x+15,self.ball_pos_y-15,x,y)#Pointer starts in center of ball
    
    def fire(self, event): #Prepare the values before firing the ball
        self.ball.x_velocity = (self.relative_x)/40 #Lowering the value of the velocity before passing them
        self.ball.y_velocity = (-self.relative_y)/40
        self.canvas.unbind("<Motion>", self.aim_bind) #Unbind so we cant aim
        self.canvas.unbind("<Button-1>", self.shoot_bind) # Unbind so we cant shoot again until ball has stopped moving
        self.canvas.delete(self.pointer)
        self.num_shots += 1
        self.canvas.itemconfigure(self.shot_label, text="Shot number "+ str(self.num_shots))
        self.ball.animate_ball()

    def start(self):
        self.aim_bind = self.canvas.bind("<Motion>", self.aim_cursor)
        self.shoot_bind = self.canvas.bind("<Button-1>", self.fire)
        self.pause_bind = self.bind("<space>", self.pause)

    def restart(self):
        left_pos, bottom_pos = self.ball.get_coordinates() #Get the coordinates of the ball 
        self.ball_pos_x = left_pos #Update the ball_pos_x and y
        self.ball_pos_y = bottom_pos
        self.pointer = self.canvas.create_line(self.ball_pos_x+15,self.ball_pos_y-15,self.ball_pos_x+100,self.ball_pos_y-100,fill="black",dash=(5,5),arrow=tk.LAST) #Re-create the pointer
        self.start()
    
    def pause(self, event):
        self.ball.pause()
        self.canvas.create_text(700,400,text="Press S to save and exit",font=("Volleyball",12))
        self.canvas.create_text(700,450,text=". . . Or Space to unpause",font=("Volleyball",12))
        self.save_bind = self.bind("<s>", self.save)
    
    def level_passed(self):
        self.canvas.create_text(650,350,text="LEVEL COMPLETE",font=("Volleyball",20))
        self.total_num_shots += self.num_shots
        self.num_shots = 0
        if self.current_level < 3:
            self.current_level += 1
            self.ball_pos_x = 5 
            self.ball_pos_y = 720
            self.canvas.create_text(650,400,text="Press Enter for next level",font=("Volleyball",12))
            self.next_level_bind = self.bind("<Return>", self.next_level)
            self.save_bind = self.bind("<s>", self.save)
        else:
            self.game_finished()

    def save(self, event):   
        self.unbind("<s>", self.save_bind)
        self.canvas.delete("all") # The ball movement does not kill cleanly like this
        # Allowing the user to enter their name to save the level they are on
        self.name_entry = tk.Entry(self, width=30)
        self.name_label = tk.Label(self, text="Enter your name", bg="lightblue")
        self.name_label2 = tk.Label(self, text="press enter to save", bg="lightblue")
        self.name_label.config(font=("Volleyball",15))
        self.name_label2.config(font=("Volleyball",12))
        self.canvas.create_window(680,400, window=self.name_entry)
        self.canvas.create_window(680,300, window=self.name_label)
        self.canvas.create_window(680,500, window=self.name_label2)

        self.save_exit_bind = self.bind("<Return>", self.save_exit)

    def save_exit(self, event):
        self.unbind("<Return>", self.save_exit_bind) 
        self.file = open("scores.txt", "a")
        data = self.name_entry.get() + " " + str(self.total_num_shots) + " " + str(self.current_level) +"\n" 
        self.file.write(data)
        self.file.close()
        self.destroy()
        Home()


    def next_level(self, event):
        self.unbind("<Return>", self.next_level_bind)
        self.unbind("<s>", self.save_bind)
        self.canvas.delete("all")
        self.format_general()
        # Adding to this layout depending on the current level
        if self.current_level == 2:
            self.format_level2()
        elif self.current_level == 3:
            self.format_level3()
        self.start()

    def game_finished(self):
        self.canvas.delete("all")
        self.canvas.create_text(650,350,text="CONGRATULATIONS",font=("Volleyball",30))
        self.name_entry = tk.Entry(self, width=30)
        self.name_label = tk.Label(self, text="Enter your name", bg="lightblue")
        self.name_label2 = tk.Label(self, text="press enter to save", bg="lightblue")
        self.name_label.config(font=("Volleyball",15))
        self.name_label2.config(font=("Volleyball",12))
        self.canvas.create_window(680,400, window=self.name_entry)
        self.canvas.create_window(680,300, window=self.name_label)
        self.canvas.create_window(680,500, window=self.name_label2)
        self.current_level = "Completed"
        self.save_exit_bind = self.bind("<Return>", self.save_exit)


class Ball:

    def __init__(self, canvas, restart, level_passed, level, colour= "black"):
        
        self.ball_colour = colour
        self.x_velocity = 5.0 #Initial values for testing, these are changed when fire is called
        self.y_velocity = -5.0
        self.canvas = canvas
        self.ball = self.canvas.create_oval(5,720,35,690,fill=self.ball_colour)#Radius 15px
        self.interval = 0.012 #Delay between frames of the ball moving
        self.x = 0
        self.restart = restart #Methods from the other class
        self.level_passed = level_passed
        self.is_paused = False
        self.level = level
        self.on_ice = False # We don't want to exponentially increase speed on a slippery surface

    def pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.paused_label = self.canvas.create_text(650,350,text="GAME PAUSED",font=("Volleyball",20))
        else:
            self.canvas.delete(self.paused_label)
    
    def animate_ball(self):
        if not self.is_paused:
            self.canvas.move(self.ball,self.x_velocity,self.y_velocity)
            (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
            self.collision_detection_general()
            if self.level == 1:
                self.collision_detection1()
            elif self.level == 2:
                self.collision_detection2()
            elif self.level == 3:
                self.collision_detection3()

            self.y_velocity = self.y_velocity + 9.5*self.interval #Using not acutal value of g since this looks more realistic
            self.x_velocity *= 0.999 #Simulate air resistance

        if self.is_moving(): #If we are still moving
            (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
            if 1190 < left_pos < 1225 and 719 <= bottom_pos <= 721 and self.x_velocity < 5: #Check if we are in the hole, not going too fast
                self.canvas.delete(self.ball)
                self.level_passed()
            else: # Otherwise keep moving
                self.canvas.after(int(self.interval*1000), self.animate_ball)
        else: #If we are not moving call our restart function
            self.restart()

    def collision_detection_general(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if right_pos >= 1366:# Floor and walls collision detection
            gap = right_pos - 1366
            self.x_velocity *= -0.7
            self.canvas.coords(self.ball, left_pos-gap, top_pos,1366,bottom_pos)#Reset ball pos to surface it collided with, rather than underneath
        elif left_pos <= 0:
            gap = left_pos
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, 0, top_pos,right_pos-gap,bottom_pos)
        elif bottom_pos >= 720:
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - 720
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif top_pos <= 0:
            self.y_velocity *= -0.8
            self.x_velocity *= 0.9
            gap = top_pos
            self.canvas.coords(self.ball, left_pos, 0,right_pos,bottom_pos-gap)

    def collision_detection1(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if bottom_pos >= 720 and right_pos >= 415 and left_pos <= 585:
            self.y_velocity *= -0.4
            self.x_velocity *= 0.4 
            gap = bottom_pos - 720
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif bottom_pos >= 720 and right_pos >= 724 and left_pos <= 905 and not self.on_ice:
            self.x_velocity *= 1.5 # Increase our x speed if we land on ice 
            gap = bottom_pos - 720
            self.on_ice = True # But we only increase once each time we are on the ice
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,720)
        elif bottom_pos >= 720 and not(right_pos >= 724 and left_pos <= 905):
            self.on_ice = False

    def collision_detection2(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        if 550 >= right_pos >= 511 and 484 <= bottom_pos <= 720: #Left wall of building
            gap = right_pos - 511
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, left_pos-gap, top_pos,511,bottom_pos)
        elif 680 <= left_pos <= 687 and 484 <= bottom_pos <= 720: 
            gap = left_pos - 687
            self.x_velocity *= -0.8
            self.canvas.coords(self.ball, 687, top_pos,right_pos-gap,bottom_pos)
        elif 470 <= bottom_pos <= 490 and 511 <= right_pos <= 687:
            self.y_velocity *= -0.7
            self.x_velocity *= 0.93 #Lose a bit of x velocity with bouncing of floor
            gap = bottom_pos - 470
            self.canvas.coords(self.ball, left_pos, top_pos-gap,right_pos,470)

    def collision_detection3(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)

    def is_moving(self):
        return not (-0.02 < float(self.x_velocity) < 0.02 and -0.02 < float(self.y_velocity) < 0.2) #We can disregard tiny velocities

    def get_coordinates(self):
        (left_pos,top_pos,right_pos,bottom_pos) = self.canvas.coords(self.ball)
        return left_pos, bottom_pos

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
        self.bg = tk.PhotoImage(file = "background.png")
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
        self.destroy()
        Window(self.colour,self.start_level,self.current_score)
    
    def customise_colour(self):
        self.colour_entry = tk.Entry(self.button_frame, width=30)
        self.colour_label = tk.Label(self.button_frame, text="Enter ball colour", bg="#99D9EA")
        self.colour_label2 = tk.Label(self.button_frame, text="press enter to save", bg="#99D9EA")
        self.colour_label.config(font=("Volleyball",12))
        self.colour_label2.config(font=("Volleyball",10))
        self.colour_entry.grid(row=4,padx=150,pady=10)
        self.colour_label.grid(row=3,padx=150,pady=10)
        self.colour_label2.grid(row=5,padx=150,pady=10)
        self.colour_bind = self.bind("<Return>", self.set_colour)
    
    def set_colour(self, event):
        self.unbind("<Return>", self.colour_bind)
        self.colour = self.colour_entry.get()
        self.colour_entry.destroy()
        self.colour_label.destroy()
        self.colour_label2.destroy()
        self.saved_colour_label = tk.Label(self.button_frame, text="Saved!", bg="#99D9EA")
        self.saved_colour_label.config(font=("Volleyball",10))
        self.saved_colour_label.grid(row=3,padx=150,pady=10)  

    def fill_leaderboard(self):
        file = open("scores.txt", "r")
        unsorted = []
        for line in file:
            record = line.split()
            if record[2] == "Completed":
                record[1] = int(record[1])
                unsorted.append(record)
        sorted_leaderboard = sorted(unsorted, key=lambda x: x[1])
        for i in range(len(sorted_leaderboard)):
            leaderboard_data = tk.Label(self.leaderboard_frame, text=sorted_leaderboard[i][0], bg="#99D9EA")
            leaderboard_data.config(font=("Volleyball",12))
            leaderboard_data.grid(row=i+1,padx=10,pady=10,sticky="W")
            leaderboard_data2 = tk.Label(self.leaderboard_frame, text=str(sorted_leaderboard[i][1]), bg="#99D9EA")
            leaderboard_data2.config(font=("Volleyball",12))
            leaderboard_data2.grid(row=i+1,column=1,padx=10,pady=10,sticky="W")
            if i >= 9:
                break # We dont want the leaderboard to be too big, only the top scores

    def load_game_message(self):
        self.load_entry = tk.Entry(self.button_frame, width=30)
        self.load_label = tk.Label(self.button_frame, text="Enter your name", bg="#99D9EA")
        self.load_label2 = tk.Label(self.button_frame, text="press enter to load your last saved game", bg="#99D9EA")
        self.load_label.config(font=("Volleyball",12))
        self.load_label2.config(font=("Volleyball",10))
        self.load_entry.grid(row=4,padx=150,pady=10)
        self.load_label.grid(row=3,padx=150,pady=10)
        self.load_label2.grid(row=5,padx=150,pady=10)
        self.load_bind = self.bind("<Return>", self.load_game)

    def load_game(self, event):
        self.unbind("<Return>", self.load_bind)
        self.name = self.load_entry.get()
        self.load_entry.destroy()
        self.load_label.destroy()
        self.load_label2.destroy()
        for line in reversed(open("scores.txt").readlines()): #Open the file in reversed order, to read the latest save in that name
            record = line.split()
            print(record[0],record[2])
            if record[0] == self.name and record[2] != "Completed":
                self.current_score = int(record[1])
                self.start_level = int(record[2])
                self.start_game()
                break
        try:
            tk.Label(self.button_frame, text="User not found", bg="#99D9EA").config(font=("Volleyball",12)).grid(row=3,padx=150,pady=10)
        except:
            pass



if __name__ == "__main__":
    Home()