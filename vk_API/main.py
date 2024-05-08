import requests
# Personal api key
from config import API_KEY

# Person's id vk token
USER_ID = '244095300'
API_VERSION = "5.131"
URL = f"https://api.vk.com/method/friends.get?user_id={USER_ID}&fields=first_name,last_name&access_token={API_KEY}&v={API_VERSION}"

class App:
    def __init__(self,id,access_token,verison):
        self.version = verison
        self.id = id
        self.acess_token = access_token

    @staticmethod
    def fetch()->None:
        response = requests.get(URL)
        data = response.json()

        if 'response' in data:
            data_pars = data['response']['items']
            for data in data_pars:
                print(data['first_name'], data['last_name'])
        else:
            print('Ошибка при получении списка друзей:', data)


vk_app = App(USER_ID,API_KEY,API_VERSION)
vk_app.fetch()
