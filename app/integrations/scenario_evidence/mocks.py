from app.integrations.scenario_evidence.classifications import FixedClassification
from app.integrations.scenario_evidence.config import ScenarioProviders
from app.integrations.scenario_evidence.rankings import FixedRanking
from app.integrations.scenario_evidence.run_policy import ExactFixturePolicy


def fixture_providers() -> ScenarioProviders:
    return ScenarioProviders(ExactFixturePolicy(), FixedRanking(), FixedClassification())
