from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Autonomous Retail OS", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    database_url: str = Field(default="sqlite:///./retail_os.db", alias="DATABASE_URL")
    default_currency: str = Field(default="INR", alias="DEFAULT_CURRENCY")
    default_upi_payee_vpa: str = Field(default="merchant@upi", alias="DEFAULT_UPI_PAYEE_VPA")
    default_upi_payee_name: str = Field(
        default="Autonomous Retail Store",
        alias="DEFAULT_UPI_PAYEE_NAME",
    )
    auto_reorder_max_amount: float = Field(default=5000.0, alias="AUTO_REORDER_MAX_AMOUNT")
    auto_price_change_max_percent: float = Field(default=10.0, alias="AUTO_PRICE_CHANGE_MAX_PERCENT")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    ai_confidence_threshold: float = Field(default=0.7, alias="AI_CONFIDENCE_THRESHOLD")


def get_settings() -> Settings:
    return Settings()
