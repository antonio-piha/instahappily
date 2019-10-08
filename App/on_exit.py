import atexit
from .service.session_service import executor

atexit.register(executor.cleanup)