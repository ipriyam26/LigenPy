from dataclasses import dataclass
from pprint import pprint
import shutil
from time import sleep
from typing import Dict, List
from requests import request
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm


@dataclass
class Book:
    Title: str
    Author: str
    Id: str
    Publisher: str
    Year: int
    Pages: str
    Language: str
    Size: str
    Type: str
    Mirrors: List[str]
    image: str
    description: str
    download_link: List[str]
    
    def download(self):
        with requests.get(self.download_link[0],stream=True) as response:
            total_length = int(response.headers.get('Content-Length'))
            with tqdm.wrapattr(response.raw,"read",total=total_length,desc="") as raw:
                with open(f"{self.Title}.{self.Type}", "wb") as f:    
                    shutil.copyfileobj(raw, f)




class Libgen:
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8,en-US;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Referer": "http://libgen.rs/search.php?req=New+Rules&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.51",
        }
        self.cookies = {
            'lg_topic': 'libgen',
        }


    def author_search(self, author:str) -> List[Book]:


        params = (
            ('req', author),
            ('column', 'author'),
        )

        response = requests.get('http://libgen.rs/search.php', headers=self.headers, params=params, cookies=self.cookies, verify=False)

        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.author_search(author)
        
    def isbn_search(self, isbn:str) -> List[Book]:
        params = (
            ('req', isbn),
            ('open', '0'),
            ('res', '25'),
            ('view', 'simple'),
            ('phrase', '1'),
            ('column', 'identifier'),
        )

        response = requests.get('http://libgen.rs/search.php', headers=self.headers, params=params, cookies=self.cookies, verify=False)

        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.isbn_search(isbn)
        
    
    

    def search(self, search:str) -> List[Book]:
        params = (
            ("req", search),
            ("open", "0"),
            ("res", "25"),
            ("view", "simple"),
            ("phrase", "1"),
            ("column", "def"),
        )

        response = requests.get(
            "http://libgen.rs/search.php",
            headers=self.headers,
            params=params,
            cookies=self.cookies,
            verify=False,
        )

        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.search(search)
        
    def _parse_mirrors(self, link: str) -> Dict[str,str]:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8,en-US;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': 'http://libgen.rs/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.51',
        }

        response = requests.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        image= f'http://library.lol{soup.find("img").get("src")}'
        try:
            des = soup.select("p+ div")[0].text
            des = des.replace("Description:", "")
        except Exception:
            des = ""
        temps = soup.select("li a")
        links = [temp.get("href") for temp in temps]
        return {
            'image': image,
            'description': des,
            'download': links,
        }

        
        
        


        
        

    def _parse_data(self, data) -> List[Book]:
        soup = BeautifulSoup(data, "html.parser")
        body = soup.find("body")
        table = body.find_all("table")[2]
        rows = table.find_all("tr")[1:]
        books = []
        for row in rows:
            mirrors_temp = row.find_all("td")[9:12]
            mirrors = []
            for mirror_temp in mirrors_temp:
                a = mirror_temp.find("a")
                mirrors.append(a.get("href"))
            temp = self._parse_mirrors(mirrors[0])
            books.append(
                Book(
                    row.find_all("td")[2].text,
                    row.find_all("td")[1].text,
                    row.find_all("td")[0].text,
                    row.find_all("td")[3].text,
                    int(row.find_all("td")[4].text) if row.find_all("td")[4].text else 0,
                    row.find_all("td")[5].text,
                    row.find_all("td")[6].text,
                    row.find_all("td")[7].text,
                    row.find_all("td")[8].text,
                    mirrors,
                    temp.get("image"),
                    temp.get("description"),
                    temp.get("download"),
                )
            )
        return books


if __name__ == "__main__":
    lib = Libgen()
    books = lib.search("ikigai")
    pprint(books)
    books[0].download()
