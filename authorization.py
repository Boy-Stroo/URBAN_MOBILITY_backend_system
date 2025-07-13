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
        'restore_backup',
        'search_system_admins',
    },
    'superadmin': {
        'add_system_admin',
        'generate_restore_code',
    }
}

def has_permission(user_role, required_permission):
    if not user_role:
        return False

    role_permissions = PERMISSIONS.get(user_role, set())
    if user_role == 'superadmin':
        role_permissions.update(PERMISSIONS.get('systemadmin', set()))
        role_permissions.update(PERMISSIONS.get('serviceengineer', set()))
        return True

    if required_permission in role_permissions:
        return True

    if user_role == 'systemadmin':
        service_engineer_permissions = PERMISSIONS.get('serviceengineer', set())
        if required_permission in service_engineer_permissions:
            return True

    return False
