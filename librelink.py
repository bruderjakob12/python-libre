import json
import requests
import pickle

class LibreLink():

    LIBRE_LINK_UP_VERSION = "4.7.0"
    LIBRE_LINK_UP_PRODUCT = "llu.ios"
    LIBRE_LINK_UP_URL = None
    LIBRE_LINK_UP_EMAIL = None
    LIBRE_LINK_UP_PASSWORD = None
    LIBRE_LINK_PATIENTID = None
    USER_AGENT = "FreeStyle LibreLink Up NightScout Uploader"
    LIBRE_LINK_UP_HEADERS = {
        "User-Agent":USER_AGENT,
        "Content-Type":"application/json",
        "version":LIBRE_LINK_UP_VERSION,
        "product":LIBRE_LINK_UP_PRODUCT,
        "Accept-Encoding":"gzip, deflate, br",
        "Connection":"keep-alive",
        "Pragma":"no-cache",
        "Cache-Control":"no-cache",
        "Authorization": ""
    }


    def __init__(self, email, password, url='api-de.libreview.io'):
        self.LIBRE_LINK_UP_EMAIL = email
        self.LIBRE_LINK_UP_PASSWORD = password
        self.LIBRE_LINK_UP_URL = url
        try:
            token = pickle.load(open('libreview_token.pkl', 'rb'))
            self.LIBRE_LINK_UP_HEADERS['Authorization'] = 'Bearer ' + token
        except:
            self.update_token()
        self.get_patientId()


    def get_url(self,url):
        r = requests.get(url, headers=self.LIBRE_LINK_UP_HEADERS)
        if r.status_code != 200:
            if self.update_token():
                # we try once more with an updated token
                r = requests.get(url, headers=self.LIBRE_LINK_UP_HEADERS)
            else:
                return None
        return r.json()
    
    
    def update_token(self,):
        url = 'https://' + self.LIBRE_LINK_UP_URL + '/llu/auth/login'
        data = {'email': self.LIBRE_LINK_UP_EMAIL, 'password': self.LIBRE_LINK_UP_PASSWORD}
        self.LIBRE_LINK_UP_HEADERS.pop('Authorization', None)
        r = requests.post(url, json=data, headers=self.LIBRE_LINK_UP_HEADERS)
        if r.status_code != 200:
            print('auth failed - no token obtained')
            return False
        else:
            token = r.json()['data']['authTicket']['token']
            self.LIBRE_LINK_UP_HEADERS['Authorization'] = 'Bearer ' + token
            pickle.dump(token, open('libreview_token.pkl', 'wb'))
            return True
        
    
    def get_patientId(self,):
        data = self.get_url('https://' + self.LIBRE_LINK_UP_URL + '/llu/connections')
        patientId = None
        if len(data['data']) > 1:
            # TODO: gracefully handle multiple patients
            print('multiple patients in there...')
            return
        self.LIBRE_LINK_PATIENTID = data['data'][0]['patientId']


    def get_data(self,):
        url = "https://" + self.LIBRE_LINK_UP_URL + "/llu/connections/" + self.LIBRE_LINK_PATIENTID + "/graph"
        data = self.get_url(url)
        return data
