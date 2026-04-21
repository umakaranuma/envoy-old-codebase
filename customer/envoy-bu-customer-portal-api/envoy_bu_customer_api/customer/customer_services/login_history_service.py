from mServices import QueryBuilderService
from datetime import datetime


def log_customer_login(customer_id, device=None, ip=None, location=None,email=None):
    """
    Log a customer login event to the core_login_histories table.
    Args:
        customer_id (int): The ID of the customer logging in.
        device (str, optional): Device info.
        ip (str, optional): IP address.
        location (str, optional): Location string.
    """
    now = datetime.now()
    data = {
        'user_id': None,
        'customer_id': customer_id,
        'login_time': now.strftime('%H:%M:%S'),
        'device': device,
        'ip': ip,
        'location': location,
        'module': 'customer',
        'email':email,
        'created_at': now,
        'updated_at': now,
    }
    QueryBuilderService('core_login_histories').insert(data)
