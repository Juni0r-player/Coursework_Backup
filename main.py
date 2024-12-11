import requests
import os
import dotenv
from tqdm import tqdm

dotenv.load_dotenv()
vk_token = os.getenv('vk_token')
id_user = int(input('Введите id пользователя VK: '))
ya_token = input('Введите токен с Полигона Яндекс диска: ')

class VK:
    def __init__(self, access_token, id_user, version=5.199):
        self.base_address = 'https://api.vk.com/method/'
        self.params = {
            'access_token': access_token,
            'v': version
        }
        self.id_user = id_user
        
    def get_user_photos(self, id_user, count=5):
        url = f'{self.base_address}photos.get'
        params = {'owner_id': id_user, # у какого пользователя взять фото 
                  'album_id': 'profile', # profile говорит о фото со стены
                  'photo_sizes': 1, # показывать размеры фото
                  'extended': 1, # возвращает инфо о фото (лайки)
                  'count': count                 
                  }
        params.update(self.params)
        response = requests.get(url=url, params=params)
        return response.json() # мы работаем по этофу файлику
          
    def __enter__(self):
        response = self.get_user_photos(self.id_user)
        photos = response['response']['items']
        return photos
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is IndexError:
            print('Произошла ошибка')
        print('сomplited')
        return True
    

class YACreateFolder: 
    def __init__(self, ya_token):
        self.ya_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.ya_token = ya_token
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {ya_token}'}
        
    def create_folder(self, directory_name='VK_photo'):
        """Создание папки на ya диске, информация подается в заголовке"""
        put_url = requests.put(f'{self.ya_url}?path={directory_name}', headers=self.headers)
        return directory_name 
    
def main():
    result = []
    ya = YACreateFolder(ya_token)
    ya.create_folder() # По умолчанию название фото VK_photo
     
    ya_upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    ya_upload_headers = {
                        'Authorization': ya_token
                        } 
                        
    with VK(vk_token, id_user) as photos: 
        '''Загрузка фото на яндекс диск.'''
    
        for photo in tqdm(photos):
            path = photo['likes']['count'] # путь к количеству лайков
            for size in photo['sizes']:
                if size['type'] == 'z': # если у фото максимальный размер
                    ya_upload_params = {
                        'path': f'VK_photo/{path}', # название фото по кол-ву лайков.
                        'url': size['url'], # ссылка
                        'disable_redirects': False
                        }
                    res = requests.post(ya_upload_url, headers=ya_upload_headers, params=ya_upload_params)
                    result.append({'file_name': f'{path}.jpg', 'size': size['type']})
    return result               
    
    
if __name__ == '__main__':
    print(main())


  

         


        