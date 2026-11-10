from sqlalchemy import create_engine, text

from database_utilis_related.database import upgrade_legacy_sqlite
from database_utilis_related.models import CaregiverStatus


def test_old_caregivers_table_gets_status_column_as_pending(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path/'old.db'}")
    with eng.begin() as conn:  # the schema from before consent existed
        conn.execute(text("CREATE TABLE caregivers (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, cg_id INTEGER NOT NULL)"))
        conn.execute(text("INSERT INTO caregivers (user_id, cg_id) VALUES (1, 2)"))

    upgrade_legacy_sqlite(eng)
    upgrade_legacy_sqlite(eng)  # running again must be harmless

    with eng.connect() as conn:
        status = conn.execute(text("SELECT status FROM caregivers")).scalar()
    assert status == CaregiverStatus.PENDING.name
