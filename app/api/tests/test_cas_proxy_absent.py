from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
PROXY_VARIABLES = ("CAS_PROXY_HOST", "CAS_PROXY_LOOK4")


def test_no_backend_module_reads_the_cas_proxy() -> None:
    readers = [
        path.relative_to(BACKEND)
        for path in BACKEND.rglob("*.py")
        if ".venv" not in path.parts
        and "tests" not in path.parts
        and any(variable in path.read_text("utf-8") for variable in PROXY_VARIABLES)
    ]
    assert readers == []
