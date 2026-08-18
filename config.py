import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # =====================================================
    # ENVIRONMENT
    # =====================================================

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )


    # =====================================================
    # APPLICATION
    # =====================================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPABASE_URL = os.getenv("SUPABASE_URL")

    SUPABASE_SECRET_KEY = os.getenv(
        "SUPABASE_SECRET_KEY"
    )

    SUPABASE_BUCKET = "vellichor-pdfs"


    # =====================================================
    # AI
    # =====================================================

    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY"
    )

    GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

    EMBEDDING_MODEL = (
        "BAAI/bge-small-en-v1.5"
    )


    # =====================================================
    # LOCAL STORAGE
    # =====================================================

    CHROMA_DB_PATH = "chroma_db"

    UPLOAD_FOLDER = "uploads"


    # =====================================================
    # FILE UPLOAD
    # =====================================================

    MAX_CONTENT_LENGTH = (
        16 * 1024 * 1024
    )

    ALLOWED_EXTENSIONS = {"pdf"}