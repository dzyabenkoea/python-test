import os
import requests

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

class WeatherController:
    """
    Выполняет запрос на получение текущей погоды для города
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()

    @staticmethod
    def get_weather_url(city):
        """
        Генерирует url включая в него необходимые параметры
        @param city: Город
        @return: str
        """
        url = 'https://api.openweathermap.org/data/2.5/weather'
        url += '?units=metric'
        url += '&q=' + city
        url += '&appid=' + WEATHER_API_KEY
        return url

    @staticmethod
    def get_weather_from_response(response):
        """
        Достает погоду из ответа
        Args:
            response: Ответ, пришедший с сервера
        Returns:

        """
        data = response.json()
        return data['main']['temp']

    def send_request(self, url):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:

        """
        r = self.session.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        return r



    def get_weather(self, city):
        """
        Делает запрос на получение погоды
        Args:
            city: Город
        Returns:

        """
        url = WeatherController.get_weather_url(city)
        response = self.send_request(url)
        if response is None:
            return None
        else:
            return WeatherController.get_weather_from_response(response)

    def check_existing(self, city):
        """
        Проверяет наличие города
        @param str city: Название города
        @return: bool
        """
        url = WeatherController.get_weather_url(city)
        response = self.send_request(url)
        if response.status_code == 404:
            return False
        if response.status_code == 200:
            return True
