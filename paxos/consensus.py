from .every_import_ever import *

# this is a work through the chapter "Cluster by consensus" from the book "500 lines or less"
# and will be modify for the ledger.

# The roles that a cluster node has are glued together by the Node class, which represents a single node on the network.
# Roles are added to and removed from the node as execution proceeds.
# Messages that arrive on the node are relayed to all active roles,
# calling a method named after the message type with a do_ prefix.
# These do_ methods receive the message's attributes as keyword arguments for easy access.
# The Node class also provides a send method as a convenience, using functools.
# partial to supply some arguments to the same methods of the Network class.


class Node:
    unique_ids = itertools.count()

    def __init__(self, network, address):
        self.network = network
        self.address = address or f'N{self.unique_ids.next()}'
        self.logger = SimTimeLogger(
            logging.getLogger(self.address), {'network': self.network})
        self.logger.info('starting')
        self.roles = []
        self.send = functools.partial(self.network.send, self)

    def register(self, roles):
        self.roles.append(roles)

    def unregister(self, roles):
        self.roles.remove(roles)

    def receive(self, sender, message):
        handler_name = f'do_{type(message).__name__}'

        for comp in self.roles[:]:
            if not hasattr(comp, handler_name):
                continue
            comp.logger.debug(f'received {message} from {sender}')
            fn = getattr(comp, handler_name)
            fn(sender=sender, **message._asdict())

##
#
# Application interface
#
##

# The application creates and starts a Member object on each cluster member,
# providing an application-specific state machine and a list of peers.
# The member object adds a bootstrap role to the node if it is joining an existing cluster,
# or seed if it is creating a new cluster.
# It then runs the protocol (via Network.run) in a separate thread.
#
# The application interacts with the cluster through the invoke method,
# which kicks off a proposal for a state transition. Once that proposal is decided and the state machine runs,
# invoke returns the machine's output.
# The method uses a simple synchronized Queue to wait for the result from the protocol thread.


class Member:

    def __init__(self, state_machine, network, peers, seed=None,
                 seed_cls=Seed, bootstrap_cls=Bootstrap):
        self.network = network
        self.node = network.new_node()
        if seed is not None:
            self.startup_role = seed_cls(self.node, initial_state=seed,
                                         peers=peers, execute_fn=state_machine)
        else:
            self.startup_role = bootstrap_cls(self.node,
                                              execute_fn=state_machine, peers=peers)

        self.requester = None

    def start(self):
        self.startup_role.start()
        self.thread = threading.Thread(target=self.network.run)
        self.thread.start()

    def invoke(self, input_value, request_cls=Requester):
        assert self.requester is None
        q = queue.Queue()
        self.requester = request_cls(self.node, input_value, q.put)
        self.requester.start()
        output = q.get()
        self.requester = None
        return output
