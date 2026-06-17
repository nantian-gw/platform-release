from pathlib import Path


def test_readme_links_repository_docs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "docs/architecture.md" in readme
    assert "docs/release-process.md" in readme
    assert (repo_root / "docs/architecture.md").exists()
    assert (repo_root / "docs/release-process.md").exists()
