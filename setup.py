from setuptools import setup, find_packages
from tqdm import tqdm

VERSION = '0.0.1' 
DESCRIPTION = 'Package for searching books in Libgen'
LONG_DESCRIPTION = """ 
Package for searching books in Libgen 
You can search by 
> Title
> Author
> ISBN
You can filter the books by multiple filters. 
You can import the Filter enum from the helper.py file.
You can Filter using
> Year
> Pages
> Size
> Extension
> Publisher
> Language
> Author

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

"""

# Setting up
setup(

        name="LibgenPy", 
        version=VERSION,
        author="Priyam Srivastava",
        author_email="ipriyam26@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["tqdm","bs4","requests"], # add any additional packages that 

        
        keywords=['python', 'library-genesis', 'libgen', 'book', 'search', 'download'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)