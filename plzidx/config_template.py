
import secrets

default_config = dict(
	SECRET_KEY="development",
	MARKER_TAG="plzidx",
	INDEX_ALL_PADS=False,
	PAD_PERMISSION_FILTER=('freely', 'editable'),
	BRAND_BULMA_URL=None,
)

def create_config_template():
	return f"""## Example configuration for the hedgedoc-tag-searcher service
## Lines prefixed with one hash-sign (`#`) denote preset default values

## Keep this secret in production systems
SECRET_KEY = "{secrets.token_hex()}"

## Name, user, password, and host of the Hedgedoc database
## (only PostgreSQL (psycopg2) supported at the moment)
HEDGEDOC_DATABASE =
HEDGEDOC_DB_USER =
HEDGEDOC_DB_PASS =
HEDGEDOC_DB_HOST =

## Web URL of your pad (will be used to create links)
PAD_URL = "https://pad.example.com"

## SQLAlchemy URI for our own databse
## See https://docs.sqlalchemy.org/core/engines.html for possible values like
## "sqlite:///project.db" or "postgresql+psycopg2://name:pass@host:port/dbname"
SQLALCHEMY_DATABASE_URI = 

## This is the required tag to appear in this tool 
# MARKER_TAG = "{default_config["MARKER_TAG"]}"

## If the MARKER_TAG should be ignored and all pads indexed instead
## (does not override the PAD_PERMISSION_FILTER)
# INDEX_ALL_PADS = {default_config["INDEX_ALL_PADS"]}

## Only pads with these permissions will be indexed
## Possible tuple entries:
##   'freely', 'editable', 'limited', 'locked', 'protected', 'private'
# PAD_PERMISSION_FILTER = {default_config["PAD_PERMISSION_FILTER"]}

## For a customized theme, you can override the default CSS path
## If None, please install a current Bulma as static/css/bulma.min.css
# BRAND_BULMA_URL = {default_config["BRAND_BULMA_URL"]}
"""
