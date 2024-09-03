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
    currentPermissions = set(getPermissionsForRole(role))
    logger.error(f"functionName: {functionName}")
    logger.error(f"currentPermissions: {currentPermissions}")
    if functionName in currentPermissions:
        return True
    else:
        return False

def accessControlJwt(func):
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
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Versuch, JWT aus der Anfrage zu holen
        jwtValid = False
        try:
            @jwt_required()
            def inner_func(*args, **kwargs):
                return True

            jwtValid = inner_func(*args, **kwargs)  # JWT-Überprüfung
        except Exception as e:
            logger.error(f"JWT Header: {request.headers}")
            logger.error(f"JWT validation error: {str(e)}")
            jwtValid = False  # Falls JWT nicht validiert werden konnte

        if jwtValid:
            jwt = get_jwt()
            userRole = jwt.get('role')
            functionName = func.__name__
            if userRoles(userRole, functionName):
                return func(*args, **kwargs)
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access not permitted! {functionName} permission required"}), 403
        else:
            # Versuch, den API-Schlüssel zu validieren
            apiKey = request.headers.get('x-api-key')
            if apiKey and apiKey == getenv('INTERNAL_API_KEY'):
                return func(*args, **kwargs)
            else:
                return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access denied, invalid token or API key"}), 403

    return wrapper


def accessControlApiKey(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != getenv('INTERNAL_API_KEY'):
            return jsonify({API_MESSAGE_DESCRIPTOR: f"{ApiStatusMessages.ERROR}Access denied invalid API KEY"}), 403
        return func(*args, **kwargs)
    return wrapper
