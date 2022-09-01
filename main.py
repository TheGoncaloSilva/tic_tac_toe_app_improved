from cgi import test
from http import server
import math, kivy, os, sys, random, time, datetime, threading, functools
from xmlrpc.client import Server
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
import src.client_server.clientTCP as client
import src.client_server.serverTCP as server

class Home(Screen):
    pass

class Soloplayer(Screen):
    pass

class Multiplayer(Screen):
    pass

class Options(Screen):
    input_ip = ObjectProperty(None)
    input_port = ObjectProperty(None)
    input_password = ObjectProperty(None)
    input_encryption = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
    
    # Function to reset the password field if the encryption button is pressed
    def check_press(self):
        if not self.input_encryption.active:
            self.input_password.text = ""

    # Function to get the Inputs size and cut the excessive
    def insert_text(self, input, size):
        if len(input.text) > size:
            input.text = input.text[:size]
    
    # Function to not let introduce characters in number inputs
    def insert_number(self, input, size):
        try:
            if int(input.text) > size:
                input.text = size
            elif int(input.text) <= 0:
                input.text = "1"
        except:
            input.text = input.text[:len(input.text)-1]

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
    temp_player = ''
    winner = ''
    found_winner = False
    difficulty = 0
    can_play = True
    lan_enc = ''
    lan_passw = ''
    server_handler = ''
    connection_mode = '' # client or server
    start = ''

    def build(self): # Construir o UI
        self.title = 'Tic Tac Toe' # Change the the name of the application window
        size_x = 960
        #size_y = 540
        size_y = 700
        Window.size = (size_x, size_y)
        Window.minimum_width, Window.minimum_height = (size_x, size_y)
        inspector.create_inspector(Window, self) # Debug (ctrl + 'e')
        return Builder.load_file('main.kv')

    def change_screen(self, sc, way):
        #if sc == 'home':
        #    self.reset_net(mode)
        manager = self.root.ids.screen_manager
        manager.transition.duration = 0.5
        manager.transition.direction = way
        manager.current = sc

    def update_info(self):
        grid = self.root.ids[self.mode].ids
        grid.btn_gamer.text = self.active_player
        if self.active_player == self.player1.player_avatar:
            grid.lbl_current.text = f"[b]Playing:[/b] {self.player1.player_name}"
        elif self.active_player == self.player2.player_avatar:
            grid.lbl_current.text = f"[b]Playing:[/b] {self.player2.player_name}"

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
            self.execute_show_options(mode, 'name', 'player2') # Last popup appears first
            self.execute_show_options(mode, 'name', 'player1') # Last popup appears first

    # reset the page values
    def reset_screen(self, mode):
        self.found_winner = False
        self.winner = ''
        if self.connection_mode != 'client':
            self.turn = bool(random.getrandbits(1))
        
        if mode == 'solo': 
            self.execute_show_options("solo", 'difficulty', '')
            self.execute_show_options("solo", 'avatar', '')
        elif mode == 'poly':
            if self.turn: # player1
                self.execute_show_options("poly", 'avatar', 'player1')
            else: # player2
                self.execute_show_options("poly", 'avatar', 'player2')
        elif mode == 'lan' and self.connection_mode == 'server':
            if self.turn: # player1
                server.queue_server_data({'op' : 'game', 'data' : 'turn', 'player' : 'player1'})
                self.execute_show_options("lan", 'avatar', 'player1')
                #server.queue_server_data({'op' : 'game', 'data' : 'avatar', 'avatar' : self.player1.player_avatar})
                self.can_play = True
            else: # client player
                server.queue_server_data({'op' : 'game', 'data' : 'turn', 'player' : 'player2'})
                self.can_play = False
        elif mode == 'lan' and self.connection_mode == 'client' and self.player1.player_avatar == "" and self.player2.player_avatar == "":  # 1st config
            if not self.turn: #player2
                self.execute_show_options("lan", 'avatar', 'player2')
                #client.queue_Client_data({'op' : 'game', 'data' : 'avatar', 'avatar' : self.player2.player_avatar})
                self.can_play = True


        self.remove_net()
        # check if there are already objects before creating
        self.draw_net(mode)
        self.update_scoreboard()

    def start_game(self):
        if self.mode != "lan":
            if self.turn:
                self.active_player = self.player1.player_avatar
                self.update_info()
            elif not self.turn:
                self.active_player = self.player2.player_avatar
                self.update_info()

            self.save_playersDB() # UNCOMMENT TO SAVE RECORDS IN DB

            if not self.turn and self.mode == 'solo':
                self.computer_player()
        else:
            if self.turn: # player 1
                self.active_player = self.player1.player_avatar
                server.queue_server_data({'op' : 'game', 'data' : 'avatar', 'avatar' : self.player1.player_avatar})
                self.update_info()
            elif not self.turn: # player 2
                self.active_player = self.player2.player_avatar
                client.queue_Client_data({'op' : 'game', 'data' : 'avatar', 'avatar' : self.player2.player_avatar})
                self.update_info()

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
            nets = [self.root.ids['solo'].ids, self.root.ids['poly'].ids] # add , self.root.ids['lan'].ids
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
        if asset.background_normal == '' and not self.found_winner and self.can_play:
            self.make_play(asset)
            if not self.turn and self.mode == 'solo' and not self.found_winner:
                self.can_play = False
                Clock.schedule_once(lambda x: self.computer_player(), 0.5) # make AI play and add delay
            if not self.turn and self.mode == 'lan' and not self.found_winner:
                self.can_play = not self.can_play
                ids = {'0-0': 0, '0-1': 1, '0-2': 2, '1-0': 3,
                       '1-1': 4, '1-2': 5, '2-0': 6, '2-1': 7, '2-2': 8}
                if self.connection_mode == 'client':
                    client.queue_Client_data({'op' : 'game', 'data' : 'update', 'position' : f'{ids[asset.text]}'}) #send choosen spot
                if self.connection_mode == 'server':
                    server.queue_server_data({'op' : 'game', 'data' : 'update', 'position' : f'{ids[asset.text]}'}) #send choosen spot

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
        self.can_play = True

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
        self.save_gameDB() # UNCOMMENT TO SAVE RESULTS IN DB
        self.update_scoreboard()

    def save_gameDB(self):
        """
        Save the game result in the database
        :param self: @MyApp object
        :return: True if successfull
        """
        conn = db.create_connection("./src/pages/GameResults.db")
        mode_id = db.getData_fromDB(conn, 'gameMode', ['id'], f"WHERE name = '{self.mode}' ")
        if not mode_id:
            return mode_id
        mode_id = mode_id[0][0]

        tS = datetime.datetime.now()
        if self.found_winner and self.winner == '': # tie
            win1 = 0
            win2 = 0
        elif self.found_winner and self.winner == self.player1.player_avatar: # player1 won
            win1 = 1
            win2 = -1
        else: # player2 won
            win1 = -1
            win2 = 1

        p1_id = db.getData_fromDB(conn, 'player', ['id'], f"WHERE name = '{self.player1.player_name}' ")
        if not p1_id:
            return p1_id
            
        p1_id = p1_id[0][0]
        query = db.insert_stats(conn, [win1, str(tS) , mode_id, p1_id])
        if not query:
            print(query)
            return query

        p2_id = db.getData_fromDB(conn, 'player', ['id'], f"WHERE name = '{self.player2.player_name}' ")
        if not p2_id:
            return p2_id

        p2_id = p2_id[0][0]
        query = db.insert_stats(conn, [win2, str(tS) , mode_id, p2_id])
        if not query:
            print(query)
            return query

        conn.close()
        return True

    def save_playersDB(self):
        """
        Check and Create, if needed, both players in the database
        :param self: @MyApp object
        :return:
        """
        conn = db.create_connection("./src/pages/GameResults.db")
        db.prepare_db(conn)
        if db.getData_fromDB(conn, 'player', ['id'], f"WHERE name = '{self.player1.player_name}' ") == []:
            db.insert_player(conn, self.player1.player_name)
        if db.getData_fromDB(conn, 'player', ['id'], f"WHERE name = '{self.player2.player_name}' ") == []:
            db.insert_player(conn, self.player2.player_name) 
        conn.close()

    def update_scoreboard(self):
        net = self.root.ids[self.mode].ids
        net.scoreboard_box.clear_widgets() # deletes all widgets inside scoreboard_box
        # Get the scoreboard data

        conn = db.create_connection("./src/pages/GameResults.db")
        db.prepare_db(conn)
        players = db.getData_fromDB(conn, 'player', ['*'], "")
        gameModes = db.getData_fromDB(conn, 'gameMode', ['*'], f"WHERE name = '{self.mode}'")
        stats = db.getData_fromDB(conn, 'stats', ['*'], f"WHERE gameMode = '{gameModes[0][0]}'") # id, result, tS, gameMode, player_id
        conn.close()

        results = []
        for st_line in stats:
            found = False
            for i, line in enumerate(results):
                if st_line[4] == line[0]:
                    line[1] = line[1] + st_line[1]
                    found = True
            if not found:
                results.append([st_line[4], st_line[1]])

        for res in results:
            name = ""
            for player in players:
                if res[0] == player[0]:
                    name = player[1]
            res[0] = name
        
        results.sort(reverse=True, key=self.order_funct)
        # Columm identifiers
        if len(results) == 0:
            lbl = Label(text = "No data", bold = True, font_size="19sp")
            net.scoreboard_box.add_widget(lbl)
            return
        lbl_player = Label(text = "Player", bold = True, font_size="19sp")
        lbl_result = Label(text = "Game Result", bold = True, font_size="19sp")
        net.scoreboard_box.add_widget(lbl_player)
        net.scoreboard_box.add_widget(lbl_result)

        # Add the best 3 to the Scoreboard
        for i in range(len(results)):
            if i >= 3: break # max number of results to show
            lbl_player = Label(text = str(results[i][0]), font_size="17sp")
            lbl_result = Label(text = str(results[i][1]), font_size="17sp")
            net.scoreboard_box.add_widget(lbl_player)
            net.scoreboard_box.add_widget(lbl_result)

    def order_funct(self, e):
        return e[1]


    ################### Server ###################

    def setup_lan(self, mode):
        self.execute_show_options(mode, 'name', 'temp')
        self.change_screen('options', 'left')
        # VERIFY IF SERVER IS RUNNING - IF its, stop it

    def lock_inputs(self, ip, port, enc, passw, create, connect, start):
        #disable inputs and buttons create and connect;
        # change opacity of connect button and start button
        ip.disabled = not ip.disabled
        port.disabled = not port.disabled
        enc.disabled = not enc.disabled
        passw.disabled = not passw.disabled
        if create.disabled == True and create.opacity == 0.0:
            create.disabled = False
            create.opacity = 1.0
            start.disabled = True
            start.opacity = 0.0
        else:
            create.disabled = True
            create.opacity = 0.0
            start.disabled = False
            start.opacity = 1.0
        
        if connect.disabled == True and connect.opacity == 0.0:
            connect.disabled = False
            connect.opacity = 1.0
            connect.size_hint = [.9, .15]
        else:
            connect.disabled = True
            connect.opacity = 0.0
            connect.size_hint = [0, 0]

        if self.connection_mode == 'client':
            start.disabled = False
            start.opacity = 0.0
        

    def update_players_lan(self):
        box = self.root.ids['options'].ids
        box.box_active_players.clear_widgets()

        if self.connection_mode == 'client':
            box.box_active_players.add_widget(Label(text=self.player1.player_name))
            box.box_active_players.add_widget(Label(text=f'{self.player1.player_ip}:{self.player1.player_port}'))
            box.box_active_players.add_widget(Label(text=self.player2.player_name + ' (me)'))
            box.box_active_players.add_widget(Label(text=f'{self.player2.player_ip}:{self.player2.player_port}'))
        else:
            box.box_active_players.add_widget(Label(text=self.player1.player_name + ' (me)'))
            box.box_active_players.add_widget(Label(text=f'{self.player1.player_ip}:{self.player1.player_port}'))
            box.box_active_players.add_widget(Label(text=self.player2.player_name))
            box.box_active_players.add_widget(Label(text=f'{self.player2.player_ip}:{self.player2.player_port}'))

    def check_inputs(self, values):
        # when create_server clicked, check if the inputs have data
        # if not popup warning
        for input in values:
            if input.text == '':
                self.execute_show_options(self.mode, 'warning', '')
                return False
        return True

    def cache_data(self, ip, port):
        # if a server is successfully created, save those inputs in a file, so that it will be easier next
        # time to create another server
        with open("src/Cached_lan.txt", "w") as f:
            f.write(f"{ip}; {port};")

    def initiate_server(self, ip, port, enc, passw):
        if server.test_connection(ip, int(port)):
            self.server_handler = threading.Thread(
                                target=server.initiate_server,args=(ip,
                                                                    port,
                                                                    enc,
                                                                    passw),
                                                                    daemon=True)
            self.server_handler.start()
            return True
        return False
    
    def create_server(self, ip, port, enc, passw, create, connect, start):
        if self.check_inputs([ip, port]) == False:
            return print(False)

        self.connection_mode = 'server'
        self.player1.player_name = self.temp_player
        self.player1.player_ip = ip.text
        self.player1.player_port = int(port.text)

        if enc.active:
            self.lan_enc = os.urandom(16)
        else:
            self.lan_enc = ''

        self.lan_passw = passw.text
        print(f"Trying to create a server with ip {ip.text}:{port.text}")

        if self.initiate_server(self.player1.player_ip, int(self.player1.player_port), self.lan_enc, self.lan_passw):
            self.execute_show_options("lan",'success_s','')
            self.cache_data(self.player1.player_ip, int(self.player1.player_port))
            self.lock_inputs(ip, port, enc, passw, create, connect, start)
            start.disabled = True # Only start with 2 players
            self.start = start
            server.queue_server_data( {'op' : 'game', 'data' : 'name', 'name': self.player1.player_name})
            Clock.schedule_interval(functools.partial(self.server_conditions), 0.5)
        else:
            self.execute_show_options(self.mode, 'error', '')

    def server_conditions(self, *kwargs):
        data = server.get_queue_client_data()
        try:
            # {'op' : 'status', 'connection' : 'established', 'ip': address}
            if data['op'] == "status" and data['connection'] == "established":
                self.player2.player_ip = data['ip'][0]
                self.player2.player_port = data['ip'][1]
                #self.player2.player_name = data['name']

            # {'op' : 'game', 'data' : 'reset'}


            # {'op' : 'game', 'data' : 'name', 'name': ''}
            elif data['op'] == 'game' and data['data'] == 'name':
                self.player2.player_name = data['name']
            
            # {'op' : 'game', 'data' ; 'turn', 'player': ''}

            # {'op' : 'game', 'data' : 'avatar', 'avatar' : ''}
            elif data['op'] == 'game' and data['data'] == 'avatar':
                self.player2.player_avatar = data['avatar'] # client avatar
                if data['avatar'] == 'x':
                    self.player1.player_avatar = 'o' # server avatar
                else:
                    self.player1.player_avatar = 'x' # server avatar
                self.active_player = self.player2.player_avatar

            # {'op' : 'game', 'data' : 'update', 'position' : 'id'}
            elif data['op'] == 'game' and data['data'] == 'update':
                pos = int(data['position'])
                if pos >= 0 and pos < 9:
                    #btn = self.get_id(f"{spot[0]}-{spot[1]}", True)
                    btn = self.all_btns_ids[pos]
                    self.make_play(btn)
                    self.can_play = True

            # {'op' : 'game', 'data' : 'result', 'result' : '', 'player' : ''} -> tie, winner

            server.remove_last_queue_client_data()
        except Exception as e:
            pass

        if self.player2.player_name == "":
            self.start.disabled = False
        self.update_players_lan()

    
        
    ############## Client #################

    def initiate_client(self, ip, port, enc, passw):
        #if not server.test_connection(ip, int(port)):
        if True:
            self.server_handler = threading.Thread(
                                target=client.connect_server,args=(ip,
                                                                    port,
                                                                    enc,
                                                                    passw),
                                                                    daemon=True)
            self.server_handler.start()
            return True
        return False

    def connect_server(self, ip, port, enc, passw, create, connect, start):
        if self.check_inputs([ip, port]) == False:
            return print(False)
        
        self.connection_mode = 'client'
        self.player2.player_name = self.temp_player
        self.player1.player_ip = ip.text
        self.player1.player_port = int(port.text)

        self.lan_enc = ''

        self.lan_passw = passw.text
        print(f"Trying to connect a server with ip {ip.text}:{port.text}")

        if self.initiate_client(self.player1.player_ip, int(self.player1.player_port), self.lan_enc, self.lan_passw):
            self.execute_show_options("lan",'success_s','')
            self.cache_data(self.player1.player_ip, int(self.player1.player_port))
            self.lock_inputs(ip, port, enc, passw, create, connect, start)
            Clock.schedule_interval(functools.partial(self.client_operation), 0.5)
            client.queue_Client_data({'op' : 'game', 'data' : 'name', 'name': self.player2.player_name})
        else:
            self.execute_show_options(self.mode, 'error', '')

    def client_operation(self, *kwargs):
        data = client.get_queue_Server_data()
        #print(data)
        try:
            # {'op' : 'status', 'connection' : 'established', 'ip': address}
            if data['op'] == "status" and data['connection'] == "established":
                self.player2.player_ip = data['ip'][0]
                self.player2.player_port = data['ip'][1]

            # {'op' : 'game', 'data' : 'reset'}
                # self.turn = 1 ou 0
                # reset_screen
                # se

            # {'op' : 'game', 'data' : 'name', 'name': ''}
            elif data['op'] == 'game' and data['data'] == 'name':
                self.player1.player_name = data['name']
            
            # {'op' : 'game', 'data' : 'turn', 'player': ''}
            elif data['op'] == 'game' and data['data'] == 'turn':
                if data['player'] == "player1":
                    self.turn = 1
                elif data['player'] == "player2":
                    self.turn = 0
                    self.change_screen('lan', 'up')
                    self.reset_screen('lan')
                # self.turn = 1 ou 0
                    #self.execute_show_options("lan", 'avatar', 'player2')
                    #client.queue_Client_data({'op' : 'game', 'data' : 'avatar', 'avatar' : self.player2.player_avatar})

            # {'op' : 'game', 'data' : 'avatar', 'avatar' : ''}
            elif data['op'] == 'game' and data['data'] == 'avatar':
                self.player1.player_avatar = data['avatar'] # server avatar
                if data['avatar'] == 'x':
                    self.player2.player_avatar = 'o' # client avatar
                else:
                    self.player2.player_avatar = 'x' # client avatar
                self.can_play = False
                self.change_screen('lan', 'up')
                self.reset_screen('lan')
                self.active_player = self.player1.player_avatar

            # {'op' : 'game', 'data' : 'update', 'position' : 'id'}
            elif data['op'] == 'game' and data['data'] == 'update':
                pos = int(data['position'])
                if pos >= 0 and pos < 9:
                    #btn = self.get_id(f"{spot[0]}-{spot[1]}", True)
                    btn = self.all_btns_ids[pos]
                    self.make_play(btn)
                    self.can_play = True


            # {'op' : 'game', 'data' : 'result', 'result' : '', 'player' : ''} -> tie, winner

            client.remove_last_queue_Server_data()
        except Exception as e:
            pass

        self.update_players_lan()

            
if __name__ == "__main__":
    app = MyApp()
    app.run()