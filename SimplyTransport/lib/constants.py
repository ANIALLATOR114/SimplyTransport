APP_DIR = "SimplyTransport"
"""Name of the app directory."""

STATIC_DIR = "static"
"""Name of the static directory."""
TEMPLATE_DIR = "templates"
"""Name of the templates directory."""

# Use these constants when outside Template context
MAPS_STATIC_DIR = f"{APP_DIR}/{TEMPLATE_DIR}/maps/static"
"""Name of the maps static directory."""
MAPS_STATIC_ROUTES_DIR = f"{MAPS_STATIC_DIR}/routes"
"""Name of the maps static routes directory."""
MAPS_STATIC_STOPS_DIR = f"{MAPS_STATIC_DIR}/stops"
"""Name of the maps static stops directory."""

# Use these constants when inside Template context
MAPS_TEMPLATES_DIR = "maps/static"
"""Name of the maps templates directory."""
MAPS_TEMPLATES_ROUTES_DIR = f"{MAPS_TEMPLATES_DIR}/routes"
"""Name of the maps templates routes directory."""
MAPS_TEMPLATES_STOPS_DIR = f"{MAPS_TEMPLATES_DIR}/stops"
"""Name of the maps templates stops directory."""