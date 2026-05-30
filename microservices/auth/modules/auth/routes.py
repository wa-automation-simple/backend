from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    GoogleLoginRequest,
)

from fastapi.responses import JSONResponse


from modules.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=AuthResponse)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):

    try:
        service = AuthService(db)

        result = await service.register(payload)

        return JSONResponse(status_code=201, content=result.model_dump(mode="json"))

    except ValueError as e:
        return JSONResponse(
            status_code=400, content={"success": False, "message": str(e)}
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error"},
        )


@router.post("/login", response_model=AuthResponse)
# async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body = await request.json()

    elif "multipart/form-data" in content_type:
        form = await request.form()
        body = dict(form)

    elif "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        body = dict(form)

    else:
        return JSONResponse(
            status_code=415,
            content={"success": False, "message": "Unsupported Content-Type"},
        )

    try:
        payload = LoginRequest.model_validate(body)

        service = AuthService(db)

        result = await service.login(
            payload.email,
            payload.password,
        )

        return JSONResponse(status_code=200, content=result.model_dump(mode="json"))

    except ValueError as e:
        return JSONResponse(
            status_code=401, content={"success": False, "message": str(e)}
        )


@router.post("/google/login", response_model=AuthResponse)
# async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
async def login_google(payload: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    # content_type = request.headers.get("content-type", "")

    # if "application/json" in content_type:
    #     body = await request.json()

    # elif "multipart/form-data" in content_type:
    #     form = await request.form()
    #     body = dict(form)

    # elif "application/x-www-form-urlencoded" in content_type:
    #     form = await request.form()
    #     body = dict(form)

    # else:
    #     return JSONResponse(
    #         status_code=415,
    #         content={"success": False, "message": "Unsupported Content-Type"},
    #     )

    try:
        # payload = LoginRequest.model_validate(body)

        service = AuthService(db)

        result = await service.login_google(payload.credential)

        return JSONResponse(status_code=200, content=result.model_dump(mode="json"))

    except ValueError as e:
        return JSONResponse(
            status_code=401, content={"success": False, "message": str(e)}
        )
