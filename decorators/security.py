from fastapi import Request, HTTPException, Depends
import hashlib
import hmac
from config import settings

def validate_signature(payload: str, signature: str) -> bool:
    expected_signature = hmac.new(
        key=bytes(settings.APP_SECRET, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)

async def signature_required(request: Request):
    signature = request.headers.get("X-Hub-Signature-256", "")[7:] 
    payload = await request.body()
    if not validate_signature(payload.decode("utf-8"), signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

