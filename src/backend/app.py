from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.db.db import init_db
from src.backend.routes import router as routes_router
from pathlib import Path


def get_app(data_csv_path: Path) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        data_csv_path: Path to the dataset CSV file
        database_path: Path to the database file
    Returns:
        Configured FastAPI application
    """
    # TODO: I don't think we need the context manager given a Neon DB in the cloud now
    # @asynccontextmanager
    # async def lifespan(app: FastAPI):
    #     # Initialize database on startup
    #     init_db(data_csv_path)
    #     yield

    # app = FastAPI(lifespan=lifespan)
    app = FastAPI()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite default port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup Routes /src/backend/routes
    app.include_router(routes_router)
    return app
