import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import init
from auth import authenticate
from core.logging import logger, uvicorn_log_config
from domains import (
    account_activation,
    apc_competence,
    apc_data,
    apc_kpi_competence,
    lnm_calendar,
    lnm_enseignant,
    lnm_etudiant,
    lnm_evaluation,
    lnm_filiere,
    lnm_mobility_assignment,
    lnm_rendu_module,
    lnm_university,
    maquette_module,
    maquette_module_creation,
)
from system import access_auth, check

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
app.include_router(maquette_module_creation.router)
app.include_router(lnm_rendu_module.router)
app.include_router(lnm_evaluation.router)
app.include_router(apc_data.router)
app.include_router(apc_kpi_competence.router)
app.include_router(apc_competence.router)
app.include_router(lnm_calendar.router)
app.include_router(lnm_mobility_assignment.router)
app.include_router(account_activation.router)


# Classical health
@app.get("/health", response_model=None)
def health() -> object:
    return {"status": "ok"}


@app.get("/", response_model=None)
async def root() -> object:
    return {"message": "Hello, I'm Learnagement BackEnd!"}


if __name__ == "__main__":
    logger.info("backend.init_database")
    init.init()
    logger.info("backend.start")

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

    uvicorn.run(app, log_config=uvicorn_log_config(), **uvicorn_kwargs)
