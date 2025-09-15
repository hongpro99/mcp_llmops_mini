#환경변수 로딩

#따로 파일에 로딩하고 import 하는 구조가 좋음

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL : str
    DB_USER : str
    DB_PASSWORD : str
    DB_HOST : str
    DB_PORT : str
    DB_NAME : str
    
    OPENAI_API_KEY : str
    CHAT_MODEL : str
    EMBED_MODEL : str
    LANGSMITH_TRACING : bool
    LANGSMITH_API_KEY : str

    
    CHUNK_SIZE : int
    CHUNK_OVERLAP : int
    
    FAISS_INDEX_PATH : str
    model_config = SettingsConfigDict(env_file='.env', extra= 'ignore')
    
settings = Settings()

print(">>> [settings] 로딩 완료")