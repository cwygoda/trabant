#!uv run

from datetime import timedelta
from enum import IntEnum
from json import dumps, loads
from pathlib import Path

from skyfield.api import EarthSatellite, Time, load, wgs84

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
FIXTURE_DIR = BASE_DIR / "tests/fixtures"


class EventIndex(IntEnum):
    rise = 0
    culminate = 1
    set = 2


def main():
    omm_file = STATIC_DIR / "hotsat-1.json"
    omm_data = loads(omm_file.read_text())[0]
    ts = load.timescale()
    sat = EarthSatellite.from_omm(ts, omm_data)

    target = wgs84.latlon(52.0, 12.0)

    epoch = sat.epoch
    t0 = epoch
    t1 = t0 + timedelta(days=5)

    highest: list[Time] = [
        ti
        for ti, event in zip(*sat.find_events(target, t0, t1, altitude_degrees=30.0))
        if event == EventIndex.culminate
    ]

    events = []
    for ti in highest:
        events.append({
            "julian": float(ti.tt),
            "utc": ti.utc_datetime().isoformat()
        })

    data = {
        "omm": omm_data,
        "start": {
            "julian": t0.tt,
            "utc": t0.utc_datetime().isoformat()
        },
        "end": {
            "julian": t1.tt,
            "utc": t1.utc_datetime().isoformat()
        },
        "events": events
    }

    events_file = FIXTURE_DIR / "hotsat-1-events.json"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_file.write_text(dumps(data, indent=2))


if __name__ == "__main__":
    main()
