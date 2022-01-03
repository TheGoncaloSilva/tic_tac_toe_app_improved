import kivy
import os, sys
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
from src.pages.common import Options_modals, analyze_moves
from src.pages.player import Player
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang.parser import global_idmap
from kivy import utils

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
    user_choice = ""
    all_btns_ids = [] # holds every button as an asset
    btns_ids = []
    turn = True
    player1 = Player()
    player2 = Player()
    winner = ''
    found_winner = False

    def build(self): # Construir o UI
        self.title = 'Tic Tac Toe' # Change the the name of the application window
        size_x = 960
        #size_y = 540
        size_y = 700
        Window.size = (size_x, size_y)
        Window.minimum_width, Window.minimum_height = (size_x, size_y)
        return Builder.load_file('main.kv')
    def on_start(self):
        """
        Function executed on app load
        """
        pass

    def change_screen(self, sc, way, mode=''):
        #if sc == 'home':
            #self.reset_net(mode)
        manager = self.root.ids.screen_manager
        manager.transition.duration = 0.5
        manager.transition.direction = way
        manager.current = sc

    """
        Function that runs the solo mode
    """
    def solo_engine():
        pass

    def show_options(self, mode, opt):
        pop = Options_modals(mode, app, opt)
        pop.open()

    def execute_show_options(self, mode, opt):
        Clock.schedule_once(lambda x: self.show_options(mode, opt), 0.5)

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
                btn.bind(on_release=self.make_play)
                box.add_widget(btn)
            net.box.add_widget(box)

    def make_play(self, asset):
        self.btns_ids.append(asset)
        if self.user_choice == 'x':
            unchecked = 'src/img/x_button.png'
            self.user_choice = 'o'
        elif self.user_choice == 'o':
            unchecked = 'src/img/o_button.png'
            self.user_choice = 'x'
        self.turn = not self.turn
        
        if asset.background_normal == '':
            asset.background_color = [1, 1, 1, 1]
            asset.background_normal = unchecked
            self.get_id(asset.text)
        else: pass
        """
        if (self.turn == False and self.mode == 'solo') and self.found_winner != True:
            self.computer_player()"""

    def get_id(self, member, get_num=False):
        ids = {'0-0': 0, '0-1': 1, '0-2': 2, '1-0': 3,
               '1-1': 4, '1-2': 5, '2-0': 6, '2-1': 7, '2-2': 8}
        if get_num == True:
            keys = list(ids.keys()) # prints 0-0, 0-1...
            values = list(ids.values()) # prints the integers 1, 2 ...
            index = values.index(member) # prints the index of a keys
            return keys[index]
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
        
        print(table) # Debugging
        return table

    # Closes the game 
    def game_ended(self, data):
        #score = Score(winner, app, mode)
        #Clock.schedule_once(lambda x: score.open(), 1)
        pass

if __name__ == "__main__":
    app = MyApp()
    app.run()