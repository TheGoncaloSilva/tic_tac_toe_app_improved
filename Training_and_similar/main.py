from typing import Text
import random
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout # Import GridLayout design
from kivy.uix.button import Button # import buttons
from kivy.uix.label import Label # Import the simbols and widgets
from kivy.uix.popup import Popup # Import Popups
from kivy.uix.boxlayout import BoxLayout # Box layout for Popup
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang.parser import global_idmap


class MainWindow(Screen): # Window for choosing the type of game
    pass

class OptionsWindow(Screen): # window for showing the computer dificulty levels
    pass            

class GameWindow(Screen): # game window (where the game occurs)
    pass    

class WindowManager(ScreenManager): # Transition between the windows
    pass

kv = Builder.load_file("my.kv") # Now the name of the kv file does not need to mathc the class name - App
sm = WindowManager()

screens = [MainWindow(name="main"), OptionsWindow(name="options"),GameWindow(name="game")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "main"

class MyApp(App):

    game_mode = [] # mode wich the game is supposed to be played
    table = []
    max_plays = 9 # number of maximum plays possible with the grid size
    player1 = "X" # Player 1 always exists
    player2 = "O" # Player 2 is a bot in single player mode and another player in multiplayer
    active_player = 0 # Currently active player
    winner = '' # wich player won the game (if null no one won)
    game_ended = False
# ****************************************


    def build(self):
        self.title = 'Tic Tac Toe' # Change the the name of the application window
        return sm
    
    # Reset the table values to 0
    def load_table(self):
        self.table = [[0, 0, 0], [0, 0, 0], [0, 0 , 0]] # no position is selected
        return self.table

    # player choose the multiplayer (1v1) mode, so load the game with this mode
    def load_multiplayer(self, mode): # update the game_mode to multiplayer
        self.game_mode = ['multiplayer', '']

        if self.active_player != 0:
            self.game_ended = True
            self.popup_manager(False, 'The game has ended! ', 'You exited the game, please restart to play again')
        else:
            self.clear_table()
            # call the popup to choose the avatar (the active player has already been randomized, so just need to choose)
    
    def load_solo_mode(self, difficulty): # update the game mode to single player and also it's difficulty
        self.game_mode = ['solo', difficulty]

        if self.active_player != 0: # if there is no active player
            self.game_ended = True # the game has ended
            self.popup_manager(False, 'The game has ended! ', 'You exited the game, please restart to play again')
        else:
            self.clear_table() # load the game
    
    # return the symbol or avatar of the current player
    def active_player_symbol(self):
        return self.player1 if self.active_player == 1 else self.player2 

    # save the players choosen position on the backend table
    def mark_pos(self, pos):
        if pos >= 0 and pos <= 8: # validate the choosen position
            if pos >= 0 and pos <= 2: # 1st row
                self.table[0][pos] = self.active_player_symbol()
            elif pos >= 3 and pos <= 5: # 2nd row
                pos -= 3
                self.table[1][pos] = self.active_player_symbol()
            else: # 3rd row
                pos -= 6
                self.table[2][pos] = self.active_player_symbol()
        else:
            self.popup_manager(False, 'OOPS! :(', 'An Error occurred trying to save your position. Please restart the game or try again later')

    # function called when a button is pressed
    # receives the labels to update with the player name and avatar
    # receives all the buttons to then provide them to the AI player if choosen (could be optimized)
    def choose_pos(self, asset, n, lbl_gamer, btn_gamer, *btns): # *btn allows to receive as much arguments as they come
        if not self.game_ended: # if the game did'nt end
            if asset.text == "":
                if self.player1 != "" and self.player2 != "":
                    self.mark_pos(n) # update table reference
                    if self.active_player % 2 == 0:
                        asset.text = self.player2
                        self.analyze_moves() # a move has been done, figure out if someone has won
                        self.active_player = 1
                    else: 
                        asset.text = self.player1
                        self.analyze_moves() # a move has been done, figure out if someone has won
                        self.active_player = 2
                    
                    # if the player is playing against the AI, choose according to it's difficulty
                    if self.game_mode[0] == 'solo' and self.active_player == 2 and not self.game_ended:
                        if self.game_mode[1] == 'easy':
                            self.easy_mode(*btns)
                        else:
                            self.ai_mode(*btns)

                        self.analyze_moves() # a move has been done, figure out if someone has won
                        self.active_player = 1
                    
                    # update the labels that show the player name and avatar
                    btn_gamer.text = self.active_player_symbol()
                    lbl_gamer.text = "Player 1" if self.active_player == 1 else "Player 2"

                else: # If the conditions aren't met, it will give a warning to the user
                    self.popup_manager(False, 'OOPS! :(', 'An Error occurred trying to register your position. Please restart the game or try again later')
        else:
            self.popup_manager(False, 'The game has ended! ', 'The game has already ended, please restart to play again')
    
    # Randomly choose the player to start the game
    def choose_player(self): 
        self.active_player = random.randrange(0, 2)

    # reset the buttons (not the most optimized way)
    def restart(self,lbl_gamer, btn_gamer,  *btn): # *btn allows to receive as much arguments as they come
        for btns in btn: # cycle through all the buttons
            btns.text = ""

        self.clear_table() # load the game (reset the variables)

        # reset the labels that show the player name and avatar
        btn_gamer.text = self.active_player_symbol()
        lbl_gamer.text = "Player 1" if self.active_player == 1 else "Player 2"

    def clear_table(self): # Reset the game
        self.table = self.load_table()
        if self.game_mode[0] == 'solo':
           self.active_player = 1
        else: 
            self.choose_player()
        self.game_ended = False
        self.winner = ''

    # AI easy mode
    # Chooses random values and checks if the spots are not taken,
    # if they are, it will recursively try to find a free spot
    def easy_mode(self, *btns):
        pos = random.randrange(0,9) # 0 to 8
        found = False
        btn_pos = pos
        
        if pos >= 0 and pos <= 2: # 1st row
            if self.table[0][pos] == 0:
                self.table[0][pos] = self.active_player_symbol()
                btns[btn_pos].text = self.active_player_symbol()
                found = True
        elif pos >= 3 and pos <= 5: # 2nd row
            pos -= 3
            if self.table[1][pos] == 0:
                self.table[1][pos] = self.active_player_symbol()
                btns[btn_pos].text = self.active_player_symbol()
                found = True
        elif pos >= 6 and pos <= 8: # 3rd row
            pos -= 6
            if self.table[2][pos] == 0:
                self.table[2][pos] = self.active_player_symbol()
                btns[btn_pos].text = self.active_player_symbol()
                found = True

        if not found:
            self.easy_mode(*btns) # recursive call

    # AI difficult mode
    def ai_mode(self, *btns):
        bestScore = float('-inf') # negative infinity
        move = []

        for l in range(3):
            for c in range(3):
                # Is the spot available?
                if (self.table[l][c] == 0):
                    self.table[l][c] = self.player2
                    score = self.minimax(0, False)
                    #score = 1
                    self.table[l][c] = 0
                    if score > bestScore :
                        bestScore = score
                        move = [l, c]

        self.table[move[0]][move[1]] = self.player2
        if move[0] == 0:
            btns[move[1]].text = self.player2
        elif move[0] == 1:
            btns[move[1] + 3].text = self.player2
        else :            
            btns[move[1] + 6].text = self.player2

        print(self.table)

    #         X, O , tie
    scores = { 'X': -1, 'O': 1, 'tie': 0}

    # Minimax AI function, to cycle all posibillities
    def minimax(self, depth, isMaximizing):
        result = self.ai_winner()
        
        if result != None:
            return self.scores[result]

        if isMaximizing :
            bestScore = float('-inf') # negative infinity
            for l in range(3):
                for c in range(3):
                    # Is the spot available?
                    if self.table[l][c] == 0 :
                        self.table[l][c] = self.player2 # AI
                        score = self.minimax(depth + 1, False) # call minimax recusively
                        self.table[l][c] = 0
                        bestScore = max(score, bestScore) # find the best spot

            return bestScore # return the best spot
        else :
            bestScore = float('inf') # negative infinity
            for l in range(3):
                for c in range(3):
                    # Is the spot available?
                    if self.table[l][c] == 0 :
                        self.table[l][c] = self.player1
                        score = self.minimax(depth + 1, True) # call minimax recusively
                        self.table[l][c] = 0
                        bestScore = min(score, bestScore) # find the best spot
                
            return bestScore # return the best spot

    def ai_winner(self):
        winner = None

        # horizontal
        for l in range(3):
            if (self.table[l][0] == self.table[l][1] == self.table[l][2]) and self.table[l][0] != 0:
                winner = self.table[l][0]

        # Vertical
        for c in range(3):
            if (self.table[0][c] == self.table[1][c] == self.table[2][c]) and self.table[0][c] != 0:
                winner = self.table[0][c]

        # Diagonal
        if (self.table[0][0] == self.table[1][1] == self.table[2][2]) and self.table[0][0] != 0:
            winner = self.table[0][0]
        
        if (self.table[2][0] == self.table[1][1] == self.table[0][2]) and self.table[2][0] != 0:
            winner = self.table[2][0]

        openSpots = 0
        for l in range(3):
                for c in range(3):
                    if (self.table[l][c] == 0):
                        openSpots += 1
            
        if (winner == None and openSpots == 0):
            return 'tie'
        else:
            return winner
        
    # AI difficult mode, anothe implementation, based on strategies (pending)
    def difficult_mode(self, *btns):
        strategies = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                      [0, 3, 6], [1, 4, 7], [2, 5, 8],
                      [0, 4, 8], [2, 4, 6]]

        best_pos = -1
        biggest_match = 0
        match = 0
        temp_pos = None
        i = 0

        for case in strategies:
            if match > biggest_match :
                biggest_match = match
            match = 0
            for pos in case:
                i += 1
                if pos >= 0 and pos <= 2: # 1st row
                    if self.table[0][pos] == 'O':
                        match += 1
                    elif self.table[0][pos] == 0:
                        temp_pos = pos
                elif pos >= 3 and pos <= 5: # 2nd row
                    pos -= 3
                    if self.table[1][pos] == 'O':
                        match += 1
                    elif self.table[1][pos] == 0:
                        temp_pos = pos
                else: # 3rd row
                    pos -= 6
                    if self.table[2][pos] == 'O':
                        match += 1
                    elif self.table[2][pos] == 0:
                        temp_pos = pos
            
            if (match >= 2 or best_pos == -1) and temp_pos != None:
                best_pos = temp_pos
                print("---/--- " + str(i))
                print(best_pos)
                print(match)
        
        # if there is no availale strategie, chose a random spot
        if biggest_match <= 1:
            return self.easy_mode(*btns) # choose random spot

        pos = best_pos
        if pos >= 0 and pos <= 2: # 1st row
            if self.table[0][pos] == 0:
                self.table[0][pos] = self.active_player_symbol()
                btns[best_pos].text = self.active_player_symbol()
        elif pos >= 3 and pos <= 5: # 2nd row
            pos -= 3
            if self.table[1][pos] == 0:
                self.table[1][pos] = self.active_player_symbol()
                btns[best_pos].text = self.active_player_symbol()
        elif pos >= 6 and pos <= 8: # 3rd row
            pos -= 6
            if self.table[2][pos] == 0:
                self.table[2][pos] = self.active_player_symbol()
                btns[best_pos].text = self.active_player_symbol()

    # analyze the board and end the game if there is a winner of if the game results in a tie
    def analyze_moves(self):
        winners = self.analyze_winner(self.table)
        if winners[0]: # discover if a winner exists
            self.winner = winners[1]
            winner_name = 'Player 1' if self.winner == 1 else 'Player2'
            loser_name = 'Player 1' if self.winner == 2 else 'Player 2'
            self.game_ended = True
            self.popup_manager(True, 'Congratulations ' + winner_name + ' ! ',
                             'Well done ' + winner_name + '! You have managed to snag a win out of ' +
                               loser_name + ' using the mighty ' + self.active_player_symbol())
        else:
            # find if the number of marked spots is equal to the max number of defined plays
            # would be better to count the amount of unmarked spots
            if self.count_plays() == self.max_plays: 
                self.game_ended = True
                self.popup_manager(True, 'We have managed to get a draw! ', 
                'Neither one of the players has achieved to win, both can do better next time!')


    # Function for dicovering the winner
    def analyze_winner(self, board):
        # all strategies possible
        strategies = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                      [0, 3, 6], [1, 4, 7], [2, 5, 8],
                      [0, 4, 8], [2, 4, 6]]
        
        for case in strategies:
            match = 0
            for pos in case:
                if pos >= 0 and pos <= 2: # 1st row
                    if board[0][pos] == self.active_player_symbol():
                        match += 1
                elif pos >= 3 and pos <= 5: # 2nd row
                    pos -= 3
                    if board[1][pos] == self.active_player_symbol():
                        match += 1
                else: # 3rd row
                    pos -= 6
                    if board[2][pos] == self.active_player_symbol():
                        match += 1
            
            if match == 3:
                return[True, self.active_player]

        return [False, 1]

    # Sum the moves made by the two players
    def count_plays(self):
        result = 0

        for row in range(len(self.table)):
            for column in range(len(self.table)):
                if self.table[row][column] != 0:
                    result += 1

        return result

    # Flexible way of showing Popups, parameters:
    #   - self...
    #   - status of the message -> True or False and act accordingly
    #   - Title given to the Popup
    #   - The Message itself
    def popup_manager(self, status, title, message):
        boxl = BoxLayout(orientation="vertical")
        boxl2 =BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        pop = Popup(title=title, content=boxl, size_hint=(0.5,0.7))
        document = Label(text=message,markup=True, valign='top')
        button = Button(text='Dismiss', size_hint_y=None, height=40)
        button.bind(on_press=(lambda x:pop.dismiss()))
        boxl.add_widget(document)
        boxl2.add_widget(button)
        boxl.add_widget(boxl2)
        document.bind(size=document.setter('text_size'))
        pop.open() # Open the Popup

if __name__ == "__main__":
    MyApp().run()
