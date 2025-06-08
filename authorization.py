# --- Role-Based Access Control (RBAC) Definitions ---

PERMISSIONS = {
    'ServiceEngineer': {
        'update_scooter_limited',
        'search_scooters',
        'view_scooter_details',
        'update_own_profile',
        'change_own_password',
    },
    'SystemAdmin': {
        'add_traveller',
        'update_traveller',
        'delete_traveller',
        'search_travellers',
        'view_traveller_details',
        'add_scooter',
        'update_scooter_full',
        'delete_scooter',
        'add_service_engineer',
        'update_service_engineer_profile',
        'delete_service_engineer',
        'reset_service_engineer_password',
        'search_service_engineers',
        'view_system_logs',
        'create_backup',
        'restore_backup',  # SysAdmin can only restore with a code
    },
    'SuperAdmin': {
        'add_system_admin',
        'generate_restore_code',
        # SuperAdmin inherits all other permissions implicitly
    }
}


# --- Main Authorization Function ---

def has_permission(user_role, required_permission):
    """
    Checks if a user role has the required permission.
    This function handles role inheritance.
    """
    if not user_role:
        return False

    # SuperAdmin inherits all permissions from SystemAdmin.
    if user_role == 'SuperAdmin':
        return True

    # Check the user's direct role permissions.
    role_permissions = PERMISSIONS.get(user_role, set())
    if required_permission in role_permissions:
        return True

    # --- Handle role inheritance ---
    # A SystemAdmin can do everything a ServiceEngineer can.
    if user_role == 'SystemAdmin':
        service_engineer_permissions = PERMISSIONS.get('ServiceEngineer', set())
        if required_permission in service_engineer_permissions:
            return True

    return False
