from app.security.jwt import create_access_token, decode_access_token
from jose import jwt
from app.security.jwt import SECRET_KEY, ALGORITHM


def test_create_access_token():

    data = {
        "sub": "43b6285b-6e7e-4b66-aaa8-d1c5cbcacc8b"
    }

    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    assert payload["sub"] == data["sub"]
    assert "exp" in payload

def test_decode_valid_token():

    data = {
        "sub": "43b6285b-6e7e-4b66-aaa8-d1c5cbcacc8b"
    }

    token = create_access_token(data)

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == data["sub"]


def test_decode_invalid_token():

    token = "invalid.jwt.token"

    payload = decode_access_token(token)

    assert payload is None