import math, kivy, os, sys, random, time
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout # Import GridLayout design
from kivy.uix.button import Button # import buttons
from kivy.uix.label import Label # Import the simbols and widgets
from kivy.uix.popup import Popup # Import Popups
from kivy.uix.boxlayout import BoxLayout # Box layout for Popup
from kivy.modules import inspector
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang.parser import global_idmap
from kivy import utils
from src.pages.common import Options_modals, analyze_moves
from src.pages.solo import ai_mode,minimax,set_scores, easy_mode
from src.pages.player import Player
import src.pages.db_control as db

class Home(Screen):
    pass

class Soloplayer(Screen):
    pass

class Multiplayer(Screen):
    pass

class Lan(Screen):
    pass

class MyApp(App):
    mode = ""
    active_player = ""
    all_btns_ids = [] # holds every button as an asset
    btns_ids = []
    turn = True # True = player1 and False = player2 playing
    player1 = Player()
    player2 = Player()
    winner = ''
    found_winner = False
    difficulty = 0

    def build(self): # Construir o UI
        self.title = 'Tic Tac Toe' # Change the the name of the application window
        size_x = 960
        #size_y = 540
        size_y = 700
        Window.size = (size_x, size_y)
        Window.minimum_width, Window.minimum_height = (size_x, size_y)
        inspector.create_inspector(Window, self) # Debug
        return Builder.load_file('main.kv')
        
    def on_start(self):
        """
        Function executed on app load
        """
        pass

    def change_screen(self, sc, way):
        #if sc == 'home':
        #    self.reset_net(mode)
        manager = self.root.ids.screen_manager
        manager.transition.duration = 0.5
        manager.transition.direction = way
        manager.current = sc

    def update_info(self):
        if self.mode == 'solo':
            grid = self.root.ids['solo'].ids
            grid.btn_gamer.text = self.active_player
            if self.active_player == self.player1.player_avatar:
                grid.lbl_current.text = f"[b]Playing:[/b] {self.player1.player_name}"
            elif self.active_player == self.player2.player_avatar:
                grid.lbl_current.text = f"[b]Playing:[/b] {self.player2.player_name}"

    """
        Function that runs the solo mode
    """
    def solo_engine():
        pass

    def show_options(self, mode, opt, args):
        pop = Options_modals(mode, app, opt, args)
        pop.open()

    def execute_show_options(self, mode, opt, args):
        Clock.schedule_once(lambda x: self.show_options(mode, opt, args), 0.5)

    def player_names(self, mode):
        if mode == 'solo':
            self.execute_show_options(mode, 'name', 'player1')
            self.player2.player_name = 'BOT'
        elif mode == 'poly':
            pass # change

    # reset the page values
    def reset_screen(self, mode):
        if mode == 'solo': 
            self.execute_show_options("solo", 'difficulty', '')
            self.execute_show_options("solo", 'avatar', '')

        self.remove_net()
        # check if there are already objects before creating
        self.draw_net(mode)
        self.found_winner = False
        self.winner = ''
        self.turn = bool(random.getrandbits(1))    

    def start_game(self):
        if self.turn:
            self.active_player = self.player1.player_avatar
            self.update_info()
        elif not self.turn:
            self.active_player = self.player2.player_avatar
            self.update_info()
        if not self.turn:
            self.computer_player()

    def draw_net(self, mode):
        self.mode = mode
        net = self.root.ids[mode].ids
        for i in range(3):
            box = BoxLayout(orientation='horizontal', spacing=5)
            for j in range(3):
                btn = Button(text=f'{i}-{j}', background_normal='', color=[0, 0, 0, 0],
                             background_down='', background_color=utils.get_color_from_hex("#fdcb01"))
                if not(btn in self.all_btns_ids):
                    self.all_btns_ids.append(btn)
                btn.bind(on_release=self.player_play)
                box.add_widget(btn)
            net.box.add_widget(box)
    
    def remove_net(self):
        if len(self.all_btns_ids) != 0:
            #net = self.root.ids['solo'].ids #, self.root.ids['poly'].ids, self.root.ids['lan'].ids]
            #net.box.clear_widgets() # deletes all widgets in the table
            nets = [self.root.ids['solo'].ids, self.root.ids['poly'].ids, self.root.ids['lan'].ids]
            for screen in nets:
                if screen != {}: screen.box.clear_widgets() # deletes all widgets in the table
            self.all_btns_ids.clear()

    def make_play(self, asset):
        self.btns_ids.append(asset)
        if self.active_player == 'x':
            unchecked = 'src/img/x_button.png'
            self.active_player = 'o'
        elif self.active_player == 'o':
            unchecked = 'src/img/o_button.png'
            self.active_player = 'x'
        self.turn = not self.turn
        
        if asset.background_normal == '':
            asset.background_color = [1, 1, 1, 1]
            asset.background_normal = unchecked
            self.get_id(asset.text)
        else: pass
        self.update_info()

    def player_play(self, asset):
        if asset.background_normal == '' and not self.found_winner:
            self.make_play(asset)
            if (not self.turn and self.mode == 'solo') and  not self.found_winner:
                Clock.schedule_once(lambda x: self.computer_player(), 0.5) # make AI play and add delay

    def computer_player(self):
        if self.mode != 'solo': return
        self.update_info()
        avatars = [self.player1.player_avatar, self.player2.player_avatar]
        set_scores(avatars)
        rng = random.randint(0,self.difficulty)
        spot = []
        if rng == 0:
            spot = ai_mode(self.matrix_array(), avatars)
        else: spot = easy_mode(self.matrix_array())

        if spot == None:
            pass # SHOW A ERROR ON THE SCREEN

        btn = self.get_id(f"{spot[0]}-{spot[1]}", True)
        self.make_play(btn)

    def get_id(self, member, get_num=False):
        ids = {'0-0': 0, '0-1': 1, '0-2': 2, '1-0': 3,
               '1-1': 4, '1-2': 5, '2-0': 6, '2-1': 7, '2-2': 8}
        if get_num:
            #keys = list(ids.keys()) # prints 0-0, 0-1...
            #values = list(ids.values()) # prints the integers 1, 2 ...
            #index = values.index(member) # prints the index of a keys
            return self.all_btns_ids[ids[member]]
        else:
            res = analyze_moves(self.table_array())
            if res != None:
                self.game_ended(res)
            #self.check_win(ids[member])

    # Returns an array containing the positions and values of the table
    def table_array(self):
        table = []

        for idd in self.all_btns_ids:
            if idd.background_normal == 'src/img/x_button.png':
                table.append('x')
            elif idd.background_normal == 'src/img/o_button.png':
                table.append('o')
            else:
                table.append(' ')
        
        # print(table) # DEBUG
        return table
    
    def matrix_array(self):
        table = self.table_array()
        matrix = []
        line_col_size = int(math.sqrt(len(table)))
        pos = -3
        for line in range(line_col_size):
            pos = pos + 3
            line = []
            for col in range(line_col_size):
                if table[pos+col] == ' ':
                    line.append(0)
                else: 
                    line.append(table[pos+col])
            matrix.append(line)
        
        # print(matrix) DEBUG
        return matrix

    # Closes the game 
    def game_ended(self, data):
        self.found_winner = True
        if data[0] == 'winner':
            self.winner = data[1]
        self.execute_show_options(self.mode, 'winner', '')
        #score = Score(winner, app, mode)
        #Clock.schedule_once(lambda x: score.open(), 1)
        pass

    def save_db(self, data):
        conn = db.create_connection("./src/GameResults.db")
        pass

if __name__ == "__main__":
    app = MyApp()
    app.run()