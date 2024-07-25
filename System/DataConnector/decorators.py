from functools import wraps
from flask_jwt_extended import get_jwt_identity
from role_permissions import getPermissionsForRole
from flask import jsonify
from interfaces import ApiStatusMessages

def permission_check(user_repo):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            currentUserID = get_jwt_identity()
            user = user_repo.get_user_by_id(currentUserID)

            if(user):
                currentRole = user.role
            else:
                return jsonify({"AuthenticationError": "Benutzer existiert nicht"}), 401

            currentPermissions = set(getPermissionsForRole(currentRole))

            if function_name in currentPermissions:
                return func(*args, **kwargs)
            else:
                return jsonify({"AuthenticationError":f"Access not permitted! {function_name} permission required"}), 403

        return wrapper
    return decorator
