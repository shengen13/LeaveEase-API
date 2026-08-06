from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from datetime import datetime
import os
import shutil

from firebase_config import verify_token
from utils import read_json, write_json

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/apply")
def apply_leave(
    leave_type: str = Form(...),
    priority: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    reason: str = Form(...),
    document: UploadFile | None = File(None),
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

    employee = next(
        (user for user in users if user["uid"] == decoded["uid"]),
        None
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee Not Found"
        )

    leave_requests = read_json("leave_requests.json")

    document_path = ""

    if document:

        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png"
        ]

        extension = os.path.splitext(document.filename)[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, JPG, JPEG and PNG files are allowed."
            )

        filename = f'{decoded["uid"]}_{int(datetime.now().timestamp())}{extension}'

        save_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(
                document.file,
                buffer
            )

        document_path = f"uploads/{filename}"

    new_leave = {
        "id": max(
            [leave["id"] for leave in leave_requests],
            default=0
        ) + 1,
        "uid": decoded["uid"],
        "employee_name": employee["email"],
        "leave_type": leave_type,
        "priority": priority,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "document": document_path,
        "status": "Pending",
        "admin_comment": "",
        "applied_on": datetime.now().strftime("%Y-%m-%d")
    }

    leave_requests.append(new_leave)

    write_json(
        "leave_requests.json",
        leave_requests
    )

    return {
        "message": "Leave Applied Successfully",
        "leave": new_leave
    }


@router.get("/history")
def get_leave_history(
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

    leave_requests = read_json("leave_requests.json")

    return [
        leave
        for leave in leave_requests
        if leave["uid"] == uid
    ]


@router.get("/all")
def get_all_leave_requests(
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

    leave_requests = read_json("leave_requests.json")

    return leave_requests


@router.put("/update/{leave_id}")
def update_leave_status(
    leave_id: int,
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

    leave_requests = read_json("leave_requests.json")

    leave = next(
        (
            item
            for item in leave_requests
            if item["id"] == leave_id
        ),
        None
    )

    if leave is None:
        raise HTTPException(
            status_code=404,
            detail="Leave Request Not Found"
        )

    leave["status"] = data["status"]
    leave["admin_comment"] = data.get(
        "admin_comment",
        ""
    )

    write_json(
        "leave_requests.json",
        leave_requests
    )

    return {
        "message": "Leave Updated Successfully",
        "leave": leave
    }