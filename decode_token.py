# import tkinter as tk
# from tkinter import messagebox
# import requests

# # Replace 'your_api_key_here' with your actual OpenWeatherMap API key
# API_KEY = "c902150074357c63678009d7b8c31451"
# BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# def get_weather(city):
#     """
#     Fetches the weather data for a given city from OpenWeatherMap.

#     Parameters:
#     - city (str): The name of the city for which to fetch the weather.

#     Returns:
#     - dict: A dictionary containing weather information, or None if an error occurs.
#     """
#     try:
#         # Construct the URL for the API request
#         url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
#         response = requests.get(url)
#         data = response.json()

#         # Check if the response contains valid weather data
#         if data['cod'] == 200:
#             return data
#         else:
#             messagebox.showerror("Error", f"City '{city}' not found.")
#             return None
#     except Exception as e:
#         messagebox.showerror("Error", "Failed to fetch weather data. Please try again.")
#         return None

# def show_weather():
#     """
#     Retrieves weather data for the city entered by the user and updates the GUI.
#     """
#     city = city_entry.get()
#     weather_data = get_weather(city)

#     if weather_data:
#         city_name = weather_data['name']
#         temperature = weather_data['main']['temp']
#         description = weather_data['weather'][0]['description']
#         humidity = weather_data['main']['humidity']
#         wind_speed = weather_data['wind']['speed']

#         weather_info = f"City: {city_name}\nTemperature: {temperature}°C\n" \
#                        f"Weather: {description.capitalize()}\nHumidity: {humidity}%\n" \
#                        f"Wind Speed: {wind_speed} m/s"

#         weather_label.config(text=weather_info)

# def create_gui():
#     """
#     Creates the main GUI window for the weather app.
#     """
#     global city_entry, weather_label

#     window = tk.Tk()
#     window.title("Weather App")
#     window.geometry("300x250")

#     # Create and place the widgets
#     city_entry = tk.Entry(window, font=("Arial", 14))
#     city_entry.pack(pady=10)

#     get_weather_button = tk.Button(window, text="Get Weather", command=show_weather)
#     get_weather_button.pack(pady=5)

#     weather_label = tk.Label(window, font=("Arial", 12), justify="left")
#     weather_label.pack(pady=20)

#     window.mainloop()

# if __name__ == "__main__":
#     create_gui()
