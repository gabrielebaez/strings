from time import time
import hashlib
import json


class Journal:

    def __init__(self):
        self.journal = []
        self.current_entries = []
        self.nodes = set()

        # Initial Journal page
        self.new_page(previous_hash=1)

    def new_page(self, previous_hash=None):
        """
        Adds a new page to the journal.
        :param previous_hash: (Optional) <str> Hash of previous page
        :return: <dict> New Page
        """

        page = {
            'index': len(self.journal) + 1,
            'timestamp': time(),
            'entries': self.current_entries,
            'previous_hash': previous_hash or self.last_page['hash'],
            'hash': 1 if len(self.journal) < 1 else self.hash(self.current_entries)
        }

        # reset current list of entries
        self.current_entries = []
        self.journal.append(page)
        return page

    def new_entry(self, data):
        """
        Add data to a page.

        :param data: <Dict>
        :return: <int> The index of the Page that will hold this data
        """
        self.current_entries.append(data)
        return self.last_page['index'] + 1

    @property
    def last_page(self):
        return self.journal[-1]

    @staticmethod
    def hash(page):
        """
        Creates a SHA-256 hash of a Page
        :param page: <dict> Page
        :return: <str>
        """
        page_string = json.dumps(page, sort_keys=True).encode()
        return hashlib.sha256(page_string).hexdigest()

    def valid_journal(self, journal):
        """
        Determine if a given journal is valid.

        :param journal: <list>
        :return: <bool> True if valid, False if not
        """

        last_page = journal[0]
        current_index = 1

        while current_index < len(journal):
            page = journal[current_index]

            #check if the hash of the page is correct
            if page['previous_hash'] != self.hash(last_page):
                return False

            last_page = page
            current_index += 1

        return True


if __name__ == '__main__':
    j = Journal()

    j.new_entry({'a': 1})
    j.new_page()

    j.new_entry({'b': 1})
    j.new_page()

    j.new_entry({'c': 1})
    j.new_page()

    j.new_entry({'d': 1})
    j.new_page()

    for page in j.journal:
        print(page)

    print(f"Journal len {len(j.journal)}")
