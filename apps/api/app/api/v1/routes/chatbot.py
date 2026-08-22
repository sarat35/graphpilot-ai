from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def chatbot_status() -> dict[str, str]:
    return {"status": "mock", "message": "Tell me your budget, city, and preferred car type."}
