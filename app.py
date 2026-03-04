from routes.api.cep import router as cep_router
from routes.web.user import router as user_router
from routes.web.admin import router as admin_router
from bootstrap import app


app.include_router(cep_router)
app.include_router(user_router)
app.include_router(admin_router)