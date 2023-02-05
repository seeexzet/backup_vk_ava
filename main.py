import requests
from datetime import datetime
import json

class VK:

   def __init__(self, access_token, user_id, count, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {
           'access_token': self.token, 'v': self.version, 'count': count
       }

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

   def photos_info(self):
       url = 'https://api.vk.com/method/photos.get'
       params = {'owner_id': self.id, 'album_id': 'profile',  'extended': 1}
       response = requests.get(url, params={**self.params, **params})

       list_photos = response.json().get('response').get('items')
       len_list_photos = len(list_photos)
       list_target_photos = []
       list_target_names = []
       list_for_json = []

       for i in range(len_list_photos):
           photo_likes = str(list_photos[i].get('likes').get('count'))
           if photo_likes not in list_target_names:
               list_target_names += [photo_likes]
           else:
               photo_likes = str(photo_likes) + ' '+ str(datetime.utcfromtimestamp(list_photos[i].get('date')).strftime('%Y-%m-%d %H-%M-%S'))
               list_target_names += [photo_likes]
           list_sizes = list_photos[i].get('sizes')
           list2 = sorted(list_sizes, key=lambda d: d['height'])
           photo_link = list2[-1].get('url')
           photo_size = list2[-1].get('type')
           list_target_photos += [photo_link]
           dict = {'filename': photo_likes + '.jpg', 'size': photo_size}
           list_for_json += [dict]
       with open('target.json', 'w') as outfile:
           json.dump(list_for_json, outfile)
       return list_target_photos, list_target_names



class YaUploader:

    base_host = 'https://cloud-api.yandex.net:443/'

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def upload(self, list_links, list_names):
        """Метод загружает файлы по списку file_list на яндекс диск"""

        uri_create_folder = 'v1/disk/resources'
        request_url_create_folder = self.base_host + uri_create_folder
        params1 = {'path': 'vk_folder', 'overwrite': True}

        #создать папку
        responce = requests.put(request_url_create_folder, headers=self.get_headers(), params=params1)

        uri_upload = 'v1/disk/resources/upload'
        request_url_upload = self.base_host + uri_upload

        len_list = len(list_links)
        for i in range(0, len_list):
            print(f'Идёт загрузка файла №{i+1} из {len_list}...')
            file_name = 'vk_folder/' + list_names[i]+'.jpg'
            params1 = {'path': file_name, 'url': list_links[i], 'overwrite': True}
            responce = requests.post(request_url_upload, headers=self.get_headers(), params = params1)
            if responce.status_code == 202:
                print(f'Загрузка файла №{i+1} произошла успешно')
            else:
                print(f'Ошибка №{responce.status_code} при загрузке файла №{i+1}')
                print(responce.json()['error'])


if __name__ == '__main__':
    from vk import VK_TOKEN

    user_id = input('Введите id профиля vk: ')
    count_photo = input('Введите количество фото для  сохранения: ')
    vk = VK(VK_TOKEN, user_id, count_photo)

    list_links, list_names = vk.photos_info()

    YANDEX_TOKEN = input('Введите token для yandex disk: ')
    ya = YaUploader(YANDEX_TOKEN)
    ya.upload(list_links, list_names)
