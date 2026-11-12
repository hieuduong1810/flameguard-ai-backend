from app.integrations.scenario_evidence.execution import ProviderFailure, execute
from app.integrations.scenario_evidence.models import ProviderRequest
from app.integrations.scenario_evidence.protocols import RankingProvider
from app.integrations.scenario_evidence.rankings import SCALES, validate_ranking
from app.schemas.api.scenarios import EvaluationRequest, InvestigationIdentity, Rankings
from app.services.scenario_interpretation import fingerprint
from app.services.scenario_traversal import page_for


async def ranking_section(
    provider: RankingProvider | None,
    provider_request: ProviderRequest,
    request: EvaluationRequest,
    identities: tuple[InvestigationIdentity, ...] | None,
) -> tuple[Rankings, str | None]:
    if provider is None:
        return Rankings(state="unavailable", reason_codes=("RANKING_PROVIDER_UNAVAILABLE",)), None
    if identities is None:
        return Rankings(state="unavailable", reason_codes=("IDENTITY_LIMIT_EXCEEDED",)), None
    try:
        payload = await execute(provider.rank(provider_request))
        if payload is None:
            return Rankings(state="unavailable", reason_codes=("OUT_OF_SCOPE",)), None
        delivery, items = validate_ranking(payload, provider_request, identities)
        if delivery.algorithm_version != provider.version:
            raise ProviderFailure("PROVIDER_VERSION_CONFLICT", rejected=True)
    except ProviderFailure as exc:
        return Rankings(
            state="rejected" if exc.rejected else "unavailable",
            reason_codes=(exc.code,),
        ), None

    digest = fingerprint(delivery.model_dump(mode="json"))
    scope = provider_request.scope.model_copy(update={"ranking_fingerprint": digest})
    page = page_for(request, scope, "ranking_offset", len(items))
    return Rankings(
        state="evaluated",
        reason_codes=("NO_RANKINGS_IN_EXAMINED_PAGE",) if page.offset >= len(items) else (),
        items=items[page.offset : page.offset + page.limit],
        page=page,
        delivery_id=delivery.delivery_id,
        contract_version=delivery.contract_version,
        algorithm_version=delivery.algorithm_version,
        dataset_version=delivery.dataset_version,
        identity_version=delivery.identity_version,
        mapping_version=delivery.mapping_version,
        material_key=delivery.material_key,
        applicability=delivery.applicability,
        caveats=(delivery.caveat,),
        scales=SCALES,
    ), digest
