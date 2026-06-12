"""Platform-as-entity harvesters — wholesale harvest of OPEN marketplaces.

A platform (AutoScout24, autocasion, ...) is an `entity` of kind='plataforma'.
Its wholesale /lst stream yields cars OWNED BY their selling dealer (a normal
entity) and LINKED to the platform via the `platform_listing` edge (dual
membership: ownership is singular, platform membership is plural).
"""
