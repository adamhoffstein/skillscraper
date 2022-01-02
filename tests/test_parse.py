import bs4
from skillscraper import parse
from pytest import raises


class TestParse:
    def test_read_local_text(self):
        result = parse.read_local_text("tests/test.txt")
        assert type(result) == str
        assert len(result) >= 0

    def test_read_local_text_error(self):
        with raises(FileNotFoundError):
            parse.read_local_text("tests/doesnotexist.txt")

    def test_read_local_html(self):
        result = parse.read_local_html("tests/test.html")
        assert type(result) == bs4.BeautifulSoup

    def test_clean_text(self):
        result = parse.clean_text("this.is an example of a JobDescription.")
        expected = "this. is an example of a job description."
        assert result == expected
