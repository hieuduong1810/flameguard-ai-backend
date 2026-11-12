"""Deterministic TEST_ONLY larger/empty variants; never a NASA data generator."""

import copy
from uuid import UUID, uuid5

from app.services.demo_manifest import fixture_rows


def pagination_manifest(investigations=105, associations=105, tags=25):
    manifest = copy.deepcopy(fixture_rows())
    manifest["collectionId"] = "synthetic-phase4-pagination-v1"
    namespace = UUID("4980f2bb-8b06-4c24-a0b2-1040de3c52dc")

    def key(name):
        return uuid5(namespace, name)

    tables = manifest["tables"]
    for i in range(4, investigations):
        tables["investigation"].append(
            {
                "id": key(f"page-inv-{i}"),
                "psi_id": f"SYNTHETIC-PAGE-{i}",
                "title": "Synthetic tied title",
                "research_purpose": None,
                "platform": None,
            }
        )
    template = tables["claim_source"][0]
    for i in range(len(tables["claim_source"]), associations):
        tables["claim_source"].append(
            {
                **template,
                "id": key(f"page-source-{i}"),
                "source_locator": f"TEST_ONLY page locator {i}",
            }
        )
    inv = tables["investigation"][0]["id"]
    for i in range(1, tags):
        identity = key(f"page-tag-{i}")
        tables["tag"].append(
            {
                "id": identity,
                "slug": f"synthetic-page-tag-{i}",
                "label": "Synthetic tag",
                "category": None,
            }
        )
        tables["investigation_tag"].append(
            {"id": key(f"page-itag-{i}"), "investigation_id": inv, "tag_id": identity}
        )
    return manifest


def comparison_manifest(*, swap_units=False):
    """Two synthetic studies with the same heterogeneous original label pairs."""
    manifest = copy.deepcopy(fixture_rows())
    tables = manifest["tables"]
    left, right = [r["id"] for r in tables["investigation"][:2]]
    left_runs = [r for r in tables["test_run"] if r["investigation_id"] == left]
    right_run = next(r for r in tables["test_run"] if r["investigation_id"] == right)
    namespace = UUID("4980f2bb-8b06-4c24-a0b2-1040de3c52dc")
    extra_run = {**right_run, "id": uuid5(namespace, "comparison-run")}
    tables["test_run"].append(extra_run)
    for index, (a, b) in enumerate(zip(left_runs, [right_run, extra_run], strict=True)):
        for row in [a, b]:
            row.update(
                gravity=f"TEST_GRAVITY_{index}",
                material_type=f"TEST_MATERIAL_{index}",
                sample_geometry=f"TEST_GEOMETRY_{index}",
            )
    left_measurements = [
        r for r in tables["measurement"] if r["test_run_id"] in {r["id"] for r in left_runs}
    ]
    right_measurement = next(
        r for r in tables["measurement"] if r["test_run_id"] == right_run["id"]
    )
    extra_measurement = {
        **right_measurement,
        "id": uuid5(namespace, "comparison-measurement"),
        "test_run_id": extra_run["id"],
    }
    tables["measurement"].append(extra_measurement)
    units = ["K", "mm/s"]
    for index, (a, b) in enumerate(
        zip(left_measurements, [right_measurement, extra_measurement], strict=True)
    ):
        a.update(observable=f"TEST_OBSERVABLE_{index}", unit=units[index])
        b.update(
            observable=a["observable"],
            unit=units[1 - index] if swap_units else units[index],
            measured_value=a["measured_value"],
            uncertainty=a["uncertainty"],
        )
    return manifest
