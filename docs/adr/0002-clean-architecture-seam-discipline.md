# Clean Architecture seam discipline — ports only at real seams

We apply Ports & Adapters only where a real seam exists: a seam is real when at least two concrete Adapters are justified (e.g. production PostgreSQL Adapter + in-memory test Adapter, or real HTTP Adapter + mock Adapter for a true external dependency). A single-Adapter seam is indirection without benefit.

Consequence: `typing.Protocol` is only used where two Adapters are actually implemented. Domain modules do not define abstract base classes or protocols just because it "looks clean." The deletion test — imagining the protocol gone — is applied before every seam introduction.

The priority order for deepening follows INSTRUCTION.md: shared kernel → database layer → User/auth → Facility → Building → Control Cabinet → SPS Controller → SPS Controller System Type → Field Device → BACnet Object → Project → Project Resource Link → Live updates → Notifications.
