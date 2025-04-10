import json
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    sender_email: str
    smtp_server: str
    smtp_port: int
    login: str = '123'
    password: str
    signature:str

    model_config = SettingsConfigDict(extra="ignore")

    @classmethod
    def from_json(cls, path: str = None):
        path = path or os.getenv("EMAIL_CONFIG_PATH", "./src/config/params.json")
        print(os.getcwd())
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
    
    def save_to_json(self, path: str = None):
        path = path or os.getenv("EMAIL_CONFIG_PATH", "./src/config/params.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=4, ensure_ascii=False)


# def load_settings_from_json(path: str = "email_config.json") -> EmailSettings:
#     with open(path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     return EmailSettings(**data)



# class Settings(BaseSettings):
#     # load_dotenv()
#     DB_USER: str 
#     DB_PASSWORD: str
#     DB_HOST: str 
#     DB_NAME: str
#     DB_PORT: int

    
    
   
#     def get_params(self):
#         print(f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
#                 f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")
#         return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
#                 f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

        
settings = Settings.from_json()
