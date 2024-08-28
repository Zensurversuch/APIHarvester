from interfaces import UserRole

def getPermissionsForRole(role):
    # Check if the role is an instance of UserRole
    if not isinstance(role, UserRole):
        print(f"Invalid role: {role}. Please use a valid UserRole instance.")
        return []
    for line in permissions_data.split('\n'):
        parts = line.strip().split(':')
        if parts[0] == str(role):
            return parts[1].split(',')
    return []


permissions_data = """
ADMIN:hello
USER:hello
PREMIUM_USER:
"""