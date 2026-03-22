import hmac
import base64
import hashlib

"""
A helper function to create the secret hash based on the 
client ID & client secret hash & the username (in our case it is email)

COGNITO requires a combined type of hashing :- HMAC + SHA256 

so why are we doing this combined HMAC thing instead of doing just the SHA256. 

so how does SHA256 work ? 
-> so we give the function () the client_id and the message 
   and it returns the hash. Lets say 256skhflkashdflkajhsd 

   so the attacker only needs to apppend this value with something like &role=admin 
   and our surver will accept it because it has the 256skhflkashdflkajhsd in it.


so to prevent this we HMAC and how does it prevent it is :- it uses two sha256 hashing 

so HMAC = INNER HASH + OUTER HASH

INNER HASH = SHA256((client_secret EXOR ipad) + message)

OUTER HASH = SHA256((client_secret EXOR opad) + INNER_HASH)

so the attacker cant calculate or reverse engineer the inner hash wich contains the message which is nothign but :- username + client_id

"""


def get_secret_hash(client_id: str, username: str, secret_hash: str):
    # first we will create a message that will comprise of client_id and username
    message = username + client_id

    # HEre we are creating the hmac hash 
    digest = hmac.new(
        key=secret_hash.encode("utf-8"), msg=message.encode("utf-8"), digestmod=hashlib.sha256
    ).digest() # .new() creates the new hashing object and .digest() returns the hashing object


    # so we are not returning the digest directly because it is in binary and the cognito requires base64 encoding
    return base64.b64encode(digest).decode("utf-8") # base64 encoding the digest
