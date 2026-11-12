import pytest

from app.services.demo_seed import authorize_target
from app.services.errors import Phase4Error


@pytest.mark.parametrize(
    "change",
    [
        {"environment": "production"},
        {"environment": "staging"},
        {"opt_in": False},
        {"confirmation": "flameguard"},
        {"raw": "postgresql+asyncpg://u:p@remote/flameguard_test_x"},
        {"raw": "postgresql+asyncpg://u:p@127.0.0.1/flameguard"},
        {"raw": "postgresql+asyncpg://u:p@127.0.0.1/flameguard_test_x?host=remote"},
        {"authorization": {}},
        {"raw": ""},
    ],
)
def test_target_denial_without_connection(change):
    args = {
        "raw": "postgresql+asyncpg://u:p@127.0.0.1/flameguard_test_x",
        "environment": "test",
        "opt_in": True,
        "confirmation": "flameguard_test_x",
        "authorization": {
            "exclusiveDisposable": True,
            "environment": "test",
            "host": "127.0.0.1",
            "port": 5432,
            "database": "flameguard_test_x",
            "role": "u",
        },
    }
    args.update(change)
    with pytest.raises(Phase4Error, match="TARGET_NOT_AUTHORIZED"):
        authorize_target(**args)


def test_regular_database_is_rejected_even_with_test_name():
    raw = "postgresql+asyncpg://u:p@127.0.0.1/flameguard_test_x"
    auth = {
        "exclusiveDisposable": True,
        "environment": "test",
        "host": "127.0.0.1",
        "port": 5432,
        "database": "flameguard_test_x",
        "role": "u",
    }
    with pytest.raises(Phase4Error, match="TARGET_NOT_AUTHORIZED"):
        authorize_target(raw, "test", True, "flameguard_test_x", auth, regular_database_url=raw)
