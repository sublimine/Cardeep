"""Country-autopilot auto-pack extractors (Phase C).

€0, free-reuse public-source extractors that DERIVE a country pack's data from
open registries, so a new country can be onboarded without hand-authoring every
file. Each extractor produces a `countries/<CC>/...` artifact the generic engine
already knows how to consume, and degrades honestly (declared checkpoints, never
fabricated figures) wherever a source cannot support an auto-derivation.
"""
