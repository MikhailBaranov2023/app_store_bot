import string
import secrets
from asgiref.sync import sync_to_async


@sync_to_async()
def gen_token():
    alphabet = string.ascii_letters + string.digits
    while True:
        token = ''.join(secrets.choice(alphabet) for i in range(20))
        if (any(c.islower() for c in token)
                and any(c.isupper() for c in token)
                and sum(c.isdigit() for c in token) >= 3):
            break
    return token
