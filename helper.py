from dataclasses import dataclass
import enum
import shutil
from typing import Dict, List
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

import requests


class Filter(enum.Enum):
    year = 'Year'
    pages = 'Page'
    author = 'Author'
    size = 'Size'
    extension = 'Type'
    publisher = 'Publisher'
    language = 'Language'
    
    
    

@dataclass
class Source:
    cloudflare: str
    ipfs_io: str
    infura: str
    pinata:str


@dataclass
class Book:        
    Title: str
    Author: str
    Id: str
    Publisher: str
    Year: int
    Pages: str
    Language: str
    Size: int
    Type: str
    Mirrors: List[str]
    image: str
    description: str
    source: Source
    
    
    def download(self):
        with requests.get(self.source.cloudflare,stream=True) as response:
            total_length = int(response.headers.get('Content-Length'))
            with tqdm.wrapattr(response.raw,"read",total=total_length,desc="") as raw:
                with open(f"{self.Title}.{self.Type}", "wb") as f:    
                    shutil.copyfileobj(raw, f)
                    
class Helper:
    def _refactor_size(self,size:str):
            parts = size.strip().split(" ")
            if parts[1] == "":
                size = 0
            if "M" in parts[1]:
                size = float(parts[0]) * 1024 * 1024
            elif "G" in parts[1]:
                size = float(parts[0]) * 1024 * 1024 * 1024
            elif "K" in parts[1]:
                size = float(parts[0]) * 1024
            else:
                size = float(parts[0])
            return size
    
    def _refactor_year(self,year:str):
        return int(year) if year else 0

    def _refactor_pages(self,pages:str):
        pages = pages.strip()
        if not pages:
            return 0
        elif '[' in pages:
            if pages.startswith('['):
                pages = pages[1:]
                pages = pages.split(']')[0]
            else:
                pages = pages.split('[')[0]
        return int(pages)
        
            
    def _parse_mirrors(self, link: str) -> Dict[str,str|Source]:
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
        source = Source(
            cloudflare=links[0] or '',
            ipfs_io=links[1] or '',
            infura=links[2] or '',
            pinata=links[3] or '',
        )

        return {
            'image': image,
            'description': des,
            'source': source,
        }

        