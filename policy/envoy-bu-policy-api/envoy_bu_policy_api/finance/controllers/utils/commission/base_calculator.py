from services.SettingService import SettingService
import ast

def _get_agent_commission_config():
    """
    Fetch and parse the agent commission config from settings.
    Returns:
        str or None: 'totalpremium', 'paid', or None
    """
    config_value = SettingService.getSettingKeyValue('COMMISSION_CONFIG')
    if config_value:
        try:
            config_dict = ast.literal_eval(config_value)
            return config_dict.get('agent_commission_config')
        except Exception:
            return None
    return None

def get_commission_calculation_mode(calculation_mode=None):
    """
    Utility to determine commission calculation mode based on argument and config.
    Args:
        calculation_mode (str, optional): Explicit calculation mode if provided.
    Returns:
        str: 'premium' or 'paid'
    """
    if calculation_mode:
        return calculation_mode
    agent_commission_config = _get_agent_commission_config()
    if agent_commission_config:
        if agent_commission_config.lower() == 'totalpremium':
            return 'premium'
        elif agent_commission_config.lower() == 'paid':
            return 'paid'
    return 'premium'  # Default fallback

def calculate_commission_base_amount(invoice_amount, paid_amount, calculation_mode=None):
    """
    Calculate base amount for commission calculation
    Args:
        invoice_amount (Decimal): Total invoice amount
        paid_amount (Decimal): Amount paid so far
        calculation_mode (str, optional): 'premium' or 'paid'. Must be provided explicitly.
    Returns:
        Decimal: Base amount for commission calculation
    """
    mode = get_commission_calculation_mode(calculation_mode)
    if mode == 'paid':
        return paid_amount
    return invoice_amount 