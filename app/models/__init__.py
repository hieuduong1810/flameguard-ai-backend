"""Import every approved model so Alembic and mapper configuration see all 21 tables."""

from app.models.base import Base
from app.models.catalog import (
    Investigation,
    InvestigationTag,
    Measurement,
    Tag,
    TestCondition,
    TestRun,
)
from app.models.chat import ChatMessage, ChatSession, MessageCitation
from app.models.evidence import ClaimSource, DocumentChunk, EvidenceClaim, SourceDocument
from app.models.ingestion import ImportIssue, IngestionJob
from app.models.prediction import ModelTrainingRun, ModelVersion, PredictionResult
from app.models.scenarios import MatchDimension, Scenario, ScenarioMatch

__all__ = [
    "Base",
    "Investigation",
    "TestRun",
    "TestCondition",
    "Measurement",
    "Tag",
    "InvestigationTag",
    "SourceDocument",
    "EvidenceClaim",
    "ClaimSource",
    "DocumentChunk",
    "Scenario",
    "ScenarioMatch",
    "MatchDimension",
    "ChatSession",
    "ChatMessage",
    "MessageCitation",
    "ModelVersion",
    "ModelTrainingRun",
    "PredictionResult",
    "IngestionJob",
    "ImportIssue",
]
