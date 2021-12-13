# main.py
import mybackend as bk
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics.context_instructions import Color, Image


class LoginWindow(Screen):
    """
    :param cur_loction
    :param duration
    :param num_rec
    initiate Properties
    """
    cur_location = ObjectProperty(None)
    duration = ObjectProperty(None)
    num_rec = ObjectProperty(None)


    def recBtn(self):
        print("login Window")

        #check if values are as excepted
        if self.validate(self.cur_location.text,self.duration.text,self.num_rec.text):
            print("Not good")
            self.reset()
        # if all parameters are valid call the backend function to return a list of strings contains the locations
        else:
            print("all good")
            self.Search()
            self.reset()

    def Search(self):
        #TODO: add functionality of BackEnd
        results = ["holon", "bash"] ## add here results getter
        pop_text = [location + "\n" for location in results]
        pop_text = "".join(pop_text)


        pop = Popup(title='Your Results',title_color=(0,0,0,1),
                    content=Label(text=str(pop_text),
                            color=(0,0,0,1),
                            bold=True),
                    size_hint=(None, None), size=(400, 400),
                    background ="popupimg.jpg")
        pop.open()

    # reset the TextInput to an empty string
    def reset(self):
        self.cur_location.text = ""
        self.duration.text = ""
        self.num_rec.text = ""

    """
    gets 3 inputs and checks if the are in the required format
    :return- True a popup window popped else all good return False
    """
    def validate(self,location,duration,amount):
        #TODO: add conditon if location is in db from backend(add a getter)

        # if location != "Holon":
        #     pop = Popup(title='Invalid Location',
        #                 content=Label(text='Location was Not Found.'+str(location)),
        #                 size_hint=(None, None), size=(400, 400))
        #     pop.open()
        #     return False
        if len(duration) == 0 or not duration.isdigit() or int(duration) <= 0:
            pop = Popup(title='Invalid Duration',
                        content=Label(text='Duration most be a None Zero Positive Number.\nTry Again.'),
                        size_hint=(None, None), size=(400, 400))
            pop.open()
            return True
        elif len(amount) == 0 or not amount.isdigit() or int(amount) <= 0:
            pop = Popup(title='Invalid Amount of Recommendations',
                        content=Label(text='Recommendation Amount most be at least 1.\nTry Again.'),
                        size_hint=(None, None), size=(400, 400))
            pop.open()
            return True
        return False

class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("bike.kv")

sm = WindowManager()
#db = DataBase("users.txt")

screens = [LoginWindow(name="login")]#,MainWindow(name="main")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()