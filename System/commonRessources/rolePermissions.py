from commonRessources.interfaces import UserRole, Permissions

def getPermissionsForRole(role):
    permissions = []
    if role == UserRole.ADMIN.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,
            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value
        ]
    elif role == UserRole.USER.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,
            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value
        ]
    elif role == UserRole.PREMIUM_USER.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,
            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value
]
    return permissions
