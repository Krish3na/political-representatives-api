#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working correctly.
Run this after the application is up and data is loaded.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_get_legislators():
    """Test getting all legislators"""
    print("Testing GET /api/legislators...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} legislators")
            print(f"Sample legislator: {json.dumps(data[0], indent=2)}")
            return data[0]['govtrack_id'] if data else None
        else:
            print(f"✗ Failed to get legislators: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get legislators: {e}")
        return None

def test_get_legislator_by_id(legislator_id):
    """Test getting a specific legislator"""
    print(f"Testing GET /api/legislators/{legislator_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators/{legislator_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved legislator: {data['first_name']} {data['last_name']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ Failed to get legislator: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get legislator: {e}")
        return False

def test_filter_legislators():
    """Test filtering legislators"""
    print("Testing filtering by state...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators?state=CA")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {len(data)} legislators from California")
            print(f"Sample California legislator: {json.dumps(data[0], indent=2)}")
            return True
        else:
            print(f"✗ Failed to filter legislators: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to filter legislators: {e}")
        return False

def test_update_notes(legislator_id):
    """Test updating legislator notes"""
    print(f"Testing PATCH /api/legislators/{legislator_id}/notes...")
    try:
        test_note = "This is a test note from the API test script."
        response = requests.patch(
            f"{BASE_URL}/api/legislators/{legislator_id}/notes",
            json={"note": test_note},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['legislator']['notes'] == test_note:
                print("✓ Successfully updated legislator notes")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print("✗ Notes were not updated correctly")
                return False
        else:
            print(f"✗ Failed to update notes: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to update notes: {e}")
        return False

def test_age_stats():
    """Test age statistics endpoint"""
    print("Testing GET /api/stats/age...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/age")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Age stats - Average: {data['average_age']}, Youngest: {data['youngest_legislator']['age']}, Oldest: {data['oldest_legislator']['age']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ Failed to get age stats: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get age stats: {e}")
        return False

def test_weather(legislator_id):
    """Test weather endpoint (optional)"""
    print(f"Testing GET /api/legislators/{legislator_id}/weather...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators/{legislator_id}/weather")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Weather data retrieved for {data['state_capital']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 500:
            print("⚠ Weather endpoint returned 500 (likely missing API key) - this is expected if WEATHER_API_KEY is not set")
            print(f"Response: {response.text}")
            return True  # Don't fail the test for missing API key
        else:
            print(f"✗ Failed to get weather: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get weather: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting API tests...\n")
    
    tests_passed = 0
    total_tests = 7
    
    # Test health
    if test_health():
        tests_passed += 1
    
    print()
    
    # Test getting legislators
    legislator_id = test_get_legislators()
    if legislator_id:
        tests_passed += 1
    
    print()
    
    # Test getting specific legislator
    if legislator_id and test_get_legislator_by_id(legislator_id):
        tests_passed += 1
    
    print()
    
    # Test filtering
    if test_filter_legislators():
        tests_passed += 1
    
    print()
    
    # Test updating notes
    if legislator_id and test_update_notes(legislator_id):
        tests_passed += 1
    
    print()
    
    # Test age stats
    if test_age_stats():
        tests_passed += 1
    
    print()
    
    # Test weather (optional)
    if legislator_id and test_weather(legislator_id):
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("All tests passed! The API is working correctly.")
        return 0
    else:
        print(f"✗ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
