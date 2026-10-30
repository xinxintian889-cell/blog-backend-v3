from fastapi import Request,FastAPI
from fastapi.responses import JSONResponse
from app.domain.exceptions import ArticleNotFoundError, DuplicateTitleError,IsnullTitleError


async def handler_not_found(request: Request, exc: ArticleNotFoundError):
    return JSONResponse(status_code=404, content={"message": str(exc)})

async def handler_dup(request: Request, exc: DuplicateTitleError):
    return JSONResponse(status_code=400, content={"message": str(exc)})

async def handler_isnull(request: Request, exc: IsnullTitleError):
    return JSONResponse(status_code=400, content={"message": str(exc)})


#统一的注册函数
def register_exception_handlers(app:FastAPI):
    app.add_exception_handler(ArticleNotFoundError,handler_not_found)
    app.add_exception_handler(DuplicateTitleError,handler_dup)
    app.add_exception_handler(IsnullTitleError,handler_isnull)
