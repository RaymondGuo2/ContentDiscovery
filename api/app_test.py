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


if __name__ == '__main__':
    unittest.main()
