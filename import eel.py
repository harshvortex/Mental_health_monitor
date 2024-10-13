import eel

eel.init('web')

@eel.expose
def login(username):
    print(f'Logged in as {username}')
    eel.show_home()

@eel.expose
def signup(username):
    print(f'Signed up as {username}')
    eel.show_home()

eel.start('index.html', size=(400, 300))