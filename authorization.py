# --- Role-Based Access Control (RBAC) Definitions ---

PERMISSIONS = {
    'serviceengineer': {
        'update_scooter_limited',
        'search_scooters',
        'view_scooter_details',
        'update_own_profile',
        'change_own_password',
    },
    'systemadmin': {
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
    'superadmin': {
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

    # SuperAdmin inherits all permissions from systemadmin.
    role_permissions = PERMISSIONS.get(user_role, set())
    if user_role == 'superadmin':
        role_permissions.update(PERMISSIONS.get('systemadmin', set()))
        role_permissions.update(PERMISSIONS.get('serviceengineer', set()))
        #
        return True

    # Check the user's direct role permissions.
    if required_permission in role_permissions:
        return True

    # --- Handle role inheritance ---
    # A systemadmin can do everything a serviceengineer can.
    if user_role == 'systemadmin':
        service_engineer_permissions = PERMISSIONS.get('serviceengineer', set())
        if required_permission in service_engineer_permissions:
            return True

    return False
