# https://www.youtube.com/watch?v=8vD-V5jpjBo
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

# Graphics use OpenGl
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.graphics import Line



class Touch(Widget):

    def __init__(self, **kwargs):
        super(Touch, self).__init__(**kwargs)

        with self.canvas:
            Line(points = (20, 30, 400, 500, 60, 300)) # various points line
            Color(1, 0 , 0, .5, mode = 'rgba') # change color of canvas below
            self.rect = Rectangle(pos = (0, 0), size = (50, 50))

    def on_touch_down(self, touch):
        self.rect.pos = touch.pos # Move the square with touches
        print("Mouse Down", touch)

    def on_touch_move(self, touch):
        self.rect.pos = touch.pos # Move the square with touches
        print("Mouse Move", touch)
    

class MyApp(App):
    def build(self):
        return Touch()

if __name__ == "__main__":
    MyApp().run()