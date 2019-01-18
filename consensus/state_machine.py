

def execute_operation(state, operation):
    """State machine"""

    if operation.name == 'deposit':
        if not verify_signature(operation.deposit_signature):
            return state, False
        state.accounts[operation.destination_account] += operation.amount
        return state, True
    elif operation.name == 'transfer':
        if state.accounts[operation.source_account] < operation.amount:
            return state, False
        state.accounts[operation.source_account] -= operation.amount
        state.accounts[operation.destination_account] += operation.amount
        return state, True
    elif operation.name == 'get-balance':
        return state, state.accounts[operation.account]
