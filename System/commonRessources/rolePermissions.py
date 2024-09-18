from commonRessources.interfaces import UserRole, Permissions

def getPermissionsForRole(role):        # set the permissions for the different roles here
    permissions = []
    if role == UserRole.ADMIN.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,

            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value,

            Permissions.SUBSCRIBE_API.value,
            Permissions.RESUBSCRIBE_API.value,
            Permissions.UNSUBSCRIBE_API.value
        ]
    elif role == UserRole.USER.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,
            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value,

            Permissions.SUBSCRIBE_API.value,
            Permissions.RESUBSCRIBE_API.value,
            Permissions.UNSUBSCRIBE_API.value
        ]
    elif role == UserRole.PREMIUM_USER.value:
        permissions = [
            Permissions.INFLUX_GET_DATA.value,
            Permissions.AVAILABLE_APIS.value,
            Permissions.SUBSCRIPTIONS.value,
            Permissions.SUBSCRIPTIONS_BY_USER_ID.value,

            Permissions.SUBSCRIBE_API.value,
            Permissions.RESUBSCRIBE_API.value,
            Permissions.UNSUBSCRIBE_API.value
        ]
    return permissions
