from functools import wraps
from flask_jwt_extended import get_jwt_identity
from rolePermissions import getPermissionsForRole
from flask import jsonify
from interfaces import ApiStatusMessages
from constants import API_MESSAGE_DESCRIPTOR

def permission_check(userRepo):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            currentUserID = get_jwt_identity()
            user = userRepo.getUserByID(currentUserID)

            if(user):
                currentRole = user.role
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}User does not exist"}), 401

            currentPermissions = set(getPermissionsForRole(currentRole))

            if function_name in currentPermissions:
                return func(*args, **kwargs)
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR:f"{ApiStatusMessages.ERROR}Access not permitted! {function_name} permission required"}), 403

        return wrapper
    return decorator
