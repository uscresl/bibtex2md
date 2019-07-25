import argparse
from datetime import datetime
import os
import subprocess

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import *
import copy


"""
bib2md: Convert collection of bibtex files to clean markdown script

markdown parser command: test.tex + mybib.bib --> test.md
pandoc -S -f latex -t markdown-native_divs-raw_html-citations --filter=pandoc-citeproc --bibliography=mybib.bib --wrap=none -o test.md test.tex
"""

BUILD_ROOT = 'build'
BIB_ROOT = 'bib'
TEX_FILE = 'skeleton.tex'


def customizations(record):
    """
    Use some functions delivered by the library

    @type record: record
    @param record: a record
    @rtype: record
    @returns: -- customized record
    """

    record = type(record)
    # record = author(record)
    record = convert_to_unicode(record)
    # record = editor(record)
    # record = journal(record)
    # record = keyword(record)
    # record = link(record)
    # record = page_double_hyphen(record)
    # record = doi(record)
    return record

def merge_bibtex(files, build_dir):
    """
    Merging with a subprocess call to bibtool.

    Does not handle duplicates or bibtool warnings!

    @type files: bibtex files
    @param files: bibtex files to be merged
    @type build_dir: file path
    @param build_dir: where to save
    @rtype: .bib file
    @returns: merged file
    """

    merge_file = os.path.join(build_dir, 'merged.bib')
    with open(merge_file, 'w') as f:
        cp = subprocess.run(['bibtool', '-s'] + files, stdout=f, check=True)
    return merge_file 

def parse_bibtex(file, build_dir):
    """
    Parse merged bibtex file again with customization to clean citations.
    
    @type file: .bib file
    @param file: file to be parsed
    @type build_dir: file path
    @param build_dir: where to save
    """

    parser = BibTexParser()
    parser.customization = customizations
    years = []
    with open(file, 'r') as f: 
        bibtex = bibtexparser.load(f, parser=parser)
        for i in range (len(bibtex.entries)):
            for key, value in bibtex.entries[i].items():
                if key == 'year':
                    years.append(int(value))
    years.sort()
    years.reverse()
    years_no_repeat = []
    for i in range(len(years)):
        if years_no_repeat.count(years[i]) == 0:
            years_no_repeat.append(years[i])
     
    for i in range(len(years_no_repeat)):
        bibtext = copy.deepcopy(bibtex)
        array = []
        for j in range (len(bibtex.entries)):
            for key, value in bibtex.entries[j].items():
                if key == 'year':
                    if int(value) == years_no_repeat[i]:
                        array.append(bibtex.entries[j])
        bibtext.entries = array
        parse_file = os.path.join(build_dir, str(years_no_repeat[i]) + 'parsed.bib')
        writer = BibTexWriter()
        writer.order_entries_by = ('ENTRYTYPE', )
        with open(parse_file, 'w') as f:
            f.write(writer.write(bibtext))
        


def render_bibtex(file, build_dir, output_file):
    """
    Renders parsed bibtex to markdown file using pandoc.

    @type file: .bib file
    @param file: the file to be rendered to markdown
    @type build_dir: file path 
    @param build_dir: where to save
    @type output_file: .md file
    @param output_file: the markdown file
    """

    render_file = os.path.join(build_dir, output_file)
    with open(render_file, 'w') as f:
        cp = subprocess.run([ 
                    'pandoc',
                    '-f', 'latex+smart',
                    '-t', 'markdown-raw_html-citations+smart',
                    '--filter=pandoc-citeproc',
                    '--bibliography=' + file,
                    '--wrap=none',
                    '-o', render_file,
                    TEX_FILE],
                check=True)

def main():
    """
    Execute purpose of the class using other methods
    """

    parser = argparse.ArgumentParser(
        description='Convert collection of bibtex files to clean markdown script.')
    parser.add_argument('-i', '--input', nargs='+', required=False,
        help='Input bibtex files. Defaults to bib/*')
    parser.add_argument('-o', '--output', default='publications.md', required=False,
        help='Output markdown floadile.')
    args = parser.parse_args()

    # Build setup
    os.makedirs(BUILD_ROOT, exist_ok=True)
    build_dir = os.path.join(
        BUILD_ROOT,
        datetime.now().strftime(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')))
    os.makedirs(build_dir)

    # Find and merge all bibtex files
    input_files = args.input
    if input_files is None:
        input_files = [os.path.join(BIB_ROOT, f) for f in os.listdir(BIB_ROOT)
                        if os.path.isfile(os.path.join(BIB_ROOT, f))]
    merge_file = merge_bibtex(input_files, build_dir)

    # Parse merged bibtex file with custom options
    parse_file = parse_bibtex(merge_file, build_dir)

    # Render bibtex to markdown
    render_file = render_bibtex(parse_file, build_dir, args.output) 

if __name__ == '__main__':
    main()
