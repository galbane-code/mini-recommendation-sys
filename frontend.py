import mybackend as bk
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup,PopupException
from kivy.uix.label import Label

import requests


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

    def get_location_weather(self):
        lon = '-74.05044364'
        lat = '40.73478582'
        api_key = '1d65977226de5416df48c4f7b523f261'
        url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'.format(lat,lon,api_key)
        res = requests.get(url)
        data = res.json()

        return data['main']['temp'], data['wind']['speed']


    def recBtn(self):

        # check if values are as excepted
        if self.validate(self.cur_location.text, self.duration.text, self.num_rec.text):
            self.reset()
        # if all parameters are valid call the backend function to return a list of strings contains the locations
        else:
            self.Search()
            self.reset()

    def Search(self):

        results = bk.get_location_for_recommendation(self.cur_location.text, int(self.duration.text), int(self.num_rec.text))
        pop_text = ["[size=24]We recommend you to travle[/size]:\n"]
        pop_text.extend(location + "\n" for location in results)
        pop_text = "".join(pop_text)
        temp,wind_speed = self.get_location_weather()
        pop = Popup(title='Your Results', title_size='30sp', title_color=(0, 0, 0, 1),
                    content=Label(text=str(pop_text),markup=True,
                                  halign="center",
                                  color=(66/255, 135/255, 245/255,1),
                                  font_size='20sp',
                                  bold=True),
                    size_hint=(None, None),
                    size=(500, 500),
                    background="popupimg.png")
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
                pop = Popup(title='Invalid Location',title_color=(1,1,1,1),
                            content=Label(text='start location-{}\nis not exists'.format(location),
                                          halign='center',
                                          color=(1,0,0,1),
                                          bold=True,
                                          font_size='40sp'),
                            size_hint=(None, None), size=(400, 400),
                            background="404.jpg")
                pop.open()
                return True
            if len(duration) == 0 or not duration.isdigit() or int(duration) <= 0:
                pop = Popup(title='Invalid Duration',title_color=(1,1,1,1),
                            content=Label(text='Duration most be a None Zero Positive Number.\nTry Again.',
                                          halign='center',
                                          color=(1,0,0,1),
                                          bold=True,
                                          font_size='20sp'),
                            size_hint=(None, None),
                            size=(400, 400),
                            background="404.jpg")
                pop.open()
                return True
            elif len(amount) == 0 or not amount.isdigit() or int(amount) <= 0:
                pop = Popup(title='Invalid Amount of Recommendations',title_color=(1,1,1,1),
                            content=Label(text='Recommendation Amount most be at least 1.\nTry Again.',
                                          halign='center',
                                          color= (1,0,0,1),
                                          bold = True,
                                          font_size='20sp'),
                            size_hint=(None, None),
                            size=(400, 400),
                            background="404.jpg")
                pop.open()
                return True
            return False

        except Exception as e:
            pop = Popup(title='error',
                        content=Label(text='Error happened in the db.'),
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
