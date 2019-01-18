# Cluster roles are:
# Acceptor -- make promises and accept proposals
# Replica -- manage the distributed state machine: submitting proposals, committing decisions, responding to requesters
# Leader -- lead rounds of the Multi-Paxos algorithm
# Scout -- perform the Prepare/Promise portion of the Multi-Paxos algorithm for a leader
# Commander -- perform the Accept/Accepted portion of the Multi-Paxos algorithm for a leader
# Bootstrap -- introduce a new node to an existing cluster
# Seed -- create a new cluster
# Requester -- request a distributed state machine operation

# TODO