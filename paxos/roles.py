from .every_import_ever import *


# To encourage testability and keep the code readable,
# we break Cluster down into a handful of classes corresponding to the roles described in the protocol.
# Each is a subclass of Role
class Role:
    """ Base class, everyone inherits from here """

    def __init__(self, node):
        self.node = node
        self.node.register(self)
        self.running = True
        self.logger = node.logger.getChild(type(self).__name__)

    def set_timer(self, seconds, callback):
        return self.node.network.set_timer(self.node.address, seconds,
                                           lambda: self.running and callback())

    def stop(self):
        self.running = False
        self.node.unregister(self)


class Acceptor(Role):
    """ make promises and accept proposals """

    def __init__(self, node):
        super(Acceptor, self).__init__(node)
        self.ballot_num = NULL_BALLOT
        self.accepted_proposals = {} # {slot: (ballot_num, proposal)}

    def do_prepare(self, sender, ballot_num):
        if ballot_num > self.ballot_num:
            self.ballot_num = ballot_num
            # we've heard from a scout, so it might be the next leader
            self.node.send([self.node.address], Accepting(leader=sender))

        self.node.send([sender], Promise(
            ballot_num = self.ballot_num,
            accepted_proposals = self.accepted_proposals))

    def do_accept(self, sender, ballot_num, slot, proposal):
        if ballot_num >= self.ballot_num:
            self.ballot_num = ballot_num
            acc = self.accepted_proposals
            if slot not in acc or acc[slot][0] < ballot_num:
                acc[slot] = (ballot_num, proposal)

        self.node.send([sender], Accepted(
            slot = slot,
            ballot_num = self.ballot_num))


class Replica(Role):
    """ manage the distributed state machine: submitting proposals, committing decisions, responding to requesters """

    def __init__(self, node, execute_fn, state, slot, decisions, peers):
        super(Replica, self).__init__(node)
        self.execute_fn = execute_fn
        self.state = state
        self.slot = slot
        self.decisions = decisions
        self.peers = peers
        self.proposals = {}
        self.next_slot = slot # next slot num for a proposal (may lead slot)
        self.latest_leader = None
        self.latest_leader_timeout = None

    # making proposals

    pass

    # handling decided proposals

    pass

    # tracking the leader

    pass

    # adding new cluster members

    pass


class Leader(Role):
    """ lead rounds of the Multi-Paxos algorithm """
    pass


class Scout(Role):
    """ perform the Prepare/Promise portion of the Multi-Paxos algorithm for a leader """
    pass


class Commander(Role):
    """ perform the Accept/Accepted portion of the Multi-Paxos algorithm for a leader """
    pass


class Bootstrap(Role):
    """ introduce a new node to an existing cluster """
    pass


class Seed(Role):
    """ create a new cluster """
    pass


class Requester(Role):
    """ request a distributed state machine operation """
    pass
