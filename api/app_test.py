import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestGetShows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_cursor = MagicMock()

    def setUp(self):
        self.mock_cursor.fetchall.reset_mock()

    @classmethod
    @patch('app.psycopg2.connect')
    def setUpClass(cls, mock_connect):
        cls.mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = cls.mock_cursor

    def test_get_shows_valid_input(self):
        self.mock_cursor.fetchall.return_value = [('The Innocent',)]

        with app.test_client() as client:
            response = client.get('/shows?country=RS')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ['The Innocent'])

    def test_empty_result_set(self):
        self.mock_cursor.fetchall.return_value = []

        with app.test_client() as client:
            response = client.get('/shows?country=CU')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {
                'message': 'There are no unique shows for this country.'})

    def test_invalid_country_code(self):
        with app.test_client() as client:
            response = client.get('/shows?country=ZZZ')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid country code."})


if __name__ == '__main__':
    unittest.main()
