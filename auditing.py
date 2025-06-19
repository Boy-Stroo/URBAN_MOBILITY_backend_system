from functools import wraps
import data_access as da
from models import User
import json
import inspect

da = da.DataAccess()

def _find_user_in_args(*args, **kwargs):
    """A helper to find the User object in the decorated function's arguments."""
    for arg in args:
        if isinstance(arg, User):
            return arg
    for key, value in kwargs.items():
        if isinstance(value, User):
            return value
    if 'current_user' in kwargs and isinstance(kwargs['current_user'], User):
        return kwargs['current_user']
    return None


def _extract_log_details(func, result, *args, **kwargs):
    """
    Intelligently extracts relevant details for logging based on the function's
    signature and arguments, avoiding sensitive data.
    """
    details = {}

    # Bind the arguments to the function signature to get their names
    try:
        bound_args = inspect.signature(func).bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
    except TypeError:
        # Fallback if binding fails
        bound_args = {'arguments': kwargs}

    # Whitelist of safe, common identifiers to log
    id_keys = ['user_id', 'traveller_id', 'scooter_id', 'profile_id', 'system_admin_id', 'backup_file']
    for key, value in bound_args.arguments.items():
        if key in id_keys:
            details['target_id' if 'id' in key else key] = value

    # For creation events, the result is the new ID.
    if "ADD" in func.__name__.upper() and isinstance(result, int):
        details['new_record_id'] = result

    return json.dumps(details) if details else ""


def audit_activity(event_type, success_desc, failure_desc, suspicious_on_fail=False):
    """
    A decorator to log the outcome of a service function. It automatically finds
    the user object or username in the function arguments to identify the actor.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the actual function first to get its result
            result = func(*args, **kwargs)

            is_success = result[0] if isinstance(result, tuple) else bool(result)

            username = "(unknown)"
            user_obj = _find_user_in_args(*args, **kwargs)
            if user_obj:
                username = user_obj.username
            elif 'username' in kwargs:
                username = kwargs['username']

            # --- Robustly build context for log message formatting ---
            try:
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                all_func_args = bound_args.arguments
            except (TypeError, ValueError):
                all_func_args = kwargs

            format_context = {
                "result": result,
                "username": username,
                **all_func_args
            }

            log_description = success_desc.format(**format_context) if is_success else failure_desc.format(
                **format_context)
            additional_info = _extract_log_details(func, result, *args, **kwargs)

            if is_success:
                da.add_log_entry(
                    username=username,
                    event_type=f"{event_type}_SUCCESS",
                    description=log_description,
                    additional_info=additional_info
                )
            else:
                is_suspicious_flag = 1 if suspicious_on_fail else 0
                da.add_log_entry(
                    username=username,
                    event_type=f"{event_type}_FAIL",
                    description=log_description,
                    additional_info=additional_info,
                    is_suspicious=is_suspicious_flag
                )

            return result

        return wrapper

    return decorator
