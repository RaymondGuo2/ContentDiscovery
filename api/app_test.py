import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestGetShows(unittest.TestCase):
    def test_get_shows_valid_input(self):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('The Innocent',)]

        with patch('app.psycopg2.connect') as mock_connect:
            mock_connect.return_value.cursor.return_value = mock_cursor

            with app.test_client() as client:
                response = client.get('/shows?country=RS')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ['The Innocent'])

    @patch('app.psycopg2.connect')
    def test_empty_result_set(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/shows?country=CU')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'There are no unique shows for this country.'})

    @patch('app.psycopg2.connect')
    def test_invalid_country_code(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/shows?country=ZZZ')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid country code."})


if __name__ == '__main__':
    unittest.main()
