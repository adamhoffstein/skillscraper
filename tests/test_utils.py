from skillscraper import utils

class TestUtils:
    def test_dir_create_if_not_exists(self):
        result = utils.create_dir_if_not_exists(path="./output")
        assert(result==None)


    def test_select_random_user_agent(self):
        result = utils.select_random_user_agent()
        assert result.startswith("Mozilla")


    def test_divide_chunks(self):
        items = [1,2,3,4,5,6]
        result = list(utils.divide_chunks(items, 2))
        assert result == [[1,2],[3,4],[5,6]]


