from datetime import datetime, time
from urllib.parse import urlencode, urlparse, urlunparse

import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden

from authapp.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return

    api_url = urlunparse(('https',
                          'api.vk.com',
                          '/method/users.get',
                          None,
                          urlencode(dict(fields=','.join(('bdate', 'sex', 'about')),
                          access_token=response['access_token'], v='5.131')),
                         None))
    resp = requests.get(api_url)
    if resp.status_code != 200:
        return
    pols = user
    data = resp.json()['response'][0]
    if data['sex']:
        user.shopuserprofile.gender = ShopUserProfile.MALE if data['sex'] == 2 else ShopUserProfile.FEMALE

    if data['about']:
        user.shopuserprofile.aboutMe = data['about']

    if data['bdate']:
        bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()
        user.shopuserprofile.age = timezone.now().date().year - bdate.year

        # if age < 18:
        #     user.delete()
        #     raise AuthForbidden('social_core.backend.vk.VKOAuth2')

    user.save()
