from fastapi import FastAPI

from autonomous_retail_os.api import agents, cart, checkout, customers, events, products, sessions, stores
from autonomous_retail_os.config import get_settings
from autonomous_retail_os.database import init_db


def create_app() -> FastAPI:
    settings = get_settings()
    init_db()
    app = FastAPI(
        title=settings.app_name,
        description="Autonomous retail control plane for camera-assisted, UPI-first Indian stores.",
        version="0.1.0",
    )
    app.include_router(stores.router)
    app.include_router(products.router)
    app.include_router(sessions.router)
    app.include_router(customers.router)
    app.include_router(events.router)
    app.include_router(cart.router)
    app.include_router(checkout.router)
    app.include_router(agents.router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

    return app


app = create_app()
