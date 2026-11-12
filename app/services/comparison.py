from app.schemas.api.queries import PageQuery
from app.services.catalog import CatalogService
from app.services.errors import Phase4Error


def observation_caveats(studies):
    """Describe only stored labels and loaded pages, never physical comparability."""
    caveats, label_sets, run_labels = [], [], []
    for index, study in enumerate(studies, 1):
        page = study["observations"]
        observations = page["items"]
        reasons = set()
        if page["offset"] or page["next"] or len(observations) < page["total"]:
            reasons.add("PARTIAL_OBSERVATION_PAGE: only the returned page was examined")
        if not observations:
            reasons.add("NO_OBSERVATIONS_ON_PAGE: no collection-wide absence is inferred")
        observables, units = set(), set()
        observable_units = {}
        metadata = {key: set() for key in ("gravity", "material_type", "sample_geometry")}
        for item in observations:
            measurement, run = item["measurement"], item["run"]
            for key, labels in metadata.items():
                if run.get(key) is not None:
                    labels.add(run[key])
            observable, unit = measurement["observable"], measurement["unit"]
            if observable and observable.strip():
                observables.add(observable)
            else:
                reasons.add("MISSING_OBSERVABLE_LABEL")
            if unit and unit.strip():
                units.add(unit)
                if observable and observable.strip():
                    observable_units.setdefault(observable, set()).add(unit)
            else:
                reasons.add("MISSING_UNIT_LABEL")
            if measurement["measured_value"] is None:
                reasons.add("MISSING_VALUE: null is not zero")
            if any(run.get(key) is None for key in ("gravity", "material_type", "sample_geometry")):
                reasons.add("MISSING_RUN_CONTEXT: stored run metadata is incomplete")
            reasons.add(
                "CONDITIONS_MISSING: no stored conditions for an examined run"
                if run["conditions"]["total"] == 0
                else "CONDITIONS_NOT_EXAMINED: follow condition pages; no compatibility is inferred"
            )
        label_sets.append((observables, units, observable_units))
        run_labels.append(metadata)
        caveats.extend(f"Study {index}: {reason}." for reason in sorted(reasons))
    for left in range(len(studies)):
        for right in range(left + 1, len(studies)):
            a, b = label_sets[left], label_sets[right]
            prefix = f"Studies {left + 1}/{right + 1}, examined pages only: "
            if a[0] and b[0] and a[0] != b[0]:
                caveats.append(prefix + "OBSERVABLE_LABEL_MISMATCH; original labels differ.")
            common = a[2].keys() & b[2].keys()
            if (
                a[1]
                and b[1]
                and (
                    a[1] != b[1]
                    or any(a[2][observable] != b[2][observable] for observable in common)
                )
            ):
                caveats.append(prefix + "UNIT_LABEL_MISMATCH; no conversion is performed.")
            if a[0] != b[0]:
                caveats.append(
                    prefix + "UNMATCHED_OBSERVABLE; label absent on the other page, "
                    "not necessarily absent from the investigation."
                )
            differing = [
                key
                for key in run_labels[left]
                if run_labels[left][key]
                and run_labels[right][key]
                and run_labels[left][key] != run_labels[right][key]
            ]
            if differing:
                caveats.append(
                    prefix
                    + "RUN_CONTEXT_LABEL_MISMATCH: stored "
                    + ", ".join(differing)
                    + " labels differ; physical equivalence "
                    "is not assessed."
                )
    return caveats


class ComparisonService(CatalogService):
    async def compare(self, request):
        rows = await self.repo.bulk_investigations(request.investigation_ids)
        if len(rows) != len(request.investigation_ids):
            raise Phase4Error("ENTITY_NOT_FOUND", 404)
        by_id = {r.id: r for r in rows}
        ordered = [by_id[i] for i in request.investigation_ids]
        investigations = await self.investigation_views(ordered)
        page = PageQuery(offset=request.observation_offset, limit=request.observation_limit)
        studies = []
        for row, view in zip(ordered, investigations, strict=True):
            studies.append(
                {
                    "investigation": view,
                    "observations": await self.observations(row.id, page),
                    "context": self.context,
                }
            )
        return {
            "studies": studies,
            "deltas": None,
            "highlights": None,
            "comparability": "not_established",
            "unavailableFields": {
                "deltas": "SCIENTIFIC_COMPARISON_NOT_APPROVED",
                "highlights": "SCIENTIFIC_COMPARISON_NOT_APPROVED",
            },
            "context": {
                **self.context,
                "caveats": [
                    *self.context["caveats"],
                    "Original observations only; units, methods and conditions "
                    "are not established as comparable.",
                    *observation_caveats(studies),
                ],
            },
        }
