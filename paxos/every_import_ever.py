from dotenv import find_dotenv, load_dotenv
from collections import namedtuple
import itertools
import functools
import threading
import queue
import os

load_dotenv(find_dotenv())

# protocol description
Proposal = namedtuple('Proposal', ['caller', 'client_id', 'input'])
Ballot = namedtuple('Ballot', ['n', 'leader'])

# constants
JOIN_RETRANSMIT = os.getenv("JOIN_RETRANSMIT")
CATCHUP_INTERVAL = os.getenv('CATCHUP_INTERVAL')
ACCEPT_RETRANSMIT = os.getenv('ACCEPT_RETRANSMIT')
PREPARE_RETRANSMIT = os.getenv('PREPARE_RETRANSMIT')
INVOKE_RETRANSMIT = os.getenv('INVOKE_RETRANSMIT')
LEADER_TIMEOUT = os.getenv('LEADER_TIMEOUT')
NULL_BALLOT = Ballot(-1, -1)  # sorts before all real ballots
NOOP_PROPOSAL = Proposal(None, None, None)  # no-op to fill otherwise empty slots

# Messages
Accepted = namedtuple('Accepted', ['slot', 'ballot_num'])
Accept = namedtuple('Accept', ['slot', 'ballot_num', 'proposal'])
Decision = namedtuple('Decision', ['slot', 'proposal'])
Invoked = namedtuple('Invoked', ['client_id', 'output'])
Invoke = namedtuple('Invoke', ['caller', 'client_id', 'input_value'])
Join = namedtuple('Join', [])
Active = namedtuple('Active', [])
Prepare = namedtuple('Prepare', ['ballot_num'])
Promise = namedtuple('Promise', ['ballot_num', 'accepted_proposals'])
Propose = namedtuple('Propose', ['slot', 'proposal'])
Welcome = namedtuple('Welcome', ['state', 'slot', 'decisions'])
Decided = namedtuple('Decided', ['slot'])
Preempted = namedtuple('Preempted', ['slot', 'preempted_by'])
Adopted = namedtuple('Adopted', ['ballot_num', 'accepted_proposals'])
Accepting = namedtuple('Accepting', ['leader'])
