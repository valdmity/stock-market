from cryptography.fernet import Fernet
from config import settings


fernet = Fernet(settings.ENCRYPTION_KEY)