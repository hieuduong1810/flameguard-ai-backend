from unittest.mock import AsyncMock, Mock

import pytest

from app.services.unit_of_work import read_unit_of_work


async def test_read_transaction_configures_before_use_and_rolls_back():
    session = Mock(
        in_transaction=Mock(return_value=False), connection=AsyncMock(), rollback=AsyncMock()
    )
    with pytest.raises(ValueError):
        async with read_unit_of_work(session):
            session.connection.assert_awaited_once()
            assert session.connection.call_args.kwargs["execution_options"]["postgresql_readonly"]
            raise ValueError("test")
    session.rollback.assert_awaited_once()


async def test_existing_transaction_is_rejected():
    with pytest.raises(RuntimeError):
        async with read_unit_of_work(Mock(in_transaction=Mock(return_value=True))):
            pass
