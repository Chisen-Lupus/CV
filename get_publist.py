try: 
    import requests
    import argparse
    from urllib.parse import urlencode
    from pylatexenc.latexencode import utf8tolatex

    def format_name(name, name_of_interest):
        '''
        Reformat names from 'Last, First' to 'First Last', translating its character to \LaTeX format
        '''
        parts = name.split(',')
        if len(parts)==1:
            formatted_name = f'{parts[0].strip()}'
        else:
            formatted_name = f'{parts[1].strip()} {parts[0].strip()}'
        if name_of_interest in name:
            return f'\\textbf{{{utf8tolatex(formatted_name)}}}'
        else: 
            return utf8tolatex(formatted_name)
    
    def format_authors(authors, name_of_interest):
        '''
        Reformat and check for the name of interest
        '''
        formatted_authors = [format_name(author, name_of_interest) for author in authors]
        formatted_name_of_interest = next((author for author in formatted_authors if '\\textbf' in author), None)
        if len(formatted_authors) == 2:
            return ' & '.join(formatted_authors)
        elif len(formatted_authors) > 3:
            first_three = ', '.join(formatted_authors[:3])
            others = ', '.join(formatted_authors[3:])
            if formatted_name_of_interest is not None and formatted_name_of_interest in others:
                return f'{first_three}, et al. (incl. {formatted_name_of_interest})'
            else:
                return f'{first_three}, et al.'
        else:
            return ', '.join(formatted_authors)

    def format_latex_publication(pub, name): 
        '''
        Transform a json-like publication list to items in \LaTeX
        Bold the author 
        '''
        authors = format_authors(pub['author'], name)
        title = utf8tolatex(pub['title'][0])
        if 'doi' in pub.keys(): 
            doi_link = f"https://doi.org/{pub['doi'][0]}"
            formatted_title = f"\\href{{{doi_link}}}{{``{title},''}}"
        else: 
            formatted_title = f"``{title},''"
        pubname = pub['pub']
        volume = ' ' + pub['volume'] if 'volume' in pub else ''
        page = ', ' + pub['page'][0] if 'page' in pub else ''
        year = pub['year']
        return f'\\item {authors}, {formatted_title} \\textit{{{pubname}{volume}}}{page} ({year})'

    def get_publications(ads_token, library_id, name=None, first_author=None):
        '''
        Get publications providing ads_token, library_id, and the author of interest, and then print the output as a \LaTeX list.
        '''
        if name is None: name = '_'
        # query information
        encoded_query = urlencode({'q': f'docs(library/{library_id})',
                                'fl': 'first_author, author, title, pub, volume, pubdate, year, page, doi',
                                'sort': 'pubdate+desc',
                                'rows': 1000
                                })
        results = requests.get(f'https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}', headers={'Authorization': 'Bearer ' + ads_token})
        publist = results.json()['response']['docs']
        # prepare output
        publist = sorted(publist, key=lambda x: x['pubdate'], reverse=True)
        out = ''
        if first_author is True: 
            for pub in publist: 
                if name in pub['first_author']: 
                    out += format_latex_publication(pub, name) + '\n'
        elif first_author is False: 
            for pub in publist: 
                if name not in pub['first_author']: 
                    out += format_latex_publication(pub, name) + '\n'
        else: 
            for pub in publist: 
                out += format_latex_publication(pub, name) + '\n'
        print(out)

    def main():
        parser = argparse.ArgumentParser(description='Fetch publication list from an ADS library.')
        parser.add_argument('--ads_token', required=True, help='Your ADS API token')
        parser.add_argument('--library_id', required=True, help='Library ID in ADS')
        parser.add_argument('--name', help='Name of interest, optional')
        parser.add_argument('--first_author', help='First author only (True) or excluded (False); print all if not specified, optional')

        args = parser.parse_args()

        if args.first_author is not None: 
            args.first_author = bool(eval(args.first_author))

        get_publications(args.ads_token, args.library_id, args.name, args.first_author)

    if __name__ == '__main__':
        main()

except Exception as e: 
    print(repr(e))