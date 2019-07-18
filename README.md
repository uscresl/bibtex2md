# bibtex2md

Take a list of bibtex files and output a clean bibliography in markdown script, with entries grouped by year.

## Installation

Requires some bibtex parsing tools
```
apt-get install pandoc pandoc-citeproc bibtool
```

Python dependencies can be installed via pipenv
```
pipenv install --dev
```

## Usage

Simply run `python main.py`

## TODO:

- Fix formatting of authors list. Doesn't convert to string properly.
    - Solution: Create custom author() customization
    - Keep format First M. Last
- Explore DOI parsing - can we automatically insert a doi link?
- Extract year tag if it doesn't exist
- Split bibtex db by year
- Implement full markdown rendering
- Explore rendering in different styles with pandoc
