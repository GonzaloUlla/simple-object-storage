"""Tests for simple_object_storage"""
import os
import sys

tests_directory = os.path.dirname(os.path.abspath(__file__))
sos_directory = os.path.join(
    os.path.dirname(tests_directory), "simple_object_storage"
)

sys.path.append(sos_directory)
