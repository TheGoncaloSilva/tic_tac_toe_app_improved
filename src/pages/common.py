# 
from typing import Text
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy import utils

class Options_modals(Popup):
    def __init__(self, mode, app, opt, extra, **kwargs):
        super(Options_modals, self).__init__(**kwargs)
        self.mode = mode
        self.app = app
        self.size_hint = [None, None]
        self.pos_hint = {'center_x': 0.5, "top": .7}
        self.height = 250
        self.width = 310
        self.auto_dismiss = False
        self.background_color =  utils.get_color_from_hex("#250448")
        if opt == 'avatar':
            # title
            self.title = "choose your symbol".upper()
            self.title_size = '16sp'
            self.title_color = [1, 1, 1, 1]
            # separator
            self.separator_color = [1, 1, 1, 1]
            self.separator_height: 10
            # content
            self.box = BoxLayout(size_hint_y=.7, padding=10, spacing=10, pos_hint={
                                'top': .99, 'center_x': .5}, orientation='horizontal')
            self.x_btn = Button(text="X", background_normal='', background_down='', background_color= 
                                utils.get_color_from_hex("#00ebea"), color=[0, 0, 0, 1], font_size="70sp", bold=True)
            self.o_btn = Button(text="O", background_normal='', background_down='', background_color=
                                utils.get_color_from_hex("#f60261"), color=[1, 1, 1, 1], font_size="70sp", bold=True)
            self.save_btn = Button(text="SAVE", background_normal='', background_color=[255, 215, 0, 1], color=[
                                0, 0, 0, 1], font_size="18sp", bold=True, pos_hint={'center_x': .5, "y": .03}, size_hint=[.9, .15])
            # callbacks
            self.x_btn.bind(on_release=lambda x: self.colorize('x'))
            self.o_btn.bind(on_release=lambda x: self.colorize('o'))
            self.save_btn.bind(on_release=lambda x: self.start_game())
            # positioning widgets on the popup
            self.box.add_widget(self.x_btn)
            self.box.add_widget(self.o_btn)
            self.float = FloatLayout()
            self.float.add_widget(self.box)
            self.float.add_widget(self.save_btn)
            self.add_widget(self.float)
        
        elif opt == 'name':  
            # title
            self.title = "what's your name?".upper()
            self.title_size = '16sp'
            self.title_color = [1, 1, 1, 1]
            # separator
            self.separator_color = [1, 1, 1, 1]
            self.separator_height: 10
            # content
            self.box = BoxLayout(size_hint_y=.7, padding=10, spacing=10, pos_hint={
                                'top': .99, 'center_x': .5}, orientation='horizontal')
            #self.inf_label = Label(text="x: ", font_size="70sp", bold=True)
            self.t_input = TextInput(multiline = False, hint_text = f'Enter {extra} name') #### dont forget to sanitize inputs
            self.save_btn = Button(text="SAVE", background_normal='', background_color=[255, 215, 0, 1], color=[
                                0, 0, 0, 1], font_size="18sp", bold=True, pos_hint={'center_x': .5, "y": .03}, size_hint=[.9, .15])
            # callbacks
            self.save_btn.bind(on_release=lambda x: self.save_name(self.t_input, extra))
            # positioning widgets on the popup
            self.box.add_widget(self.t_input)
            self.float = FloatLayout()
            self.float.add_widget(self.box)
            self.float.add_widget(self.save_btn)
            self.add_widget(self.float)

        elif opt == 'settings':
            pass

        elif opt == 'difficulty':
            #self.height = 250
            #self.width = 400
            # title
            self.title = "Difficulty level".upper()
            self.title_size = '16sp'
            self.title_color = [1, 1, 1, 1]
            # separator
            self.separator_color = [1, 1, 1, 1]
            self.separator_height: 10
            # content
            self.box = BoxLayout(size_hint_y=.7, padding=5, spacing=5, pos_hint={
                                'top': .99, 'center_x': .5}, orientation='vertical')
            self.easy = Button(text="easy", background_normal='', background_down='', background_color= 
                                utils.get_color_from_hex("#07fc03"), color=[0, 0, 0, 1], font_size="20sp")
            self.medium = Button(text="medium", background_normal='', background_down='', background_color=
                                utils.get_color_from_hex("#ffd900"), color=[0, 0, 0, 1], font_size="20sp")
            self.hard = Button(text="hard", background_normal='', background_down='', background_color=
                                    utils.get_color_from_hex("#ff1e00"), color=[0, 0, 0, 1], font_size="20sp")
            # callbacks
            self.easy.bind(on_release=lambda x: self.difficulty(2))
            self.medium.bind(on_release=lambda x: self.difficulty(1))
            self.hard.bind(on_release=lambda x: self.difficulty(0))
            # positioning widgets on the popup
            self.box.add_widget(self.easy)
            self.box.add_widget(self.medium)
            self.box.add_widget(self.hard)
            self.float = FloatLayout()
            self.float.add_widget(self.box)
            self.add_widget(self.float)

        elif opt == 'winner':
            # title
            self.title = "game ended!".upper()
            self.title_size = '16sp'
            self.title_color = [1, 1, 1, 1]
            # separator
            self.separator_color = [1, 1, 1, 1]
            self.separator_height: 10
            # content
            self.box = BoxLayout(size_hint_y = .3,
                    padding = 10, 
                    spacing = 10, 
                    pos_hint = {'top': .99, 'center_x': .5}, 
                    orientation = 'horizontal', 
                    height = 40)
                    
            if self.app.found_winner and self.app.winner != '': # winner exists
                if self.app.mode == 'solo' and self.app.winner == self.app.player1.player_avatar:
                    self.title = "Congratulatins".upper()
                    self.info = Label(text = f"{self.app.player1.player_name} won the game", 
                                color = [1, 1, 1, 1], 
                                bold = True,
                                markup = True)
                elif self.app.mode == 'solo' and self.app.winner == self.app.player2.player_avatar:
                    self.info = Label(text = f"{self.app.player2.player_name} has won the game", 
                                color = [1, 1, 1, 1], 
                                bold = True,
                                markup = True)

            elif self.app.found_winner: # tie
                self.info = Label(text = "The game ended with a TIE.", 
                                color = [1, 1, 1, 1], 
                                bold = True,
                                markup = True)

            self.save_btn = Button(text="Restart", background_normal='', background_color=[255, 215, 0, 1], color=[
                            0, 0, 0, 1], font_size="18sp", bold=True, pos_hint={'center_x': .5, "y": .03}, size_hint=[.9, .15])
            # callbacks
            self.save_btn.bind(on_release=lambda x: self.reset_game())
            # positioning widgets on the popup
            self.box.add_widget(self.info)
            self.float = FloatLayout()
            self.float.add_widget(self.box)
            self.float.add_widget(self.save_btn)
            self.add_widget(self.float)

        else: # error found
            pass

    def colorize(self, symbol):
        if symbol == "x":
            self.x_btn.background_color = utils.get_color_from_hex("#847878")
            self.o_btn.background_color = utils.get_color_from_hex("#f60261")
            self.o_btn.color=[1, 1, 1, 1]
            self.app.player1.player_avatar = 'x'
            self.app.player2.player_avatar = 'o'
        elif symbol == "o":
            self.o_btn.background_color = utils.get_color_from_hex("#847878")
            self.x_btn.background_color = utils.get_color_from_hex("#00ebea")
            self.x_btn.color = [0, 0, 0, 1]
            self.app.player1.player_avatar = 'o'
            self.app.player2.player_avatar = 'x'
        self.app.active_player = symbol
    
    def difficulty(self, value):
        self.app.difficulty = value
        self.app.start_game()
        self.dismiss()

    def reset_game(self):
        self.app.reset_screen(self.mode)
        self.dismiss()

    def start_game(self):
        if self.app.active_player != "":
            #self.app.reset_screen(self.mode)
            self.dismiss()

    def save_name(self, asset, player):
        max_size = 10
        if player == "player1":
            self.app.player1.player_name = asset.text[:max_size]
        else: 
            self.app.player2.player_name = asset.text[:max_size]
        self.dismiss()
        

# Evaluate each move made
def analyze_moves(board):
    result = analyze_winner(board)
    if result[0]:
        return ['winner', result[1]]

    for x in board:
         if x == ' ': return # if empty spaces, game continues

    return ['tie'] # no empty spaces or winners

# Function for dicovering the winner
def analyze_winner(board):
    # all strategies possible
    strategies = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                  [0, 3, 6], [1, 4, 7], [2, 5, 8],
                  [0, 4, 8], [2, 4, 6]]

    for player in ['x','o']:    
        for case in strategies:
            match = 0
            for pos in case:
                if board[pos] == player:
                    match += 1

            if match == 3:
                return [True, player]

    return [False, 1]