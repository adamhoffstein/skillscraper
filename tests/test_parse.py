import bs4
from skillscraper import parse
from pytest import raises


class TestParse:
    def test_read_local_text(self):
        result = parse.read_local_text("tests/test.txt")
        assert type(result) == str
        assert len(result) >= 0

    def test_read_local_text_error(self):
        with raises(Exception) as e:
            parse.read_local_text("tests/doesnotexist.txt")

    def test_read_local(self):
        result = parse.read_local("tests/test.html")
        assert type(result) == bs4.BeautifulSoup
