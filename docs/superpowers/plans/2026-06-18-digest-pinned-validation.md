# Digest-Pinned Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure platform-release validation uses release images pulled from the digest-pinned `manifest.yaml` artifacts instead of mutable `latest` images.

**Architecture:** Keep command execution centralized in `tools/releasectl.py`, but allow `run_command` to receive a check-specific environment overlay. Pull the digest-pinned release images, retag them to local validation aliases derived from the platform version, and pass the aliases to gateway platform checks. The aliases avoid kind/containerd digest-only archive imports with missing `RepoTags`, while still proving the manifest digests.

**Tech Stack:** Python 3, pytest, bash wrappers, YAML manifest data.

---

### Task 1: Add Regression Test

**Files:**
- Modify: `tests/test_releasectl.py`

- [ ] **Step 1: Write the failing test**

Add a test after `test_run_validation_success_marks_component_and_platform_checks_passed`:

```python
def test_run_validation_platform_checks_use_manifest_image_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, manifest, manifest_schema_path, summary, summary_schema_path = write_release_inputs(tmp_path)
    workspace = tmp_path / ".work/v2026.06.0-rc1"
    calls: list[tuple[str, Path, dict[str, str] | None]] = []
    prepared: list[tuple[str, str]] = []

    def fake_checkout_repo(repo: str, commit: str, target: Path) -> Path:
        target.mkdir(parents=True, exist_ok=True)
        return target

    def fake_run_command(command: str, cwd: Path, env: dict[str, str] | None = None) -> None:
        calls.append((command, cwd, env))

    def fake_prepare_release_image_alias(source: str, alias: str) -> None:
        prepared.append((source, alias))

    monkeypatch.setattr(releasectl, "checkout_repo", fake_checkout_repo)
    monkeypatch.setattr(releasectl, "run_command", fake_run_command)
    monkeypatch.setattr(releasectl, "prepare_release_image_alias", fake_prepare_release_image_alias)

    releasectl.run_validation(
        registry,
        manifest,
        manifest_schema_path,
        summary,
        summary_schema_path,
        workspace,
    )

    assert prepared == [
        (
            "ghcr.io/nantian-gw/nantian-controlplane@sha256:" + "a" * 64,
            "nantian-gw-validation/controlplane:v2026.06.0-rc1",
        ),
        (
            "ghcr.io/nantian-gw/dataplane@sha256:" + "b" * 64,
            "nantian-gw-validation/dataplane:v2026.06.0-rc1",
        ),
    ]
    assert calls == [
        ("make build", workspace / "gateway", None),
        ("make test", workspace / "gateway", None),
        ("cargo build --workspace", workspace / "dataplane", None),
        (
            "make e2e-smoke",
            workspace / "gateway",
            {
                "CONTROL_PLANE_IMAGE": "nantian-gw-validation/controlplane:v2026.06.0-rc1",
                "DATA_PLANE_IMAGE": "nantian-gw-validation/dataplane:v2026.06.0-rc1",
            },
        ),
        (
            "make conformance",
            workspace / "gateway",
            {
                "CONTROL_PLANE_IMAGE": "nantian-gw-validation/controlplane:v2026.06.0-rc1",
                "DATA_PLANE_IMAGE": "nantian-gw-validation/dataplane:v2026.06.0-rc1",
            },
        ),
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python3 -m pytest tests/test_releasectl.py::test_run_validation_platform_checks_use_manifest_image_artifacts -q
```

Expected: FAIL because `run_command` currently accepts only `command` and `cwd`, and no environment overlay is passed.

### Task 2: Implement Digest-Pulled Local Alias Platform Check Environment

**Files:**
- Modify: `tools/releasectl.py`
- Modify: `tests/test_releasectl.py`

- [ ] **Step 1: Update `run_command` to accept an environment overlay**

Change:

```python
def run_command(command: str, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, shell=True, check=True)
```

to:

```python
def run_command(command: str, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, shell=True, check=True, env={**os.environ, **env} if env else None)
```

- [ ] **Step 2: Add manifest image extraction helper**

Add:

