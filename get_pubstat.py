try: 
    import requests
    import argparse
    from urllib.parse import urlencode

    def calculate_h_index(citations):
        '''
        calculate the h-index based on the citation list
        '''
        citations.sort(reverse=True)
        h_index = 0
        for i, citation in enumerate(citations):
            if citation >= i + 1:
                h_index = i + 1
            else:
                break
        return h_index
    
    def get_pubstat(ads_token, library_id, name):
        '''
        Count the number of publications and the number of citations
        '''
        encoded_query = urlencode({'q': f'docs(library/{library_id})',
                                'fl': 'first_author, author, citation_count',
                                'sort': 'pubdate+desc',
                                'rows': 1000
                                })
        results = requests.get(f'https://api.adsabs.harvard.edu/v1/search/query?{encoded_query}', headers={'Authorization': 'Bearer ' + ads_token})
        publist = results.json()['response']['docs']
        # counts
        paper_count = len(publist)
        citation_count_first = sum([pub['citation_count'] for pub in publist if name in pub['first_author']])
        citation_count = sum([pub['citation_count'] for pub in publist])
        h_index = calculate_h_index([pub['citation_count'] for pub in publist])
        # prepare output
        out = f'total count = {paper_count}, total citation = {citation_count}, first-author citation = {citation_count_first}, h-index = {h_index} (based on ADS)'
        print(out)

    def main():
        parser = argparse.ArgumentParser(description='Fetch publication list from an ADS library.')
        parser.add_argument('--ads_token', required=True, help='Your ADS API token')
        parser.add_argument('--library_id', required=True, help='Library ID in ADS')
        parser.add_argument('--name', required=True, help='Name of interest, optional')

        args = parser.parse_args()

        get_pubstat(args.ads_token, args.library_id, args.name)

    if __name__ == '__main__':
        main()

except Exception as e: 
    print(repr(e))