#!/usr/bin/env python3
"""Test script for poverty predictor model"""

from models.predictor import predict_poverty

# Test case 1: Urban household with good conditions
print("Test 1: Urban household with good conditions")
result = predict_poverty(
    household_size=5,
    residence=1,  # Urban
    water_source=1,  # Safe
    toilet_type=1,  # Improved
    has_electricity=True,
    has_mobile_phone=True,
    has_radio=False,
    has_television=False,
    has_refrigerator=False,
    has_bicycle=False,
    has_motorcycle=False,
    has_car=False,
)
print(f"  Probability: {result['probability']:.2%}")
print(f"  Classification: {result['classification']}")
print(f"  Score: {result['score']}")
print()

# Test case 2: Rural household with poor conditions
print("Test 2: Rural household with poor conditions")
result = predict_poverty(
    household_size=8,
    residence=0,  # Rural
    water_source=0,  # Unsafe
    toilet_type=0,  # Unimproved
    has_electricity=False,
    has_mobile_phone=False,
    has_radio=False,
    has_television=False,
    has_refrigerator=False,
    has_bicycle=False,
    has_motorcycle=False,
    has_car=False,
)
print(f"  Probability: {result['probability']:.2%}")
print(f"  Classification: {result['classification']}")
print(f"  Score: {result['score']}")
print()

# Test case 3: Urban household with many assets
print("Test 3: Urban household with many assets")
result = predict_poverty(
    household_size=4,
    residence=1,  # Urban
    water_source=1,  # Safe
    toilet_type=1,  # Improved
    has_electricity=True,
    has_mobile_phone=True,
    has_radio=True,
    has_television=True,
    has_refrigerator=True,
    has_bicycle=True,
    has_motorcycle=True,
    has_car=True,
)
print(f"  Probability: {result['probability']:.2%}")
print(f"  Classification: {result['classification']}")
print(f"  Score: {result['score']}")
print()

print("✅ All tests completed successfully!")
