TRANSACTION_TYPES = [
    {
        "id": 1,
        "name": "New Business",
        "description": "New policy issuance",
        "note_types": ["Debit Note"],
        "commission": True
    },
    {
        "id": 2,
        "name": "Addition",
        "description": "Additional coverage or premium",
        "note_types": ["Debit Note"],
        "commission": True
    },
    {
        "id": 3,
        "name": "Renewal",
        "description": "Policy renewed after expiry like new business",
        "note_types": ["Debit Note"],
        "commission": True
    },
    {
        "id": 4,
        "name": "Refund",
        "description": "Premium refund or reversal",
        "note_types": ["Credit Note"],
        "commission": False
    },
    {
        "id": 5,
        "name": "Cancellations",
        "description": "Policy cancellation before expiry",
        "note_types": ["Credit Note"],
        "commission": False
    },
    {
        "id": 6,
        "name": "Non-Financials",
        "description": "Non-monetary changes like address or name update",
        "note_types": [],
        "commission": False
    }
]

def get_transaction_type_by_id(type_id):
    """Get transaction type configuration by ID"""
    return next((t for t in TRANSACTION_TYPES if t["id"] == type_id), None)

def get_transaction_type_by_name(name):
    """Get transaction type configuration by name"""
    return next((t for t in TRANSACTION_TYPES if t["name"].lower() == name.lower()), None)

def get_note_type_for_transaction(type_id):
    """Get the appropriate note type for a transaction type"""
    transaction = get_transaction_type_by_id(type_id)
    if not transaction or not transaction["note_types"]:
        return None
    return transaction["note_types"][0]  # Return first note type

def is_commissionable(type_id):
    """Check if this transaction type is commissionable"""
    transaction = get_transaction_type_by_id(type_id)
    return transaction["commission"] if transaction else False