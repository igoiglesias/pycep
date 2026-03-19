from fastapi.responses import FileResponse

from routes.api.cep import router as cep_router
from routes.web.user import router as user_router
from routes.web.admin import router as admin_router
from bootstrap import app


app.include_router(cep_router)
app.include_router(user_router)
app.include_router(admin_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")