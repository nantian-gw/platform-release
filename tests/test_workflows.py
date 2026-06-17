from pathlib import Path

import yaml


def test_validate_release_uses_node24_artifact_upload() -> None:
    workflow = Path(__file__).resolve().parents[1] / ".github/workflows/validate-release.yaml"
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))

    upload_refs = []
    for job in data["jobs"].values():
        for step in job["steps"]:
            uses = step.get("uses")
            if uses and uses.startswith("actions/upload-artifact@"):
                upload_refs.append(uses)

    assert upload_refs == ["actions/upload-artifact@v6"]
