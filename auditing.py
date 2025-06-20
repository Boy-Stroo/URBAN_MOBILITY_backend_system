from functools import wraps
import data_access as da
from models import User
import inspect

# Create a single instance of DataAccess
data_access_instance = da.DataAccess()


def _get_user_from_args(*args, **kwargs):
    """Finds the User object from the function's arguments."""
    # Prioritize 'current_user' keyword argument
    if 'current_user' in kwargs and isinstance(kwargs['current_user'], User):
        return kwargs['current_user']

    # Search in positional and keyword arguments
    for arg in list(args) + list(kwargs.values()):
        if isinstance(arg, User):
            return arg
    return None


def _format_details(func, result, *args, **kwargs):
    """
    Creates a human-readable string from key function arguments for the log's 'details' field.
    """
    details = {}
    try:
        # Bind arguments to their names to easily access them
        bound_args = inspect.signature(func).bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
        arguments = bound_args.arguments
    except TypeError:
        # Fallback for cases where binding fails
        arguments = kwargs

    # Define keys that are universally useful for context
    id_keys = [
        'user_id', 'traveller_id', 'scooter_id', 'profile_id', 'system_admin_id',
        'username', 'first_name', 'last_name', 'email_address',
        'backup_file', 'traveller_query', 'query'
    ]

    # Extract relevant details from the arguments
    for key, value in arguments.items():
        if key in id_keys and value:
            # For 'data' dictionaries, extract specific fields
            if isinstance(value, dict):
                name = f"{value.get('first_name', '')} {value.get('last_name', '')}".strip()
                if name:
                    details['name'] = name
                if value.get('email_address'):
                    details['email'] = value.get('email_address')
            else:
                details[key] = value

    # If the function result is a new ID, include it
    if "ADD" in func.__name__.upper() and result and not isinstance(result, bool):
        details['new_id'] = result

    # Format the dictionary into a clean string
    return ", ".join([f"{key}: {value}" for key, value in details.items()])


def audit_activity(event_type, success_desc, failure_desc, suspicious_on_fail=False):
    """
    A decorator that logs the execution of a function, creating a readable and structured log entry.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # --- 1. Execute the actual function ---
            result = func(*args, **kwargs)

            # --- 2. Determine Success and User ---
            is_success = result[0] if isinstance(result, tuple) else bool(result)

            username = "(unknown)"
            user_obj = _get_user_from_args(*args, **kwargs)
            if user_obj:
                username = user_obj.username
            elif 'username' in kwargs:
                username = kwargs['username']

            # --- 3. Format Log Message ---
            try:
                # Use a dictionary of all args to format the description string
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                format_context = bound_args.arguments
                format_context['result'] = result
            except (TypeError, ValueError):
                format_context = kwargs
                format_context['result'] = result

            log_description = success_desc.format(**format_context) if is_success else failure_desc.format(
                **format_context)
            additional_info = _format_details(func, result, *args, **kwargs)

            # --- 4. Write to Log ---
            is_suspicious_flag = 1 if (not is_success and suspicious_on_fail) else 0

            data_access_instance.add_log_entry(
                username=username,
                event_type=f"{event_type}_{'SUCCESS' if is_success else 'FAIL'}",
                description=log_description,
                additional_info=additional_info,
                is_suspicious=is_suspicious_flag
            )

            return result

        return wrapper

    return decorator