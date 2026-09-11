from services.turso.repository import DB

def test_schema(tmp_path,monkeypatch):
 # smoke import; app DB path may be local
 db=DB(); assert db.one("select count(*) n from projects") is not None; db.close()
