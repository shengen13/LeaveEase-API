import firebase_admin
from firebase_admin import credentials, auth

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
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