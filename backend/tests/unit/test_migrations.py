from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_revision_chain_is_linear():
    root = Path(__file__).resolve().parents[3]
    cfg = Config(str(root / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    revisions = list(script.walk_revisions())
    assert revisions, "expected at least one Alembic revision"
    heads = script.get_heads()
    assert len(heads) == 1
    assert heads[0] == "002_simulation_isolation"
    assert script.get_revision("001_initial").down_revision is None
