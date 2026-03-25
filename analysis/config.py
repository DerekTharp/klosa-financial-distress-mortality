"""Shared configuration for analysis scripts."""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "KLoSA Dataset (Korean Longitudinal Study of Aging)", "data")
OUT = os.path.join(BASE, "output")
