import os
import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = os.getenv('ALGORITHMS')
API_AUDIENCE = os.getenv('API_AUDIENCE')


class AuthError(Exception):
    """A standardized way to communicate auth failure modes."""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    Get the header from the request and raise an AuthError if no header is present.
    Split the bearer and token and raise an AuthError if the header is malformed.
    Return the token part of the header.
    """
    
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    header_parts = auth_header.split(' ')
    if header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    elif len(header_parts) != 2:
        raise AuthError({
            'code': 'invalid header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = header_parts[1]
    return token


def check_permissions(permission, payload):
    """
    Parameters:
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
    
    Raise an AuthError if permissions are not included in the payload.
    Raise an AuthError if the requested permission string is not in the payload permissions array;
    return true otherwise.
    """

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_payload',
            'description': 'Payload must include permissions.'
        }, 401)
    elif permission not in payload['permissions']:
        raise AuthError({
            'code': 'invalid_payload',
            'description': 'Requested permission not in payload.'
        }, 401)
    return True
    

def verify_decode_jwt(token):
    """
    Parameters:
        token: a json web token (string)
    
    Raise an AuthError if key id (kid) is not in the token.
    Verify the token using Auth0 /.well-known/jwks.json.
    Decode the payload from the token.
    Validate the claims.
    Return the decoded payload. 
    """
    
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)

    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 401)


def requires_auth(permission=''):
    """
    Parameters:
        permission: string permission (i.e. 'post:drink')
    
    Use the get_token_auth_header method to get the token.
    Use the verify_decode_jwt method to decode the jwt.
    Use the check_permissions method to validate claims and check the requested permission.
    Return the decorator which passes the decoded payload to the decorated method.
    """

    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator