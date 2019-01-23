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

    def do_invoke(self, sender, caller, client_id, input_value):
        proposal = Proposal(caller, client_id, input_value)
        slot = next((s for s, p in self.proposals.iteritems() if p == proposal), None)
        # propose, or re-propose if this proposal already has a slot
        self.propose(proposal, slot)

    def propose(self, proposal, slot=None):
        """Send (or resend, if slot is specified) a proposal to the leader"""
        if not slot:
            slot, self.next_slot = self.next_slot, self.next_slot + 1
        self.proposals[slot] = proposal
        # find a leader we think is working - either the latest we know of, or
        # ourselves (which may trigger a scout to make us the leader)
        leader = self.latest_leader or self.node.address
        self.logger.info(
            "proposing %s at slot %d to leader %s" % (proposal, slot, leader))
        self.node.send([leader], Propose(slot=slot, proposal=proposal))

    # handling decided proposals

    def do_decision(self, sender, slot, proposal):
        assert not self.decisions.get(self.slot, None), \
                "next slot to commit is already decided"
        if slot in self.decisions:
            assert self.decisions[slot] == proposal, \
                "slot %d already decided with %r!" % (slot, self.decisions[slot])
            return
        self.decisions[slot] = proposal
        self.next_slot = max(self.next_slot, slot + 1)

        # re-propose our proposal in a new slot if it lost its slot and wasn't a no-op
        our_proposal = self.proposals.get(slot)
        if (our_proposal is not None and
                our_proposal != proposal and our_proposal.caller):
            self.propose(our_proposal)

        # execute any pending, decided proposals
        while True:
            commit_proposal = self.decisions.get(self.slot)
            if not commit_proposal:
                break  # not decided yet
            commit_slot, self.slot = self.slot, self.slot + 1

            self.commit(commit_slot, commit_proposal)

    def commit(self, slot, proposal):
        """Actually commit a proposal that is decided and in sequence"""
        decided_proposals = [p for s, p in self.decisions.iteritems() if s < slot]
        if proposal in decided_proposals:
            self.logger.info(
                "not committing duplicate proposal %r, slot %d", proposal, slot)
            return  # duplicate

        self.logger.info("committing %r at slot %d" % (proposal, slot))
        if proposal.caller is not None:
            # perform a client operation
            self.state, output = self.execute_fn(self.state, proposal.input)
            self.node.send([proposal.caller],
                           Invoked(client_id=proposal.client_id, output=output))

    # tracking the leader

    def do_adopted(self, sender, ballot_num, accepted_proposals):
        self.latest_leader = self.node.address
        self.leader_alive()

    def do_accepting(self, sender, leader):
        self.latest_leader = leader
        self.leader_alive()

    def do_active(self, sender):
        if sender != self.latest_leader:
            return
        self.leader_alive()

    def leader_alive(self):
        if self.latest_leader_timeout:
            self.latest_leader_timeout.cancel()

        def reset_leader():
            idx = self.peers.index(self.latest_leader)
            self.latest_leader = self.peers[(idx + 1) % len(self.peers)]
            self.logger.debug("leader timed out; tring the next one, %s",
                              self.latest_leader)

        self.latest_leader_timeout = self.set_timer(LEADER_TIMEOUT, reset_leader)

    # adding new cluster members

    def do_join(self, sender):
        if sender in self.peers:
            self.node.send([sender], Welcome(
                state=self.state,
                slot=self.slot,
                decisions=self.decisions))


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
