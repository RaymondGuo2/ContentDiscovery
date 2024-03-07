import unittest
from unittest.mock import patch, MagicMock
from app import app
import psycopg2


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
        self.assertEqual(
            response.json, {
                'message': 'There are no unique shows for this country.'})

    @patch('app.psycopg2.connect')
    def test_invalid_country_code(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/shows?country=ZZZ')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid country code."})


    @patch('app.psycopg2.connect')
    def test_database_connection_error(self, mock_connect):
        mock_connect.side_effect = psycopg2.OperationalError(
            "Could not connect to database")

        with app.test_client() as client:
            response = client.get('/shows?country=US')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json, {
                "error":
                "Internal server error, could not connect to database."
            })

    @patch('app.psycopg2.connect')
    def test_sql_injection(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/shows?country=GB; DROP TABLE netflix;')

        self.assertNotEqual(response.status_code, 500)

    @patch('app.psycopg2.connect')
    def test_search_valid_query(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("Bridget Jones's Baby",), ("Bridget Jones's Diary",)]
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/search?query=Bridget')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, [
                "Bridget Jones's Baby", "Bridget Jones's Diary"])

    @patch('app.psycopg2.connect')
    def test_search_no_results(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/search?query=UnknownShow')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch('app.psycopg2.connect')
    def test_search_special_characters(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value.cursor.return_value = mock_cursor

        with app.test_client() as client:
            response = client.get('/search?query=%; DROP TABLE netflix;--')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])


if __name__ == '__main__':
    unittest.main()
