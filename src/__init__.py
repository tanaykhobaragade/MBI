"""MBI - Market Breadth Indicator for NIFTY MIDSMALLCAP 400."""

__version__ = "1.0.0"
__author__ = "MBI Project"
__description__ = "Automated Market Breadth Indicator for NIFTY MIDSMALLCAP 400"

# Make main modules easily importable
from src import core, fetchers, processors, utils

__all__ = ["core", "fetchers", "processors", "utils"]