```python
def validation_image_alias(platform_version: str, component: str) -> str:
    return f"nantian-gw-validation/{component}:{platform_version}"


def release_image_aliases(manifest: dict) -> list[tuple[str, str]]:
    images = manifest.get("artifacts", {}).get("containerImages", {})
    aliases: list[tuple[str, str]] = []
    if gateway_image := images.get("gateway"):
        aliases.append((gateway_image, validation_image_alias(manifest["platformVersion"], "controlplane")))
    if dataplane_image := images.get("dataplane"):
        aliases.append((dataplane_image, validation_image_alias(manifest["platformVersion"], "dataplane")))
    return aliases


def prepare_release_image_alias(source: str, alias: str) -> None:
    subprocess.run(["docker", "pull", source], check=True)
    subprocess.run(["docker", "tag", source, alias], check=True)


def prepare_release_image_aliases(manifest: dict) -> None:
    for source, alias in release_image_aliases(manifest):
        prepare_release_image_alias(source, alias)


def platform_check_env(manifest: dict, repo_name: str) -> dict[str, str] | None:
    if repo_name != "gateway":
        return None

    aliases = dict(release_image_aliases(manifest))
    env = {
        "CONTROL_PLANE_IMAGE": aliases.get(manifest["artifacts"]["containerImages"].get("gateway", "")),
        "DATA_PLANE_IMAGE": aliases.get(manifest["artifacts"]["containerImages"].get("dataplane", "")),
    }
    env = {key: value for key, value in env.items() if value}
    return env or None
```

- [ ] **Step 3: Prepare aliases once and pass the environment to platform checks**

Change platform check execution from:

```python
run_command(check["run"], checkout)
```

to:

```python
env = platform_check_env(manifest, repo_name)
if env and not release_image_aliases_prepared:
    prepare_release_image_aliases(manifest)
    release_image_aliases_prepared = True
run_command(check["run"], checkout, env=env)
```

- [ ] **Step 4: Update existing command-capture test**

Update `test_run_validation_success_marks_component_and_platform_checks_passed` to capture `(command, cwd, env)` and expect `None` for component commands plus the local validation alias env for `make e2e-smoke` and `make conformance`.

- [ ] **Step 5: Run targeted tests**

Run:

```bash
.venv/bin/python3 -m pytest tests/test_releasectl.py::test_run_validation_success_marks_component_and_platform_checks_passed tests/test_releasectl.py::test_run_validation_platform_checks_use_manifest_image_artifacts -q
```

Expected: PASS.

### Task 3: Verify and Regenerate Release Evidence

**Files:**
- Modify: `results/v2026.06.0-rc4/summary.yaml`
- Modify: `results/v2026.06.0-rc4/test-matrix.md`
- Modify: `results/v2026.06.0-rc4/conformance.md`
- Modify: `results/v2026.06.0-rc4/artifacts.yaml`

- [ ] **Step 1: Run local validation tests**

Run:

```bash
make test
git diff --check
```

Expected: `13 passed` or higher if new tests were added; `git diff --check` produces no output.

- [ ] **Step 2: Remove stale validation workspace**

Run:

```bash
rm -rf .work/v2026.06.0-rc4
```

Expected: command exits 0. This removes only the generated platform-release validation workspace, not component worktrees.

- [ ] **Step 3: Re-run rc4 validation**

Run:

```bash
ulimit -c 0; CARGO_BUILD_JOBS=1 ./scripts/run-validation.sh releases/v2026.06.0-rc4/manifest.yaml results/v2026.06.0-rc4/summary.yaml .work/v2026.06.0-rc4
```

Expected: command exits 0 and `results/v2026.06.0-rc4/summary.yaml` reports all checks passed.

- [ ] **Step 4: Regenerate human-readable result files**

Run:

```bash
./scripts/collect-results.sh results/v2026.06.0-rc4/summary.yaml results/v2026.06.0-rc4/test-matrix.md results/v2026.06.0-rc4/conformance.md results/v2026.06.0-rc4/artifacts.yaml
```

Expected: command exits 0, `test-matrix.md` lists `gateway-api-conformance | passed`, and `conformance.md` says `Gateway API conformance status: passed`.

- [ ] **Step 5: Verify repository boundaries**

Run:

```bash
git status --short --branch
```

Expected: only platform-release files related to this plan are modified; component repositories remain untouched.
