from re import MULTILINE
import kivy
from kivy.app import App
from kivy.uix.label import Label # Import the simbols and widgets
import os
#os.environ["SDL_VIDEODRIVER"] = "x11"
from kivy.uix.gridlayout import GridLayout # Import GridLayout design
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button # import buttons

class MenuLayout(GridLayout):
    def __init__(self, **kwargs): # handle as many kwargs as come
        super(MenuLayout, self).__init__(**kwargs)
        self.cols = 1
        
        self.inside = GridLayout() # first layout
        self.inside.cols = 2

        #self.cols = 2
        self.inside.add_widget(Label(text = "First Name: "))
        self.firstName = TextInput(multiline = False)
        self.inside.add_widget(self.firstName)

        self.inside.add_widget(Label(text = "Last Name: "))
        self.lastName = TextInput(multiline = False)
        self.inside.add_widget(self.lastName)

        self.inside.add_widget(Label(text = "Email: "))
        self.email = TextInput(multiline = False)
        self.inside.add_widget(self.email)

        self.add_widget(self.inside)


        self.submit = Button(text = "Submit:", font_size = 40)
        self.submit.bind(on_press = self.pressed)
        self.add_widget(self.submit)

    def pressed(self, instance):
        name = self.firstName.text
        last = self.lastName.text
        email = self.email.text

        print("Name: ", name, "LastName: ", last, "Email: ", email)
        self.lastName.text = ""
        self.firstName.text = ""
        self.email.text = ""

class MyApp(App):
    def build(self): # Construir o UI
        return MenuLayout()

if __name__ == "__main__":
    MyApp().run()