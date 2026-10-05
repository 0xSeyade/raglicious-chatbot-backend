import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()

    print("Database URL:", settings.database_url)

    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )

    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text(
                    "SELECT current_user, current_database(), "
                    "inet_server_addr(), inet_server_port()"
                )
            )

            print("CONNECTED:", result.one())
    finally:
        await engine.dispose()


asyncio.run(main())
