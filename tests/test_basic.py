from pathlib import Path
from core.template import render_from_template


def test_render_from_template(tmp_path: Path) -> None:
	tpl = tmp_path / "app.env.safe"
	tpl.write_text("API_KEY=\nDB_URL=\n")
	result = render_from_template(tpl, {"API_KEY": "x"})
	assert "API_KEY=x" in result
	assert "DB_URL=" in result


