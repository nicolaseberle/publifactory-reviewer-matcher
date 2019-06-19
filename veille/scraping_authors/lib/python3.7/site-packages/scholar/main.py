from argparse import ArgumentParser
from prettytable import PrettyTable
from .scholar import Scholar
import sys

try:
    from builtins import input
except Exception as e:
    print(e)


def main():
    parser = ArgumentParser()
    parser.add_argument('discipline',
                        help='The study discipline.')
    parser.add_argument('query',
                        help='The search query.',
                        nargs='?')
    parser.add_argument('show_all',
                        default='False',
                        nargs='?',
                        help='Set show_all to False to retrieve preview only content.')
    parser.add_argument('page',
                        default='1',
                        nargs='?',
                        help='The page number.')
    args = parser.parse_args()
    scholar = Scholar()
    articles = scholar.search(discipline=args.discipline, query=args.query, show_all=args.show_all, page=args.page)
    if not int(scholar.num_results) > 0:
        return False
    row = PrettyTable()
    row.field_names = ["Id", "Title", "Authors"]
    row.align = 'l'
    count = 1
    for article in articles:
        row.add_row([count, article.title, ', '.join(author for author in article.authors)])
        count += 1
    print(row)
    while 1:
        print("You can download a specific article by selecting its id. Run s or save_all to download all files.")
        read = input().lower()
        if read == 's' or read == 'save_all':
            for article in articles:
                scholar.download(article.pdf_link, article.title)
            sys.exit(1)
        try:
            int_val = int(read)
        except (ValueError, TypeError) as error:
            print(error)
            continue
        count = 1
        for article in articles:
            if count == int_val:
                scholar.download(article.pdf_link, article.title)
                sys.exit(1)
            count += 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
