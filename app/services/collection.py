import asyncio
import hashlib
import json
import re
from pathlib import Path

from sqlalchemy.exc import DBAPIError

from app.models import Base
from app.repositories.collection import database_identity, inspect_fixture
from app.services.demo_manifest import fixture_rows, snapshot_rows
from app.services.errors import Phase4Error


async def admit_collection(session, settings, *, capture_content=False):
    try:
        if not settings.catalog_collection_manifest:
            raise ValueError
        path = Path(settings.catalog_collection_manifest)
        config = json.loads(await asyncio.to_thread(path.read_text, "utf-8"))
        from sqlalchemy.engine import make_url

        url = make_url(settings.database_url.get_secret_value())
        target = config["target"]
        identity = await database_identity(session)
        if (
            target["database"] != identity["database"]
            or target["databaseOid"] != identity["databaseOid"]
            or target["readRole"] != identity["role"]
            or target["host"] != url.host
            or target["port"] != (url.port or 5432)
            or identity["superuser"]
            or identity["canWrite"]
        ):
            raise ValueError
        # A missing origin/review declaration stays unknown. Curated publication
        # is a separate Data acceptance gate; raw stored statuses never grant it.
        config.setdefault("origin", "unknown")
        config.setdefault("reviewState", "unknown")
        if config["origin"] not in {"synthetic", "real", "unknown"} or config[
            "reviewState"
        ] not in {"unreviewed", "unknown"}:
            raise ValueError
        if config["origin"] == "synthetic":
            if config["reviewState"] != "unreviewed":
                raise ValueError
            manifest = await asyncio.to_thread(fixture_rows, path.parent / config["fixture"])
        else:
            if "fixture" in config:
                raise ValueError
            manifest = (
                await asyncio.to_thread(snapshot_rows, path.parent / config["snapshot"])
                if config.get("snapshot")
                else {
                    "collectionId": config["collectionId"],
                    "origin": config["origin"],
                    "tables": {name: [] for name in Base.metadata.tables},
                }
            )
            if manifest.get("origin", "unknown") != config["origin"]:
                raise ValueError
        if manifest["collectionId"] != config["collectionId"]:
            raise ValueError
        if capture_content:
            # Bind exact database and manifest originals, including Numeric scale.
            # Phase 4 keeps its existing admission and Decimal equivalence semantics.
            content = hashlib.sha256()
            await inspect_fixture(session, manifest, content_hash=content)
            config["phase5ContentHash"] = content.hexdigest()
            config["phase5DatasetVersion"] = (
                f"TEST_ONLY_fixture-v{manifest['version']}"
                if config["origin"] == "synthetic" and isinstance(manifest.get("version"), int)
                else None
            )
            config["phase5IdentityVersion"] = None
        else:
            await inspect_fixture(session, manifest)
        if config["origin"] != "synthetic" and not config.get("slugs"):
            return config, {}
        slugs = json.loads(
            await asyncio.to_thread((path.parent / config["slugs"]).read_text, "utf-8")
        )
        if slugs["collectionId"] != config["collectionId"]:
            raise ValueError
        entries = slugs["entries"]
        if (
            len({e["slug"] for e in entries}) != len(entries)
            or len({e["psiId"] for e in entries}) != len(entries)
            or any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", e["slug"]) for e in entries)
        ):
            raise ValueError
        if capture_content and config["origin"] == "synthetic":
            if isinstance(slugs.get("version"), int):
                config["phase5IdentityVersion"] = f"TEST_ONLY_slugs-v{slugs['version']}"
        return config, {e["psiId"]: e["slug"] for e in entries}
    except DBAPIError:
        raise Phase4Error("DATA_UNAVAILABLE") from None
    except Exception:
        raise Phase4Error("COLLECTION_SCOPE_INVALID") from None


def collection_context(config):
    origin = config.get("origin", "unknown")
    return {
        "collectionId": config["collectionId"],
        "origin": origin,
        "reviewState": config.get(
            "reviewState", "unreviewed" if origin == "synthetic" else "unknown"
        ),
        "caveats": [
            "Synthetic test data, not NASA evidence; verification is unavailable."
            if origin == "synthetic"
            else "Owner-declared origin; scientific review and verification are not established."
        ],
    }
