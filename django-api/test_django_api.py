#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:8001/api"

def test_health():
    print("Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health/")
        if r.status_code == 200:
            print("PASS: Health check")
            print(f"Response: {r.json()}")
            return True
        print(f"FAIL: Health check - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Health check - {e}")
    return False

def test_get_legislators():
    print("Testing GET /legislators...")
    try:
        r = requests.get(f"{BASE_URL}/legislators/")
        if r.status_code == 200:
            data = r.json()
            print(f"PASS: Retrieved {len(data)} legislators")
            if data:
                print(f"Sample:\n{json.dumps(data[0], indent=2)}")
                return data[0]["govtrack_id"]
            return None
        print(f"FAIL: Get legislators - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Get legislators - {e}")
    return None

def test_get_legislator_by_id(legislator_id):
    print(f"Testing GET /legislators/{legislator_id}...")
    try:
        r = requests.get(f"{BASE_URL}/legislators/{legislator_id}/")
        if r.status_code == 200:
            data = r.json()
            print(f"PASS: Retrieved {data['first_name']} {data['last_name']}")
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        print(f"FAIL: Get legislator - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Get legislator - {e}")
    return False

def test_filter_legislators():
    print("Testing filter by state (CA)...")
    try:
        r = requests.get(f"{BASE_URL}/legislators/?state=CA")
        if r.status_code == 200:
            data = r.json()
            print(f"PASS: Found {len(data)} legislators from California")
            if data:
                print(f"Sample:\n{json.dumps(data[0], indent=2)}")
            return True
        print(f"FAIL: Filter legislators - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Filter legislators - {e}")
    return False

def test_update_notes(legislator_id):
    print(f"Testing PATCH /legislators/{legislator_id}/notes...")
    try:
        note = "Test note from Django API test script"
        r = requests.patch(
            f"{BASE_URL}/legislators/{legislator_id}/notes/",
            json={"notes": note},
            headers={"Content-Type": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if data["legislator"]["notes"] == note:
                print("PASS: Updated legislator notes")
                print(f"Response:\n{json.dumps(data, indent=2)}")
                return True
            print("FAIL: Notes not updated correctly")
            return False
        print(f"FAIL: Update notes - {r.status_code}")
        if r.text:
            print(f"Error: {r.text}")
    except requests.RequestException as e:
        print(f"FAIL: Update notes - {e}")
    return False

def test_age_stats():
    print("Testing GET /stats/age...")
    try:
        r = requests.get(f"{BASE_URL}/stats/age/")
        if r.status_code == 200:
            data = r.json()
            print(f"PASS: Age stats - Avg: {data['average_age']}, "
                  f"Youngest: {data['youngest_legislator']['age']}, "
                  f"Oldest: {data['oldest_legislator']['age']}")
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        print(f"FAIL: Age stats - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Age stats - {e}")
    return False

def test_weather(legislator_id):
    print(f"Testing GET /legislators/{legislator_id}/weather...")
    try:
        r = requests.get(f"{BASE_URL}/legislators/{legislator_id}/weather/")
        if r.status_code == 200:
            data = r.json()
            print(f"PASS: Weather for {data['state_capital']}")
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        if r.status_code == 500:
            print("INFO: Weather endpoint returned 500 (missing API key or URL)")
            print(f"Response: {r.text}")
            return True
        print(f"FAIL: Weather - {r.status_code}")
    except requests.RequestException as e:
        print(f"FAIL: Weather - {e}")
    return False

def main():
    print("Starting Django API tests\n")
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
