APP_DIR = "SimplyTransport"  # Name of the app directory.
STATIC_DIR = "static"  # Name of the static directory.
TEMPLATE_DIR = "templates"  # Name of the templates directory.

# Base directories for maps
MAPS_STATIC_BASE_DIR = f"{APP_DIR}/{TEMPLATE_DIR}/maps/static"
MAPS_TEMPLATES_BASE_DIR = "maps/static"

# Static Maps - Use STATIC when outside context of a Template(path)
# Base directories for static maps
MAPS_STATIC_BASE_DIR = f"{APP_DIR}/{TEMPLATE_DIR}/maps/static"
MAPS_TEMPLATES_BASE_DIR = "maps/static"
# Derived directories for static maps
MAPS_STATIC_ROUTES_DIR = f"{MAPS_STATIC_BASE_DIR}/routes"
MAPS_STATIC_STOPS_DIR = f"{MAPS_STATIC_BASE_DIR}/stops"
MAPS_TEMPLATES_ROUTES_DIR = f"{MAPS_TEMPLATES_BASE_DIR}/routes"
MAPS_TEMPLATES_STOPS_DIR = f"{MAPS_TEMPLATES_BASE_DIR}/stops"

# Cleanup
CLEANUP_DELAYS_AFTER_DAYS = 180
