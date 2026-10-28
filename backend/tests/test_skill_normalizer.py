"""Unit tests for skill normalization service."""
import pytest
from app.services.ai.skill_normalizer import SkillNormalizerService


def test_canonical_skill_name_mappings():
    normalizer = SkillNormalizerService()

    assert normalizer.normalize_skill_name("react.js") == "React"
    assert normalizer.normalize_skill_name("REACTJS") == "React"
    assert normalizer.normalize_skill_name("python3") == "Python"
    assert normalizer.normalize_skill_name("k8s") == "Kubernetes"
    assert normalizer.normalize_skill_name("postgres") == "PostgreSQL"
    assert normalizer.normalize_skill_name("aws") == "AWS"
    assert normalizer.normalize_skill_name("ts") == "TypeScript"
    assert normalizer.normalize_skill_name("UnknownCustomTech") == "UnknownCustomTech"


def test_skill_categories():
    normalizer = SkillNormalizerService()

    assert normalizer.get_category("React") == "Frontend"
    assert normalizer.get_category("FastAPI") == "Backend"
    assert normalizer.get_category("PostgreSQL") == "Database"
    assert normalizer.get_category("Docker") == "DevOps"
    assert normalizer.get_category("PyTorch") == "AI/ML"
    assert normalizer.get_category("UnknownSkill") == "Technical"
