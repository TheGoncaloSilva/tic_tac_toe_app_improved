import kivy
from kivy.app import App
from kivy.uix.label import Label # Import the simbols and widgets
from kivy.uix.gridlayout import GridLayout # Import GridLayout design
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button # import buttons
from kivy.uix.widget import Widget # import tu use kv language
from kivy.properties import ObjectProperty #Import object properties, to get the values

class MyGrid(Widget):
    # Get the variable values on the kv file
    name = ObjectProperty(None) # Initialize name
    email = ObjectProperty(None)

    # Onpress on the kv file button
    def btn(self):
        print("Name: ", self.name.text, " Email: ", self.email.text)
        self.name.text = ""
        self.email.text = ""

class MyApp(App):
    def build(self): # Construir o UI
        return MyGrid()

if __name__ == "__main__":
    MyApp().run()