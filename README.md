# HedgeDoc Tag Searcher

> "Wasn't there a pad about that?"

This WiP tool is a global search for pads on a [HedgeDoc](https://github.com/hedgedoc/hedgedoc/) (pre v2) instance.

For a pad to be discoverable, it must explicitly ask to be indexed by providing the `plzidx` tag (can be configured). Try to encourage users in your organization to provide meaningful tags a and the marker if they want to have their work found by others.

Our use case is to build a hierarchical index akin to `https://<url>/tag1/tag2` for past projects. A *poor-peoples-wiki* so to say. This might not be your use case. Feel free to provide a pull request.

## Installation and Usage

It's a flask app. Use [gunicorn](https://flask.palletsprojects.com/en/2.3.x/deploying/gunicorn/) or comparable tools.
You will need to download [Bulma](https://bulma.io/) and put a `css/bulma.min.css` in your static path, or customize your CSS and supply a `BRAND_BULMA_URL` as flask config.

To get a list of available configuration options you can run the flask cli command `plzidx-ctrl createconfig`

```
$ python3 -m venv venv
$ flask plzidx-ctrl createconfig | sudo tee /etc/<your webapp path>/config.py
## Example configuration for the hedgedoc-tag-searcher service
## Lines prefixed with one hash-sign (`#`) denote preset default values

## Keep this secret in production systems
SECRET_KEY = "<your random secret here>"

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
# MARKER_TAG = "plzidx"

## If the MARKER_TAG should be ignored and all pads indexed instead
## (does not override the PAD_PERMISSION_FILTER)
# INDEX_ALL_PADS = False

## Only pads with these permissions will be indexed
## Possible tuple entries:
##   'freely', 'editable', 'limited', 'locked', 'protected', 'private'
# PAD_PERMISSION_FILTER = ('freely', 'editable')

## For a customized theme, you can override the default CSS path
## If None, please install a current Bulma as static/css/bulma.min.css
# BRAND_BULMA_URL = {default_config["BRAND_BULMA_URL"]}
```

To rebuild an index you can use a cronjob/systemd-timer periodically calling:

`$ flask plzidx-ctrl update`

## Limitations

Too many to count, but notable ones are:

* At the moment, `plzidx-ctrl update` rebuilds the entire index (expensive!). Given enough time we will eventually only do so on updated pads, or provide a PostgreSQL Hook. But hopefully this project will render itself superfluous, as soon as HedgeDoc 2 with its [Explore feature](https://github.com/hedgedoc/hedgedoc/issues/3833) gets released.
* Likewise, our tool needs read-access to the Hedgedoc database and expects a HedgeDoc pre-2 version. This will break, but again, then we hope this project is superfluous.
* Using `shortid`s is also deprecated.
