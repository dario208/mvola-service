from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "mvola-service"
    environment: str = "development"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+psycopg2://mvola:mvola@db:5432/mvola"

    # Mvola credentials
    mvola_access_token: str = ""
    mvola_partner_name: str = ""
    mvola_app_num: str = ""
    mvola_credit_num: str = ""
    mvola_requesting_org_transaction_reference: str = ""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore env vars that are not explicitly declared
    )


settings = Settings()
