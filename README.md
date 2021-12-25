# tic_tac_toe_app_improved
Improved Tic-tac-toe game (jogo do galo) using python and kivy with graphical interfaces. Also incorporating connections with server and client for multiplayer
  - Same functionalities as previous version;
  - Improved UI;
  - Server and client functionality in order to play in LAN;
  - Messaging chat.

# Install using PIP
    2.2 Using Pip
      2.2.1 Install virtual environments
        $ python3 -m pip install --upgrade pip setuptools virtualenv
        $ python3 -m virtualenv kivy_venv
      2.2.2 Activate virtual environments
        2.2.2.1 Windows
          $ kivy_venv\Scripts\activate
        2.2.2.2 Bash
          $ source kivy_venv/Scripts/activate
        2.2.2.3 Linux
          $ source kivy_venv/bin/activate
      2.2.3 Install kivi
        $ python3 -m pip install kivy[base] kivy_examples
        $ python3 -m pip install kivy[full] kivy_examples -> for full dependencies
        $ pip install kivy[sdl2]
      Check the installation
        Windows:
          $ python3 kivy_venv\share\kivy-examples\demo\showcase\main.py
        Linux:
          $ python3 kivy_venv/share/kivy-examples/demo/showcase/main.py
