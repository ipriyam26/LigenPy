from pprint import pprint
from time import sleep
from typing import Any, Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
from helper import Book, Helper,Filter



class Search:
    """
    Library genius search engine.
    """
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
        self.books = []
        self.helper = Helper()
        self.count = 25
        self.used_search = None
        self.attributes = None
    
    def get_more(self)->List[Book]:
        """To be called after any search to get more books.
        

        Returns:
            List[Book]: List of books with more books added
        """
        try:
            self.count += 25
            return   self.used_search(self.attributes)
        except Exception:
            self.count -= 25
            print("Please use after running any other search")

    def author_search(self, author:str) -> List[Book]:
        """Search books from there author.

        Args:
            author (str): author name

        Returns:
            List[Book]: List of books matching the author name.
        """     
        params = (
            ('req', author),
            ('column', 'author'),
        )
        
        response = requests.get('http://libgen.rs/search.php', headers=self.headers, params=params, cookies=self.cookies, verify=False)
        self.used_search = self.author_search
        self.attributes = author
        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.author_search(author)
        
    def isbn_search(self, isbn:str) -> List[Book]:
        """List of books with the isbn number.

        Args:
            isbn (str): isbn number of the book.

        Returns:
            List[Book]: books with the isbn number.
        """
        
        params = (
            ('req', isbn),
            ('open', '0'),
            ('res', f'{self.count}'),
            ('view', 'simple'),
            ('phrase', '1'),
            ('column', 'identifier'),
        )

        response = requests.get('http://libgen.rs/search.php', headers=self.headers, params=params, cookies=self.cookies, verify=False)
        self.used_search = self.isbn_search
        self.attributes = isbn
        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.isbn_search(isbn)
        
    
    

    def title_search(self, search:str) -> List[Book]:
        """Search books from there title.

        Args:
            search (str): Title of the book.

        Returns:
            List[Book]: List of books with the title as search.
        """
        
        params = (
            ("req", search),
            ("open", "0"),
            ("res", f"{self.count}"),
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
        self.used_search = self.title_search
        self.attributes = search
        if response.status_code == 200:
            return self._parse_data(response.text)
        print("Request failed with status code: {}".format(response.status_code))
        sleep(5)
        self.title_search(search)
        

        
    def filter(self,filters:Dict[Filter,List[Any]|str|int])->List[Book]:
        """
        You can filter the books by multiple filters. You can import the filters enum from the helper.py file.
        
        For year,pages,size you can specify a range by sending a tuple of two numbers.
        
        
        Example:
        
        year_fil = {
            Filter.year: (2000,2020),
        }
        
        For other filters you can send a single value or a list of values.
        
    
        Author_year_fil={
            Filter.Author:['author name','author name2']    ,
            Filter.year:[2020,2021]

        }

        Args:
            filters (Dict[Filter,List[Any]]): List of filters to filter the books by.
        """
        
        for filter in filters:
            key,value = list(filter.items())[0]
            self.inner_filter(
                filter=key,
                arg=value
            )
        return self.books
    

    def inner_filter(self,filter: Filter, arg: Tuple|List):
        """filter the books by the filter and the arg.

        Args:
            filter (Filter): one filter
            arg (Tuple | List)
        """
        
        if type(arg) in (str,int,float):
            self.books = [book for book in self.books if getattr(book, filter.value) == arg]
        elif len(arg) == 1:
            self.books = [book for book in self.books if getattr(book, filter.value) == arg[0]]
        elif len(arg) == 2 and type(arg) == tuple:
            # if filter in [Filter.author,Filter.extension,Filter.publisher,Filter.language]:
            #     self.books = [book for book in self.books if getattr(book,filter.value) in arg]
            if filter in [Filter.year,Filter.pages,Filter.size]:
                self.books = [book for book in self.books if getattr(book,filter.value) <= arg[0] and getattr(book,filter.value) >= arg[1]]
        else:
            self.books = [book for book in self.books if getattr(book,filter.value) in arg]

     
            
        

    def _parse_data(self, data: str) -> List[Book]:
        """Inner method to parse the data.

        Args:
            data (str): data to parse from response

        Returns:
            List[Book]: List of books
        """
        
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
            temp = self.helper._parse_mirrors(mirrors[0])
            books.append(
                Book(
                    row.find_all("td")[2].text,
                    row.find_all("td")[1].text,
                    row.find_all("td")[0].text,
                    row.find_all("td")[3].text,
                    self.helper._refactor_year(row.find_all("td")[4].text),
                    self.helper._refactor_pages(row.find_all("td")[5].text),
                    row.find_all("td")[6].text,
                    self.helper._refactor_size(row.find_all("td")[7].text),
                    row.find_all("td")[8].text,
                    mirrors,
                    temp.get("image"),
                    temp.get("description"),
                    temp.get("source"),
                )
            )
        self.books = books
        return books



if __name__ == "__main__":
    lib = Search()
    books = lib.title_search("Atomic Habits")
    pprint(books)
    # books[1].download()