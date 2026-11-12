from contextlib import asynccontextmanager


@asynccontextmanager
async def read_unit_of_work(session):
    if session.in_transaction():
        raise RuntimeError("Read unit of work requires a fresh session")
    try:
        await session.connection(
            execution_options={
                "isolation_level": "REPEATABLE READ",
                "postgresql_readonly": True,
            }
        )
        yield session
    finally:
        await session.rollback()
