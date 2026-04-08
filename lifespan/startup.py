from fastapi import FastAPI
from loguru import logger

from app.documents.core.vectorstore import init_vector_store


async def startup(app: FastAPI):
    logger.info("Starting application processes...")

    await init_vector_store()
