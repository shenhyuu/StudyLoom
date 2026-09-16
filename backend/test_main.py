import importlib
import os
import tempfile
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


class ProductionTests(unittest.TestCase):
    def test_first_boot_presence_media_and_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            os.environ['STUDYLOOM_DB'] = str(Path(directory) / 'nested' / 'room.db')
            from backend import main
            main = importlib.reload(main)
            with TestClient(main.app) as client:
                self.assertTrue(main.DB_PATH.exists())
                self.assertEqual(client.get('/api/rooms/current').status_code, 401)
                a = client.post('/api/users/join', json={'name': '甲'}).json()
                b = client.post('/api/users/join', json={'name': '乙'}).json()
                ha, hb = {'X-User-Id': a['token']}, {'X-User-Id': b['token']}
                room = client.get('/api/rooms/current', headers=ha).json()
                self.assertEqual(room['member_count'], 2)
                self.assertEqual({m['name'] for m in room['members']}, {'甲', '乙'})
                session = client.post('/api/focus/start', headers=ha).json()
                self.assertEqual(client.post('/api/focus/start', headers=ha).status_code, 409)
                self.assertEqual(client.post(f"/api/focus/{session['id']}/stop", headers=hb).status_code, 404)
                self.assertEqual(client.get('/api/rooms/current', headers=ha).json()['active_session']['id'], session['id'])
                with main.database() as db:
                    db.execute('UPDATE focus_sessions SET started_at=? WHERE id=?', (time.time() - 125, session['id']))
                self.assertEqual(client.post(f"/api/focus/{session['id']}/stop", headers=ha).json()['duration_minutes'], 2)
                self.assertEqual(client.post('/api/stitches', headers=ha, json={'content': '   '}).status_code, 422)
                self.assertEqual(client.post('/api/stitches', headers=ha, json={'content': '重启后保留'}).status_code, 201)
                playlist = client.get('/api/tracks').json()
                self.assertGreater(len(playlist), 0)
                for track in playlist:
                    response = client.get(track['audio_url'], headers={'Range': 'bytes=0-31'})
                    self.assertEqual(response.status_code, 206)
                    self.assertEqual(len(response.content), 32)
                    if track['lyrics_url']:
                        self.assertEqual(client.get(track['lyrics_url']).status_code, 200)
                client.post('/api/presence/leave', headers=hb)
                self.assertEqual(client.get('/api/rooms/current', headers=ha).json()['member_count'], 1)
                with main.database() as db:
                    db.execute('UPDATE users SET last_seen=? WHERE id=?', (time.time() - 60, b['id']))
                self.assertEqual(client.get('/api/rooms/current', headers=ha).json()['member_count'], 1)
                if main.DIST.is_dir():
                    self.assertEqual(client.get('/').status_code, 200)
            with TestClient(main.app) as client:
                room = client.get('/api/rooms/current', headers=ha).json()
                self.assertEqual(room['own_minutes'], 2)
                self.assertEqual(room['collective_minutes'], 2)
                self.assertEqual(room['stitches'][0]['content'], '重启后保留')
            os.environ.pop('STUDYLOOM_DB', None)


if __name__ == '__main__':
    unittest.main()
