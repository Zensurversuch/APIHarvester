from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from commonRessources.rolePermissions import getPermissionsForRole
from flask import jsonify, request
from os import getenv
from commonRessources.interfaces import ApiStatusMessages
from commonRessources import API_MESSAGE_DESCRIPTOR

import logging
logger = logging.getLogger(__name__)

def userRoles(role, functionName):
    """
    Check if a user with the given role has permission to access the specified function.
    Parameters:
    - role (str): The role of the user.
    - functionName (str): The name of the function to check permission for.
    Returns:
    - bool: True if the user has permission, False otherwise.
    """
    
    currentPermissions = set(getPermissionsForRole(role))
    if functionName in currentPermissions:
        return True
    else:
        return False

def accessControlJwt(func):
    """
    Decorator function that provides access control based on JWT authentication.
    This is used to restrict access to certain functions based on the role of the user.
    Raises:
        403: If access is not permitted.
    """
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        functionName = func.__name__
        jwt = get_jwt()
        userRole = jwt.get('role')

        if userRoles(userRole, functionName):
            return func(*args, **kwargs)
        else:
            return jsonify({API_MESSAGE_DESCRIPTOR:f"{ApiStatusMessages.ERROR}Access not permitted! {functionName} permission required"}), 403
    return wrapper

def accessControlJwtOrApiKey(func):
    """
    Decorator function that provides access control based on JWT or API key.
    It is used for API Routes which can be accessed by a user (grants access via JWT)
    and internal services (grants access via API key).
    Raises:
        403: If access is not permitted.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        validJwtAvailable = False
        try:
            @jwt_required()
            def testIfJwtIsPassed(*args, **kwargs):
                return True
            validJwtAvailable = testIfJwtIsPassed(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT validation error: {str(e)}")
            validJwtAvailable = False

        if validJwtAvailable:            # The access request is from a user with a JWT token
            jwt = get_jwt()
            userRole = jwt.get('role')
            functionName = func.__name__
            if userRoles(userRole, functionName):
                return func(*args, **kwargs)
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access not permitted! {functionName} permission required"}), 403
        else:                   # The access request is from an internal service with an API key
            apiKey = request.headers.get('x-api-key')
            if apiKey and apiKey == getenv('INTERNAL_API_KEY'):
                return func(*args, **kwargs)
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access denied, invalid token or API key"}), 403

    return wrapper


def accessControlApiKey(func):
    """
    Decorator function for access control based on API key.
    It is used for API Routes which can only be accessed by internal services.
    Raises:
        403: If access is not permitted.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != getenv('INTERNAL_API_KEY'):
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access denied invalid API KEY"}), 403
        return func(*args, **kwargs)
    return wrapper
