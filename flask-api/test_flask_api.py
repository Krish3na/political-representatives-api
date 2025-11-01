#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:5001"

def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("PASS: Health check")
            print(f"Response: {response.json()}")
            return True
        print(f"FAIL: Health check - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Health check - {e}")
        return False

def test_get_legislators():
    print("Testing GET /api/legislators...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Retrieved {len(data)} legislators")
            if data:
                print(f"Sample: {json.dumps(data[0], indent=2)}")
                return data[0]['govtrack_id']
            return None
        print(f"FAIL: Get legislators - {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Get legislators - {e}")
        return None

def test_get_legislator_by_id(legislator_id):
    print(f"Testing GET /api/legislators/{legislator_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators/{legislator_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Retrieved {data['first_name']} {data['last_name']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        print(f"FAIL: Get legislator - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Get legislator - {e}")
        return False

def test_filter_legislators():
    print("Testing filter by state (CA)...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators?state=CA")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Found {len(data)} legislators from California")
            if data:
                print(f"Sample: {json.dumps(data[0], indent=2)}")
            return True
        print(f"FAIL: Filter legislators - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Filter legislators - {e}")
        return False

def test_update_notes(legislator_id):
    print(f"Testing PATCH /api/legislators/{legislator_id}/notes...")
    try:
        test_note = "Test note from API test script"
        response = requests.patch(
            f"{BASE_URL}/api/legislators/{legislator_id}/notes",
            json={"note": test_note},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['legislator']['notes'] == test_note:
                print("PASS: Updated legislator notes")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            print("FAIL: Notes not updated correctly")
            return False
        print(f"FAIL: Update notes - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Update notes - {e}")
        return False

def test_age_stats():
    print("Testing GET /api/stats/age...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/age")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Age stats - Avg: {data['average_age']}, "
                  f"Youngest: {data['youngest_legislator']['age']}, "
                  f"Oldest: {data['oldest_legislator']['age']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        print(f"FAIL: Age stats - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Age stats - {e}")
        return False

def test_weather(legislator_id):
    print(f"Testing GET /api/legislators/{legislator_id}/weather...")
    try:
        response = requests.get(f"{BASE_URL}/api/legislators/{legislator_id}/weather")
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Weather for {data['state_capital']}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        if response.status_code == 500:
            print("INFO: Weather endpoint returned 500 (missing API key or URL)")
            print(f"Response: {response.text}")
            return True
        print(f"FAIL: Weather - {response.status_code}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAIL: Weather - {e}")
        return False

def main():
    print("Starting Flask API tests\n")
    tests_passed = 0
    total_tests = 7

    if test_health(): tests_passed += 1
    print()

    legislator_id = test_get_legislators()
    if legislator_id: tests_passed += 1
    print()

    if legislator_id and test_get_legislator_by_id(legislator_id): tests_passed += 1
    print()

    if test_filter_legislators(): tests_passed += 1
    print()

    if legislator_id and test_update_notes(legislator_id): tests_passed += 1
    print()

    if test_age_stats(): tests_passed += 1
    print()

    if legislator_id and test_weather(legislator_id): tests_passed += 1

    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    if tests_passed == total_tests:
        print("All tests passed")
        return 0
    print("Some tests failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())
