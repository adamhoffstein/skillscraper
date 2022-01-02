import pandas as pd
import pytest
from skillscraper.parse import Extractor

CLEANED_DESCRIPTIONS = [
    "this is a test description about a job that requires python ",
    "this is a different test description about a python related job that requires sql and java knowledge ",
]

ORIGINAL_DESCRIPTIONS = [
    "This is a test description about a job thatRequires python.",
    "This is a different test description about a Python-related job that requires SQL and JavaKnowledge.",
]


@pytest.fixture
def extractor():
    return Extractor(descriptions=ORIGINAL_DESCRIPTIONS, target_path="tests")


@pytest.mark.parametrize("expected", [CLEANED_DESCRIPTIONS])
def test_extractor_clean_descriptions(extractor, expected):
    assert extractor.clean_descriptions == expected


@pytest.mark.parametrize("expected", [{"sql", "java", "python"}])
def test_keywords(extractor, expected):
    assert set(extractor.keywords) == expected


@pytest.mark.parametrize(
    "expected",
    [
        pd.DataFrame(
            {
                "keyword": ["python", "java", "sql"],
                "occurs": [2, 1, 1],
                "occurs_rate": [100.0, 50.0, 50.0],
            }
        )
    ],
)
def test_grouped_keywords(extractor, expected):
    assert extractor.grouped_keywords.equals(expected)


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "This is a quick-test to Check if the text is normalized properly.",
            "this is a quick test to check if the text is normalized properly ",
        )
    ],
)
def test_clean_text(extractor, text, expected):
    assert extractor.clean_text(text) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected", [("this sentence has java in it ", ["java"])]
)
async def test_get_keywords_task(extractor, text, expected):
    assert await extractor.get_keywords_task(item=text) == expected
