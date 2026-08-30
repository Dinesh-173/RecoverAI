from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

REQUIRED_DOCS = (
    "docs/architecture.md",
    "docs/security.md",
    "docs/evaluation.md",
    "docs/product.md",
    "docs/decisions.md",
)

REQUIRED_ARCHITECTURE_HEADINGS = (
    "# RecoverAI System Architecture",
    "## 2. Folder structure",
    "## 3. Database design",
    "## 4. API design",
    "## 5. Agent architecture",
    "## 6. ML architecture",
    "## 7. Policy architecture",
    "## 8. Razorpay integration architecture",
    "## 9. Testing strategy",
    "## 10. Security strategy",
    "## 11. Development phases (gates)",
)

REQUIRED_PATHS = (
    "backend/app/models",
    "backend/app/api",
    "backend/app/services",
    "backend/app/agents",
    "backend/app/policies",
    "backend/app/providers",
    "backend/app/workers",
    "backend/app/repositories",
    "backend/app/core",
    "backend/alembic",
    "frontend/app",
    "ml/data",
    "evaluation",
    "scripts",
    "docs",
)


def test_phase1_required_documentation_exists():
    missing = [rel for rel in REQUIRED_DOCS if not (ROOT / rel).is_file()]
    assert missing == [], f"Phase 1 docs missing: {missing}"


def test_phase1_architecture_contract_headings():
    text = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    missing = [h for h in REQUIRED_ARCHITECTURE_HEADINGS if h not in text]
    assert missing == [], f"architecture.md missing headings: {missing}"
    assert "LLM proposes" in text
    assert "policy engine" in text.lower()
    assert "alembic" in text.lower()
    assert "rzp_test_" in text or "Test Mode" in text


def test_phase1_monorepo_layout():
    missing = [rel for rel in REQUIRED_PATHS if not (ROOT / rel).exists()]
    assert missing == [], f"Phase 1 folder structure missing: {missing}"
