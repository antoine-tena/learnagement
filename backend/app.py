import logging
import os
from collections.abc import Awaitable, Callable
from typing import override

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import init
from auth import authenticate
from core.config import TermColors
from domains import (
    apc_competence,
    apc_data,
    apc_kpi_competence,
    lnm_calendar,
    lnm_enseignant,
    lnm_etudiant,
    lnm_evaluation,
    lnm_filiere,
    lnm_mobility_assignment,
    lnm_university,
    maquette_module,
)
from system import access_auth, check

access_logger = logging.getLogger("uvicorn.access")


class HealthFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()


access_logger.addFilter(HealthFilter())

formatter = logging.Formatter(fmt="%(levelname)s:     %(filename)s:%(lineno)d - %(message)s")

for handler in access_logger.handlers:
    handler.setFormatter(formatter)

# app = FastAPI(dependencies=[Depends(get_query_token)])
origins = ["*"]
app = FastAPI()

# Ajouter le middleware à l'application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autorise ton port 40080
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Autorise Authorization, Content-Type, etc.
)

app.include_router(authenticate.router)
app.include_router(check.router)
app.include_router(access_auth.router)
app.include_router(lnm_enseignant.router)
app.include_router(lnm_etudiant.router)
app.include_router(lnm_university.router)
app.include_router(lnm_filiere.router)
app.include_router(maquette_module.router)
app.include_router(lnm_evaluation.router)
app.include_router(apc_data.router)
app.include_router(apc_kpi_competence.router)
app.include_router(apc_competence.router)
app.include_router(lnm_calendar.router)
app.include_router(lnm_mobility_assignment.router)


# Classical health
@app.get("/health", response_model=None)
def health() -> object:
    return {"status": "ok"}


# make health silent (without log)
@app.middleware("http")
async def silence_health_logs(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    if request.url.path == "/health":
        previous_state = access_logger.disabled
        access_logger.disabled = True
        try:
            response = await call_next(request)
        finally:
            access_logger.disabled = previous_state
        return response
    return await call_next(request)


@app.get("/", response_model=None)
async def root() -> object:
    return {"message": "Hello, I'm Learnagement BackEnd!"}


if __name__ == "__main__":
    print(TermColors.OKGREEN + "Init BD framework..." + TermColors.ENDC)
    init.init()
    print(TermColors.OKGREEN + "Start backend Python..." + TermColors.ENDC)

    is_prod = os.getenv("ENV", "dev") == "prod"
    ssl_dir = os.getenv("DOCKER_SSL_INTERNAL_DIR")

    uvicorn_kwargs = {
        "host": "0.0.0.0",
        "port": 4000,
    }

    if is_prod:
        uvicorn_kwargs.update(
            {
                "ssl_certfile": os.path.join(ssl_dir, "cert.pem"),
                "ssl_keyfile": os.path.join(ssl_dir, "key.pem"),
            }
        )

    uvicorn.run(app, **uvicorn_kwargs)
