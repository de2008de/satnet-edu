from pathlib import Path

from satnet_edu import load

ROOT = Path(__file__).resolve().parents[2]


def test_classic_matches_wheel_asset():
    assert (ROOT / "web/player/dist/satnet-edu-player.js").read_bytes() == (
        ROOT / "src/satnet_edu/assets/satnet-edu-player.js"
    ).read_bytes()


def test_all_committed_demo_traces():
    for path in (ROOT / "examples/data").glob("*.json"):
        load(path)


def test_packaged_schema_matches_contract():
    for name in ["trace", "scenario"]:
        assert (ROOT / f"schemas/{name}.schema.json").read_bytes() == (
            ROOT / f"src/satnet_edu/assets/{name}.schema.json"
        ).read_bytes()
