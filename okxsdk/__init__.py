"""
Python SDK for the OKX API v5

"""
import logging

__version__ = "0.17.0"

# Library logging: records propagate to the application's handlers, and the
# null handler keeps "no handler found" noise out when nobody configures logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())
