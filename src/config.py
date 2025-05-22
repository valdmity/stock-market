from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    HASH_KEY: str
    ENCRYPTION_KEY: str

    @property
    def DATABASE_URL_asyncpg(self):
        return "postgresql+asyncpg://" + self.DATABASE_URL
    
    @property
    def DATABASE_URL_default(self):
        return "postgresql://" + "userone:qwertyuseronepostgrestochka@c-c9qpfjjk5123cemgdb8q.rw.mdb.yandexcloud.net:6432/market"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()