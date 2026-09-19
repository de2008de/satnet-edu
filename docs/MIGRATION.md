# From the supplied prototypes

- `satlab` import and old export functions → `satnet_edu.Network`, Run.save/export_html.
- Old `satlab/model.py` is not imported; the adapted original UserGS propagation is used.
- UI route selection and disable buttons → Python `record_routes` and `add_failure`.
  The player only chooses recorded queries. Modify Python/configuration and re-run
  when you want new endpoints, models, parameters or failures.
- Paper Task/Bid/Dish objects → generic RouteQuery/GroundStation records.
- Mutation-heavy `route_traffic()` → immutable `Snapshot.route()`.
- CSV experiment aggregates → versioned full JSON traces. Old CSV/old UI JSON is not
  accepted as new trace data and is not silently converted.
- Website-specific branding/navigation → independent SatNet Edu component. Hosts
  can supply their own surrounding page, without changing the player.

Historical filenames remain under handoff for provenance. They are not dependencies
of a wheel installation. No UDTJ resources, server, Flask, React, account or CDN is needed.
The original M1 minimal page is preserved in commit da5021a as milestone evidence.
Its current replacement uses the same final player/parser as every other demo.
