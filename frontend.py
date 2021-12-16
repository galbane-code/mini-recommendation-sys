import mybackend as bk
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label


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
        # check if values are as excepted
        if self.validate(self.cur_location.text, self.duration.text, self.num_rec.text):
            self.reset()
        # if all parameters are valid call the backend function to return a list of strings contains the locations
        else:
            self.Search()
            self.reset()

    def Search(self):
        try:
            results = bk.get_location_for_recommendation(self.cur_location.text, int(self.duration.text), int(self.num_rec.text))
            pop_text = [location + "\n" for location in results]
            pop_text = "".join(pop_text)

            pop = Popup(title='Your Results', title_size='30sp', title_color=(1, 1, 1, 1),
                        content=Label(text=str(pop_text),
                                      color=(1, 1, 1, 1),
                                      font_size='20sp',
                                      bold=True),
                        size_hint=(None, None), size=(500, 500),
                        background="popupimg.png")
            pop.open()

        except Exception as e:
            pop = Popup(title='error',
                        content=Label(text='error happened in the db.'),
                        size_hint=(None, None), size=(400, 400))
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
    def validate(self, location, duration, amount):
        try:
            if not bk.check_location_in_db(location):
                pop = Popup(title='Invalid Location',
                            content=Label(text='Location was Not Found.' + str(location)),
                            size_hint=(None, None), size=(400, 400))
                pop.open()
                return False
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

        except Exception as e:
            pop = Popup(title='error',
                        content=Label(text='error happened in the db.'),
                        size_hint=(None, None), size=(400, 400))
            pop.open()


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my.kv")

sm = WindowManager()

screens = [LoginWindow(name="login")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    MyMainApp().run()
