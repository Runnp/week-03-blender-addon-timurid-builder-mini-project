# tests/test_generators.py

import bpy
import sys
import os

# Make sure project root is on the path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generators.base_building import generate_base
from generators.dome import generate_dome
from generators.minaret import generate_minarets
from generators.arch import generate_arches
from generators.courtyard import generate_courtyard
