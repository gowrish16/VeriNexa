import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# VeriNexa Core Model & Inference Configuration
# Fast 1.3 GB weights for high-throughput CPU inference
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "60m")
NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "8"))
NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "33"))
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
