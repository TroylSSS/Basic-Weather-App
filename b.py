import sys, requests, os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QLineEdit, QLabel, 
                             QPushButton, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.city_label = QLabel("Enter City Name:  ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.description_label = QLabel(self)

        self.toggle_button = QPushButton("Show °F", self)
        self.is_celsius = True

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")

        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.setWindowIcon(QIcon(icon_path))


        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.description_label)

        vbox.addWidget(self.toggle_button)

        self.setLayout(vbox)

        # Align elements
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        # Object names for targeted styling
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.description_label.setObjectName("description_label")

        # Stylesheet
        self.setStyleSheet("""
            QLabel, QPushButton {
                font-family: Arial, sans-serif;
            }
            QLabel#city_label {
                font-size: 40px;
                font-weight: bold;
                font-style: italic;
                color: #333;
            }
            QLineEdit#city_input {
                font-size: 40px;
                color: #333;
                border: 2px solid #ccc;
            }
            QPushButton#get_weather_button {
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temperature_label {
                font-size: 75px;
                font-weight: bold;
            }
            QLabel#description_label {
                font-size: 50px;
                font-weight: bold;
                font-style: italic;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)
        self.toggle_button.clicked.connect(self.toggle_temperature_unit)

    def get_weather(self):

        api_key = "" # https://home.openweathermap.org/api_key              
                    # Removed the api key, please use your own API key
        
        
        city = self.city_input.text()


        if not city:
            self.display_error("Please enter a city name.")
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)
            

        # Exception Handling
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess denied")
                case 404:
                    self.display_error("Not Found:\nCity not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid response from server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down or overloaded")
                case 504:
                    self.display_error("Gateway Timeout:\nNo response from server")
                case _:
                    self.display_error(f"HTTP error occurred:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection:\nPlease check your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("Request timed out:\nPlease try again later")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects:\nPlease check the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"An error occurred: {req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 15px;")
        self.temperature_label.setText(message)
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_kelvin = data["main"]["temp"]
        temperature_celsius = temperature_kelvin - 273.15
        temperature_fahrenheit = (temperature_kelvin * 9 / 5) - 459.67

        feels_like_kelvin = data["main"]["feels_like"]
        feels_like_celsius = feels_like_kelvin - 273.15


        # For temperature unit toggle
        self.current_temperature_c = temperature_celsius
        self.current_temperature_f = temperature_fahrenheit
    
        humidity = data["main"]["humidity"]   
        pressure = data["main"]["pressure"]      
        wind_speed = data["wind"]["speed"]        

        weather_description = data["weather"][0]["description"]

        self.temperature_label.setText(
            f"{temperature_celsius:.2f} °C / {temperature_fahrenheit:.2f} °F"
        )

        self.update_temperature_display()

        details = (

            f"{weather_description.capitalize()}\n"
            f"Feels like: {feels_like_celsius:.2f} °C\n"
            f"Humidity: {humidity}%\n"
            f"Pressure: {pressure} hPa\n"
            f"Wind Speed: {wind_speed} m/s"
                
                 )

        self.current_temperature_c = temperature_celsius
        self.current_temperature_f = temperature_fahrenheit
        self.description_label.setText(details.title())


    def update_temperature_display(self):
        if self.is_celsius:
            self.temperature_label.setText(f"{self.current_temperature_c:.2f} °C")
            self.toggle_button.setText("Show °F")
        else:
            self.temperature_label.setText(f"{self.current_temperature_f:.2f} °F")
            self.toggle_button.setText("Show °C")


    def toggle_temperature_unit(self):
        self.is_celsius = not self.is_celsius
        self.update_temperature_display()





if __name__ == "__main__":
    app = QApplication(sys.argv)


    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    app.setWindowIcon(QIcon(icon_path))

    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
