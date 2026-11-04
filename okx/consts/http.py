"""HTTP header names, HTTP verbs, base URL and the credential sentinel."""

# Http header
API_URL = 'https://www.okx.com'

CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'

ACEEPT = 'Accept'
COOKIE = 'Cookie'
LOCALE = 'Locale='

APPLICATION_JSON = 'application/json'

GET = "GET"
POST = "POST"

# Unset sentinel for credential args — lets public endpoints work without keys.
# Never signed or transmitted as a real key/secret/passphrase.
_NO_CREDENTIAL = '-1'

SERVER_TIMESTAMP_URL = '/api/v5/public/time'
