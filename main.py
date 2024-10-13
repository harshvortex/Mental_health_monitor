from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=2)

        layout.add_widget(Label(text='Username:'))
        self.username = TextInput(multiline=False)
        layout.add_widget(self.username)

        layout.add_widget(Label(text='Password:'))
        self.password = TextInput(password=True, multiline=False)
        layout.add_widget(self.password)

        login_button = Button(text='Login')
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)

        signup_button = Button(text='Sign Up')
        signup_button.bind(on_press=self.signup)
        layout.add_widget(signup_button)

        self.add_widget(layout)

    def login(self, instance):
        print(f'Logged in as {self.username.text}')
        self.manager.current = 'home'

    def signup(self, instance):
        print(f'Signed up as {self.username.text}')
        self.manager.current = 'home'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        menu_label = Label(text='Menu', size_hint_y=None, height=40)
        layout.add_widget(menu_label)

        options_layout = BoxLayout(size_hint_y=None, height=40)
        options = ['Home', 'Results', 'Chatbot', 'Profile']
        
        for option in options:
            button = Button(text=option)
            button.bind(on_press=self.show_option)
            options_layout.add_widget(button)

        layout.add_widget(options_layout)
        
        self.add_widget(layout)

    def show_option(self, instance):
        print(f'Selected: {instance.text}')

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        
        return sm

if __name__ == '__main__':
    MyApp().run()