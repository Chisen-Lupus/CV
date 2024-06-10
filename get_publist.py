try: 
    import requests
    import argparse
    from urllib.parse import urlencode

    def reformat_name(name):
        '''
        Reformat names from 'Last, First' to 'First Last'
        '''
        parts = name.split(',')
        return f"{parts[1].strip()} {parts[0].strip()}" if len(parts) == 2 else name

    def format_latex_publication(pub, name): 
        '''
        Transform a json-like publication list to items in \LaTeX
        Bold the author 
        '''
        authors = ', '.join(
            f'\\textbf{{{reformat_name(author)}}}' if name in author else reformat_name(author)
            for author in pub['author']
        )
        title = pub['title'][0]
        doi_link = f"https://doi.org/{pub['doi'][0]}"
        formatted_title = f"\\href{{{doi_link}}}{{``{title},''}}"
        pubname = pub['pub']
        volume = pub['volume'] if 'volume' in pub else ''
        page = pub['page'][0] if 'page' in pub else ''
        year = pub['year']
        latex_item = f"\\item {authors}, {formatted_title} {pubname} {volume}, {page} ({year})"
        return latex_item

    def get_publications(ads_token, library_id, name=None, first_author=None):
        '''
        Get publications providing ads_token, library_id, and the author of interest, and then print the output as a \LaTeX list.
        '''
        if name is None: name = '_'
        encoded_query = urlencode({"q": f'docs(library/{library_id})',
                                "fl": 'first_author, author, title, pub, volume, pubdate, year, page, doi',
                                'sort': 'pubdate+desc',
                                "rows": 1000
                                })
        results = requests.get(f'https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}', headers={'Authorization': 'Bearer ' + ads_token})
        publist = results.json()['response']['docs']
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
        parser.add_argument("--ads_token", required=True, help="Your ADS API token")
        parser.add_argument("--library_id", required=True, help="Library ID in ADS")
        parser.add_argument("--name", help="Name of interest, optional")
        parser.add_argument("--first_author", help="First author only (True) or excluded (False); print all if not specified, optional")

        args = parser.parse_args()

        if args.first_author is not None: 
            args.first_author = bool(eval(args.first_author))

        get_publications(args.ads_token, args.library_id, args.name, args.first_author)

    if __name__ == "__main__":
        main()

except Exception as e: 
    print(repr(e))