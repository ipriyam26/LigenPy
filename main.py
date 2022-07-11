from time import sleep
from requests import request
import requests
from bs4 import BeautifulSoup
class Libgen:
    def __init__(self):
        self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8,en-US;q=0.7',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Pragma': 'no-cache',
                'Referer': 'http://libgen.rs/search.php?req=New+Rules&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.51',
            }
    def get_search(self,search)->str:
            cookies = {
                'lg_topic': 'libgen',
            }


            params = (
                ('req', search),
                ('open', '0'),
                ('res', '25'),
                ('view', 'simple'),
                ('phrase', '1'),
                ('column', 'def'),
            )

            response = requests.get('http://libgen.rs/search.php', headers=self.headers, params=params, cookies=cookies, verify=False)

            if response.status_code == 200:
                return self.parse_data(response.text)
            print("Request failed with status code: {}".format(response.status_code))
            sleep(5)
            self.get_raw()
    
    def parse_data(self,data)->list:
        soup = BeautifulSoup(data, 'html.parser')
        body = soup.find('body')
        table = body.find_all('table')[2]
        print(table)
        
        

if __name__ == '__main__':
    lib = Libgen()
    lib.get_search("Atomic Habits")