from environs import Env
from loguru import logger

env = Env()
logger.info("Loading environment variables...")


DATABASE_URL = env.str("DOCUMENT_SERVICE_DATABASE_URL")
SERVICE_NAME = "document-service"
PORT = 30005


ENVIRONMENT = env.str("ENVIRONMENT", "production")
RELOAD = True if ENVIRONMENT == "development" else False


SUPABASE_PROJECT_ID = env.str("SUPABASE_PROJECT_ID")
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
ISSUER = f"{SUPABASE_URL}/auth/v1"
AUDIENCE = "authenticated"


DESCRIPTION = f"""
# Chào mừng đến với {SERVICE_NAME}

Bạn có thể đăng nhập qua Google bằng đường dẫn dưới đây:
* [Đăng nhập với Google](https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/authorize?provider=google)

Xem redoc:
* [Xem redoc](/redoc)

Xem docs:
* [Xem docs](/docs)

Xem voyager:
* [Xem voyager](/voyager)

### Thông tin hệ thống:
* **SERVICE_NAME:** {SERVICE_NAME}
* **ENVIRONMENT:** {ENVIRONMENT}
* **RELOAD:** {RELOAD}
""".strip()


if ENVIRONMENT == "development":
    import subprocess

    subprocess.run(["start", f"http://localhost:{PORT}/docs"], shell=True)
    subprocess.run(
        [
            "start",
            f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/authorize?provider=google",
        ],
        shell=True,
    )


NVIDIA_API_KEY = env.str("NVIDIA_API_KEY")


CLOUDFLARE_ACCOUNT_ID = env.str("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = env.str("CLOUDFLARE_API_TOKEN")


CHOOSE_LLM_TOKEN_COUNT_THRESHOLD = 4000


MAX_FILE_SIZE = env.int("MAX_FILE_SIZE", 50 * 1024 * 1024)
ALLOWED_FILE_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt", ".md", ".pptx"]


MAX_SUMMARY_TEXT_LENGTH = 15000
PRESIGNED_URL_EXPIRATION = 3600


R2_ACCESS_KEY_ID = env.str("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = env.str("R2_SECRET_ACCESS_KEY")
R2_ACCOUNT_ID = CLOUDFLARE_ACCOUNT_ID
R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"


R2_BUCKET_NAME = "dev-documents" if ENVIRONMENT == "development" else "prod-documents"


R2_PUBLIC_DOMAIN = f"https://pub-{R2_ACCOUNT_ID}.r2.dev"


QDRANT_URL = env.str("QDRANT_URL")
QDRANT_API_KEY = env.str("QDRANT_API_KEY")
