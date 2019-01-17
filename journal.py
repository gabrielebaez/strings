from typing import Optional
from time import time
import logging
import hashlib
import json


class Journal:

    def __init__(self, journal_name: Optional[str] = None) -> None:
        self.journal = []
        self.current_entries = []
        self.metadata = {}

        if journal_name:
            self.metadata['name'] = journal_name

    def genesis(self):
        """Generates the first page of a new Journal"""

        if len(self.journal) == 0:
            self.new_page(previous_hash='none')

    def new_page(self, previous_hash: Optional[str] = None) -> dict:
        """Adds a new page to the journal."""

        page = {
            'index': len(self.journal) + 1,
            'timestamp': time(),
            'entries': self.current_entries,
            'previous_hash': previous_hash or self.last_page['hash'],
        }

        page['hash'] = self.hash(page)

        # reset current list of entries
        self.current_entries = []
        self.journal.append(page)
        return page

    def new_entry(self, data: dict) -> int:
        """
        Add data to a page.

        :param data:
        :return: The index of the Page that will hold this data
        """

        try:
            assert len(self.journal) > 0

            self.current_entries.append(data)
            return self.last_page['index'] + 1

        except AssertionError:
            logging.critical("Journal not initialized, try running the genesis function")

    @property
    def last_page(self) -> int:
        return self.journal[-1]

    @staticmethod
    def hash(page: dict) -> str:
        """
        Creates a SHA-256 hash of a Page
        :param page: <dict> Page
        :return: hash
        """
        page_string = json.dumps(page, sort_keys=True).encode()
        return hashlib.sha256(page_string).hexdigest()

    @staticmethod
    def validate_journal(journal: list) -> bool:
        """Determine if a given journal is valid."""

        hashes_a = []
        hashes_b = []

        for page in journal:
            hashes_a.append(page['previous_hash'])
            hashes_b.append(page['hash'])
        hashes_b.insert(0, 'none')

        for previous, current in zip(hashes_a, hashes_b):
            if previous != current:
                return False

        return True


if __name__ == '__main__':
    j = Journal(journal_name="aaa")

    print(j.metadata)
    j.genesis()

    j.new_entry({'a': 1, 'b': 1})
    j.new_entry({'a': 1, 'b': 1})
    j.new_entry({'c': 1, 'd': 1})
    j.new_page()

    j.new_entry({'a': 1,'b': 1})
    j.new_page()

    j.new_entry({'b': 1})
    j.new_page()

    j.new_entry({'c': 1,'d': 1})
    j.new_page()

    j.new_entry({'d': 1})
    j.new_page()

    for page in j.journal:
        print(page)

    print(f"Journal len {len(j.journal)}")

    print(f'Is a valid journal? {j.validate_journal(j.journal)}')
