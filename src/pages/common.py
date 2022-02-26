# 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy import utils

class Options_modals(Popup):
    def __init__(self, mode, app, opt, **kwargs):
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
            self.input = input()
            self.save_btn = Button(text="SAVE", background_normal='', background_color=[255, 215, 0, 1], color=[
                                0, 0, 0, 1], font_size="18sp", bold=True, pos_hint={'center_x': .5, "y": .03}, size_hint=[.9, .15])
            # callbacks
            self.save_btn.bind(on_release=lambda x: self.start_game())
            # positioning widgets on the popup
            #self.box.add_widget(self.inf_label)
            self.box.add_widget(self.input)
            self.float = FloatLayout()
            self.float.add_widget(self.box)
            self.float.add_widget(self.save_btn)
            self.add_widget(self.float)

        elif opt == 'settings':
            pass

        elif opt == 'difficulty':
            pass

        elif opt == 'winner':
            pass

        else: # error found
            pass

    def colorize(self, symbol):
        if symbol == "x":
            self.x_btn.background_color = utils.get_color_from_hex("#847878")
            self.o_btn.background_color = utils.get_color_from_hex("#f60261")
            self.o_btn.color=[1, 1, 1, 1]
        elif symbol == "o":
            self.o_btn.background_color = utils.get_color_from_hex("#847878")
            self.x_btn.background_color = utils.get_color_from_hex("#00ebea")
            self.x_btn.color = [0, 0, 0, 1]
        self.app.user_choice = symbol

    def start_game(self):
        if self.app.user_choice != "":
            self.app.reset_screen(self.mode)
            self.dismiss()

    def save_name(self):
        #self.app.player1.player_name = ""
        pass

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