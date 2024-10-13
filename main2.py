import sys
import sqlite3
import random
import smtplib
from twilio.rest import Client  # For sending SMS (install Twilio library)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QStackedWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
import re

# Twilio credentials (replace with your actual credentials)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                mobile TEXT NOT NULL,
                personality_details TEXT,
                mental_health_details TEXT
            )
        ''')
        self.connection.commit()

    def add_user(self, username, password, email, mobile):
        try:
            self.cursor.execute("INSERT INTO users (username, password, email, mobile) VALUES (?, ?, ?, ?)", 
                                (username, password, email, mobile))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return self.cursor.fetchone() is not None

    def close(self):
        self.connection.close()

class LoginScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        
        self.stacked_widget = stacked_widget  # Store reference to the stacked widget
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_label = QLabel('Username:')
        layout.addWidget(self.username_label)
        
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:')
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton('Login')
        login_button.clicked.connect(self.on_login)
        
        signup_button = QPushButton('Sign Up')
        signup_button.clicked.connect(self.switch_to_signup)

        forgot_password_button = QPushButton('Forgot Password')
        forgot_password_button.clicked.connect(self.switch_to_forgot_password)

        layout.addWidget(login_button)
        layout.addWidget(signup_button)
        layout.addWidget(forgot_password_button)

        self.setLayout(layout)

    def on_login(self):
         db = Database()
         if db.authenticate_user(self.username_input.text(), self.password_input.text()):
             print(f'Logged in as {self.username_input.text()}')
             QMessageBox.information(self, 'Success', 'Logged in successfully!')
         else:
             QMessageBox.warning(self, 'Error', 'Invalid credentials!')
         db.close()

    def switch_to_signup(self):
         self.stacked_widget.setCurrentIndex(1)  # Switch to sign-up screen

    def switch_to_forgot_password(self):
         QMessageBox.information(self, 'Info', 'Forgot Password functionality is not implemented yet!')

class SignupScreen(QWidget):
    def __init__(self):
       super().__init__()
       self.initUI()

    def initUI(self):
       layout = QVBoxLayout()

       # Sign up form fields
       self.username_label = QLabel('Username:')
       layout.addWidget(self.username_label)

       self.username_input = QLineEdit()
       layout.addWidget(self.username_input)

       self.password_label = QLabel('Password:')
       layout.addWidget(self.password_label)

       self.password_input = QLineEdit()
       self.password_input.setEchoMode(QLineEdit.Password)
       layout.addWidget(self.password_input)

       self.email_label = QLabel('Email (@gmail.com):')
       layout.addWidget(self.email_label)

       self.email_input = QLineEdit()
       layout.addWidget(self.email_input)

       self.mobile_label = QLabel('Mobile (+91XXXXXXXXXX):')
       layout.addWidget(self.mobile_label)

       self.mobile_input = QLineEdit()
       layout.addWidget(self.mobile_input)

       signup_button = QPushButton('Sign Up')
       signup_button.clicked.connect(self.on_signup)
       
       back_button = QPushButton('Back to Login')
       back_button.clicked.connect(lambda: app.setCurrentIndex(0))

       layout.addWidget(signup_button)
       layout.addWidget(back_button)

       self.setLayout(layout)

    def on_signup(self):
         username = self.username_input.text()
         password = self.password_input.text()
         email = self.email_input.text()
         mobile = self.mobile_input.text()

         if not validate_email(email):
             QMessageBox.warning(self, 'Error', 'Please enter a valid Gmail address.')
             return
         
         if not validate_mobile(mobile):
             QMessageBox.warning(self, 'Error', 'Please enter a valid Indian mobile number.')
             return

         db = Database()
         if db.add_user(username, password, email, mobile):
             otp = random.randint(100000, 999999)  # Generate OTP
             if send_otp_email(email, otp) and send_otp_sms(mobile, otp):  # Send OTP to user
                 QMessageBox.information(self, 'Success', 'User registered successfully! Check your email and SMS for OTP.')
                 # Here you can implement OTP verification logic
             else:
                 QMessageBox.warning(self, 'Error', 'Failed to send OTP!')
         else:
             QMessageBox.warning(self, 'Error', 'Username already exists!')
         db.close()

def validate_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email) is not None

def validate_mobile(mobile):
    return re.match(r"^\+91[0-9]{10}$", mobile) is not None

def send_otp_email(email_address, otp):
    try:
        sender_email = "your_email@gmail.com"  # Replace with your Gmail address
        sender_password = "your_password"  # Replace with your Gmail password
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            message = f"Your OTP is: {otp}"
            server.sendmail(sender_email, email_address, message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_otp_sms(mobile_number, otp):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=mobile_number
        )
        
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

class MyApp(QWidget):
    def __init__(self):
       super().__init__()
       self.initUI()

    def initUI(self):
       global app
       
       # Create stacked widget for navigation between screens
       self.stacked_widget = QStackedWidget()
       
       # Create screens and pass the stacked widget reference to LoginScreen
       self.login_screen = LoginScreen(stacked_widget=self.stacked_widget)
       self.signup_screen = SignupScreen()

       # Add screens to stacked widget
       self.stacked_widget.addWidget(self.login_screen)
       self.stacked_widget.addWidget(self.signup_screen)

       # Set main layout
       main_layout = QVBoxLayout()
       
       # Set window title and size
       self.setWindowTitle('Mental Health Monitoring App')
       
       # Load background image and set it as a palette for the main window
       pixmap = QPixmap("C:/Users/harsh/OneDrive/Desktop/mhm/WhatsApp Image 2024-10-12 at 11.23.26_0fcc39e5.jpg")
       
       palette = QPalette()
       
       palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
           400,
           300,
           Qt.KeepAspectRatioByExpanding,
           Qt.SmoothTransformation)))
       
       self.setPalette(palette)
       
       main_layout.addWidget(self.stacked_widget)
       
       # Set main layout to the window
       self.setLayout(main_layout)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   ex.show()
   sys.exit(app.exec_())