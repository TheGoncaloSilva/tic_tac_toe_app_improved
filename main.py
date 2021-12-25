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
from src.pages.common import Options_modals
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang.parser import global_idmap

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
    all_btns_ids = []
    btns_ids = []
    turn = True
    #player1 = TicTacToe()
    #player2 = TicTacToe()
    winner = ''
    found_winner = False

    def build(self): # Construir o UI
        self.title = 'Tic Tac Toe' # Change the the name of the application window
        size_x = 960
        size_y = 540
        Window.size = (size_x, size_y)
        Window.minimum_width, Window.minimum_height = (size_x, size_y)
        return Builder.load_file('main.kv')
    
    def on_start(self):
        """
        Function executud on app load
        """
        pass

    def change_screen(self, sc, way, mode=''):
        #if sc == 'home':
            #self.reset_net(mode)
        manager = self.root.ids.screen_manager
        manager.transition.duration = 0.5
        manager.transition.direction = way
        manager.current = sc

    def show_options(self, mode):
        pop = Options_modals(mode, app)
        pop.open()

    def execute_show_options(self, mode):
        Clock.schedule_once(lambda x: self.show_options(mode), 0.5)

    def draw_net(self, mode):
        self.mode = mode
        net = self.root.ids[mode].ids
        for i in range(3):
            box = BoxLayout(orientation='horizontal', spacing=5)
            for j in range(3):
                btn = Button(text=f'{i}-{j}', background_normal='', color=[0, 0, 0, 0],
                             background_down='', background_color=[1, 1, 1, 1])
                if not(btn in self.all_btns_ids):
                    self.all_btns_ids.append(btn)
                btn.bind(on_release=self.change_icon)
                box.add_widget(btn)
            net.box.add_widget(box)

if __name__ == "__main__":
    app = MyApp()
    app.run()