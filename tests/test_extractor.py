import pytest
from skillscraper.parse import Extractor

CLEANED_DESCRIPTIONS = [
    "this is a test description about a job that requires python ",
    "this is a different test description about a job that requires sql and java knowledge ",
]

ORIGINAL_DESCRIPTIONS = [
    "This is a test description about a job thatRequires python.",
    "This is a different test description about a job that requires SQL and JavaKnowledge.",
]


@pytest.fixture
def extractor():
    return Extractor(descriptions=ORIGINAL_DESCRIPTIONS, target_path="tests")


@pytest.mark.parametrize("expected", [CLEANED_DESCRIPTIONS])
def test_extractor_clean_descriptions(extractor, expected):
    assert extractor.clean_descriptions == expected


def test_keywords(extractor):
    assert set(extractor.keywords) == {" sql ", " java ", " python "}


