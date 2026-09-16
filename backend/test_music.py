import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from backend import main


class SharedRadioTests(unittest.TestCase):
    def test_clock_history_concurrent_skips_and_restart(self):
        songs = [{'id': str(i), 'title': str(i), 'duration_seconds': 30.0} for i in range(4)]
        with tempfile.TemporaryDirectory() as directory, patch.object(main, 'DB_PATH', Path(directory) / 'music.db'), patch.object(main, 'tracks', return_value=songs), patch('backend.music.time.time', return_value=1000.0) as clock:
            with TestClient(main.app) as client:
                a = client.post('/api/users/join', json={'name': 'A'}).json()
                b = client.post('/api/users/join', json={'name': 'B'}).json()
                ha, hb = {'X-User-Id': a['token']}, {'X-User-Id': b['token']}
                self.assertEqual(client.get('/api/music/current').status_code, 401)
                initial = client.get('/api/music/current', headers=ha).json()
                self.assertEqual(initial, client.get('/api/music/current', headers=hb).json())
                clock.return_value = 1012.5
                self.assertEqual(client.get('/api/music/current', headers=hb).json()['track']['position_seconds'], 12.5)
                payload = {'direction': 'next', 'revision': initial['revision']}
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = list(pool.map(lambda headers: client.post('/api/music/skip', json=payload, headers=headers).json(), [ha, hb]))
                self.assertEqual(results[0], results[1])
                current = results[0]
                self.assertEqual(current['revision'], initial['revision'] + 1)
                self.assertNotEqual(current['track']['id'], initial['track']['id'])
                self.assertNotIn('volume', current)
                self.assertEqual(client.post('/api/music/skip', json={'direction': 'choose', 'revision': 0}, headers=ha).status_code, 422)
                previous = client.post('/api/music/skip', json={'direction': 'previous', 'revision': current['revision']}, headers=hb).json()
                self.assertEqual(previous['track']['id'], initial['track']['id'])
                self.assertEqual(previous['track']['position_seconds'], 0)
                clock.return_value = 1044.5
                advanced = client.get('/api/music/current', headers=ha).json()
                self.assertNotEqual(advanced['track']['id'], previous['track']['id'])
                self.assertEqual(advanced['track']['position_seconds'], 2)
            with TestClient(main.app) as client:
                self.assertEqual(advanced, client.get('/api/music/current', headers=hb).json())
            with patch.object(main, 'tracks', return_value=[]), TestClient(main.app) as client:
                self.assertIsNone(client.get('/api/music/current', headers=ha).json()['track'])
            with patch.object(main, 'tracks', return_value=[songs[0]]), TestClient(main.app) as client:
                single = client.get('/api/music/current', headers=ha).json()
                next_song = client.post('/api/music/skip', headers=ha, json={'direction': 'next', 'revision': single['revision']}).json()
                self.assertEqual(next_song['track']['id'], songs[0]['id'])
                self.assertEqual(next_song['track']['position_seconds'], 0)

    def test_real_library_durations(self):
        songs = main.tracks()
        self.assertTrue(songs)
        self.assertTrue(all(song['duration_seconds'] > 0 for song in songs))


if __name__ == '__main__':
    unittest.main()
