import requests
# Personal api key
from config import API_KEY
# Person's id vk token
user_id = '244095300'

response = requests.get(
    f'https://api.vk.com/method/friends.get?user_id={user_id}&fields=first_name,last_name&access_token={API_KEY}&v=5.131')
data = response.json()

if 'response' in data:
    data_pars = data['response']['items']
    for data in data_pars:
        print(data['first_name'], data['last_name'])
else:
    print('Ошибка при получении списка друзей:', data)