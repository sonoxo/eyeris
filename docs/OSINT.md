# EYERIS OSINT Integration

EYERIS can host OSINT adapters alongside its GeoVision components when the inputs are public or otherwise lawfully accessible.

## Initial artifact

The first OSINT artifact is `osint/run_tracker.sh`, a shell launcher for a local `tracker.py` entry point.

```bash
bash osint/run_tracker.sh
```

The current repository does **not** contain `tracker.py`; therefore this integration is a baseline launcher scaffold, not a completed tracking engine.

## Integration boundary

Future OSINT adapters should emit structured, reviewable records and should not bypass authentication, access controls, paywalls, or private systems. Any future tracker implementation should include tests, provenance fields, timestamps, source URLs/identifiers, and clear collection authorization.
