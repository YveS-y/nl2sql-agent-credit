import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL_PATH = os.getenv("MODEL_PATH", "/Users/ys/e/models/bge-large-zh-v1.5")
PORT = int(os.getenv("PORT", "8081"))

model: SentenceTransformer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    print(f"Loading model from {MODEL_PATH} ...")
    model = SentenceTransformer(MODEL_PATH)
    print("Model ready.")
    yield


app = FastAPI(lifespan=lifespan)


class EmbedRequest(BaseModel):
    inputs: str | list[str]


@app.get("/health")
def health():
    return {}


@app.post("/embed")
def embed(req: EmbedRequest):
    texts = req.inputs if isinstance(req.inputs, list) else [req.inputs]
    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    return vectors


@app.post("/")
def feature_extraction(req: EmbedRequest):
    texts = req.inputs if isinstance(req.inputs, list) else [req.inputs]
    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    return vectors
