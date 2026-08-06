from fastapi import APIRouter, Header, HTTPException

from firebase_config import verify_token
from utils import read_json, write_json

router = APIRouter()


@router.post("/register")
def register(
    data: dict,
    Authorization: str = Header(...)
):
    if not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    token = Authorization.replace("Bearer ", "")

    try:
        decoded = verify_token(token)
    except Exception as e:
        print("Firebase Error:", e)
        raise HTTPException(
            status_code=401,
            detail="Token Verification Failed"
    )

    uid = decoded["uid"]
    email = decoded.get("email", "")

    users = read_json("users.json")

    for user in users:
        if user["uid"] == uid:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

    new_user = {
        "uid": uid,
        "employeeId": "",
        "name": data["name"],
        "email": email,
        "department": data["department"],
        "designation": data["designation"],
        "role": "employee",
        "annual_leave": 24,
        "sick_leave": 10,
        "casual_leave": 6,
        "emergency_leave": 5,
        "status": "Active"
    }

    users.append(new_user)

    write_json("users.json", users)

    return {
        "message": "Registration Successful",
        "user": new_user
    }


@router.post("/login")
def login(
    Authorization: str = Header(...)
):

    if not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    token = Authorization.replace("Bearer ", "")

    try:
        decoded = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token Verification Failed"
        )

    uid = decoded["uid"]

    users = read_json("users.json")

    for user in users:
        if user["uid"] == uid:
            return user

    raise HTTPException(
        status_code=404,
        detail="User not found. Please register first."
    )

@router.get("/users")
def get_users(Authorization: str = Header(...)):

    if not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    token = Authorization.replace("Bearer ", "")

    try:
        decoded = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token Verification Failed"
        )

    users = read_json("users.json")

    admin = next(
        (user for user in users if user["uid"] == decoded["uid"]),
        None
    )

    if not admin or admin["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return users

@router.put("/update/{uid}")
def update_user(
    uid: str,
    data: dict,
    Authorization: str = Header(...)
):

    if not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    token = Authorization.replace("Bearer ", "")

    try:
        decoded = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token Verification Failed"
        )

    users = read_json("users.json")

    admin = next(
        (user for user in users if user["uid"] == decoded["uid"]),
        None
    )

    if not admin or admin["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    updated = False

    for user in users:

        if user["uid"] == uid:

            user["name"] = data["name"]
            user["department"] = data["department"]
            user["designation"] = data["designation"]
            user["role"] = data["role"]

            updated = True
            break

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Employee Not Found"
        )

    write_json("users.json", users)

    return {
        "message": "Employee Updated Successfully"
    }

@router.delete("/delete/{uid}")
def delete_user(
    uid: str,
    Authorization: str = Header(...)
):

    if not Authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    token = Authorization.replace("Bearer ", "")

    try:
        decoded = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token Verification Failed"
        )

    users = read_json("users.json")

    admin = next(
        (user for user in users if user["uid"] == decoded["uid"]),
        None
    )

    if not admin or admin["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    if uid == decoded["uid"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )

    user_found = False
    new_users = []

    for user in users:

        if user["uid"] == uid:
            user_found = True
            continue

        new_users.append(user)

    if not user_found:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    write_json("users.json", new_users)

    return {
        "message": "Employee deleted successfully."
    }