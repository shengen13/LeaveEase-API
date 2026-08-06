import os

import firebase_admin
from firebase_admin import credentials, auth


if not firebase_admin._apps:

    if os.path.exists("firebase-key.json"):

        cred = credentials.Certificate("firebase-key.json")

    else:

        firebase_dict = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
        }

        cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)


def verify_token(id_token: str):
    try:
        return auth.verify_id_token(id_token)

    except Exception as e:
        print("\n================ FIREBASE ERROR ================")
        print(type(e).__name__)
        print(str(e))
        print("===============================================\n")
        raise