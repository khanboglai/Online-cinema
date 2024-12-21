from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/heartbeat", response_class=JSONResponse)
async def heartbeat(request: Request):
    return JSONResponse({
        "status": True,
        "message": "I'm alive!"
    })