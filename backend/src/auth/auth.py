import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen



AUTH0_DOMAIN = 'loynv2vi.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'dev'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
✅TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({
            "code": "Auth_head_missing",
            "description": "Auth header is expected",
        }, 401)
    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({
            "code": "invalid header",
            "description": 'Authorization header must start with "Bearer"',
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            "code": "Invalid header",
            "description": "Token not found",
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            "code": "Invalid header",
            "description":"Auth header must be Bear Token",
        }, 401)

    token = parts[1]
    return token


'''
✅TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    # if permissions are not included in the payload
    if 'permission' not in payload:
        raise AuthError({
            "code": "invalid_payload",
            "description":"Permission not included in payload",
        }, 401)
    # if the requested permission string is not in the payload permissions array
    if permission not in payload['permissions']:
        raise AuthError({
            'code': "Unauthorized",
            'description':"Permission denied",
        },401)

    return True



'''
✅TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    ✅it should be an Auth0 token with key id (kid)
    ✅it should verify the token using Auth0 /.well-known/jwks.json
    ✅it should decode the payload from the token
    ✅it should validate the claims
    ✅return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    #Get the public key
    jsonURL = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonURL.read())

    #Get header data
    unverifiedHeader = jwt.get_unverified_header(token)

    rsaKey = {}
    #check if key 'kid' in the header:
    if 'kid' not in unverifiedHeader:
        raise AuthError({
            'code':'invalid header',
            'description': 'Authorization unverified',
        },401)

    for key in jwks['keys']:
        if key['kid'] == unverifiedHeader['kid']:
            #load rsaKEy with .well-known jwks keys
            rsaKey = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    #Validation:
    if rsaKey:
        try:
            payload = jwt.decode(
                token,
                rsaKey,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        #validate token expiry
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description':'Token has expired its time',
            }, 401)
            #validate token claims
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'claims_invalid',
                'description':'Incorrect claims',
            })
            #validate token header
        except Exception:
            raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

            


'''
✅TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
