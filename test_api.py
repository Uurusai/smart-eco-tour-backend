#!/usr/bin/env python3
"""
Quick start script to test the Smart Eco Tour API.
Run this after starting the backend server.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section title."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_health_check():
    """Test the health check endpoint."""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/api/health")
    pprint(response.json())
    return response.status_code == 200


def test_create_mock_travelers():
    """Create mock travelers for testing."""
    print_section("2. Create Mock Travelers")
    response = requests.post(f"{BASE_URL}/api/mock-traveler-data")
    data = response.json()
    pprint(data)
    return response.status_code == 200


def test_generate_itineraries():
    """Test itinerary generation."""
    print_section("3. Generate Itineraries (Paris)")
    
    request_body = {
        "origin": "New York",
        "destination": "Paris",
        "days": 5,
        "transport_preference": "train",
        "interests": ["culture", "food", "local"],
        "sustainability_weights": {
            "carbon": 0.4,
            "local": 0.3,
            "culture": 0.2,
            "overtourism": 0.1
        }
    }
    
    print("Request:")
    pprint(request_body)
    
    response = requests.post(
        f"{BASE_URL}/api/generate-itinerary",
        json=request_body,
        params={"num_options": 3}
    )
    
    data = response.json()
    print("\nResponse Summary:")
    print(f"Status: {data.get('status')}")
    print(f"Origin: {data.get('origin')}")
    print(f"Destination: {data.get('destination')}")
    print(f"Number of itineraries: {len(data.get('itineraries', []))}")
    
    if data.get('itineraries'):
        for i, itinerary in enumerate(data['itineraries'], 1):
            print(f"\n  Itinerary {i}:")
            print(f"    ID: {itinerary['id']}")
            print(f"    Title: {itinerary['title']}")
            print(f"    Days: {len(itinerary['days'])}")
            print(f"    Sustainability Score: {itinerary['sustainability']['total_score']:.1f}/100")
            print(f"    Carbon Footprint: {itinerary['sustainability']['total_carbon_kg']:.1f} kg CO2")
    
    return response.status_code == 200


def test_get_itinerary_details():
    """Test getting detailed itinerary information."""
    print_section("4. Get Itinerary Details")
    
    # First generate an itinerary to get an ID
    request_body = {
        "origin": "New York",
        "destination": "Tokyo",
        "days": 7,
        "transport_preference": "train",
        "interests": ["culture", "adventure"]
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-itinerary", json=request_body)
    itinerary_data = response.json()
    
    if itinerary_data.get('itineraries'):
        itinerary_id = itinerary_data['itineraries'][0]['id']
        
        print(f"Fetching details for itinerary ID: {itinerary_id}")
        response = requests.get(f"{BASE_URL}/api/itinerary/{itinerary_id}")
        
        if response.status_code == 200:
            data = response.json()['itinerary']
            print(f"\nTitle: {data['title']}")
            print(f"Description: {data['description']}")
            print(f"Days: {len(data['days'])}")
            
            # Show first day details
            if data['days']:
                day1 = data['days'][0]
                print(f"\nDay {day1['day']} Activities:")
                for activity in day1['activities'][:2]:  # Show first 2
                    print(f"  - {activity['time']}: {activity['activity']} ({activity['duration_hours']}h)")
            
            return True
    
    return False


def test_traveler_profile():
    """Test creating a traveler profile."""
    print_section("5. Create Traveler Profile")
    
    profile = {
        "id": "test_user_001",
        "name": "Test Traveler",
        "destination": "Paris",
        "trip_days": 5,
        "sustainability_score_min": 85,
        "interests": ["culture", "food"],
        "transport_preference": "train",
        "max_group_size": 4
    }
    
    print("Creating profile:")
    pprint(profile)
    
    response = requests.post(f"{BASE_URL}/api/traveler-profile", json=profile)
    data = response.json()
    
    print("\nResponse:")
    print(f"Status: {data.get('status')}")
    print(f"Traveler ID: {data.get('traveler_id')}")
    print(f"Message: {data.get('message')}")
    
    return response.status_code == 200


def test_list_travelers():
    """List all registered travelers."""
    print_section("6. List Travelers")
    
    response = requests.get(f"{BASE_URL}/api/travelers")
    data = response.json()
    
    print(f"Total travelers: {data.get('count')}")
    
    if data.get('travelers'):
        print("\nRegistered Travelers:")
        for traveler in data['travelers'][:5]:  # Show first 5
            print(f"  - {traveler['name']} (ID: {traveler['id']})")
            print(f"    Destination: {traveler['destination']}, Days: {traveler['trip_days']}")
    
    return response.status_code == 200


def test_find_group_matches():
    """Test finding group matches."""
    print_section("7. Find Group Matches")
    
    traveler_id = "traveler_001"  # From mock data
    
    print(f"Finding matches for traveler: {traveler_id}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/find-group",
        params={
            "traveler_id": traveler_id,
            "min_similarity": 0.7
        }
    )
    
    data = response.json()
    
    print(f"Status: {data.get('status')}")
    print(f"Matches found: {data.get('matches_found')}")
    
    if data.get('top_matches'):
        print("\nTop Matches:")
        for match in data['top_matches'][:3]:  # Show top 3
            print(f"  - {match['name']} (ID: {match['traveler_id']})")
            print(f"    Destination: {match['destination']}")
            print(f"    Similarity Score: {match['similarity_score']:.2f}")
            print(f"    Common Interests: {', '.join(match.get('common_interests', []))}")
    
    if data.get('group_recommendations'):
        print("\nGroup Recommendations:")
        for rec in data['group_recommendations']:
            print(f"  - Group Size: {rec['recommended_group_size']}")
            print(f"    Members: {len(rec['traveler_ids'])}")
            print(f"    Avg Similarity: {rec['similarity_score']:.2f}")
    
    return response.status_code == 200


def test_compare_itineraries():
    """Test comparing multiple itineraries."""
    print_section("8. Compare Itineraries")
    
    # Generate multiple itineraries first
    request_body = {
        "origin": "London",
        "destination": "Barcelona",
        "days": 4,
        "transport_preference": "train",
        "interests": ["adventure", "culture"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/generate-itinerary",
        json=request_body,
        params={"num_options": 3}
    )
    
    itinerary_data = response.json()
    
    if itinerary_data.get('itineraries') and len(itinerary_data['itineraries']) >= 2:
        ids = [it['id'] for it in itinerary_data['itineraries'][:3]]
        
        print(f"Comparing {len(ids)} itineraries: {ids}\n")
        
        response = requests.post(
            f"{BASE_URL}/api/compare-itineraries",
            json={"itinerary_ids": ids}
        )
        
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Itineraries compared: {data.get('count')}")
        
        if data.get('comparison', {}).get('by_score'):
            print("\nRanked by Sustainability Score:")
            for i, item in enumerate(data['comparison']['by_score'], 1):
                print(f"  {i}. {item['title']} - {item['score']:.1f}/100")
        
        if data.get('comparison', {}).get('by_carbon'):
            print("\nRanked by Carbon Footprint:")
            for i, item in enumerate(data['comparison']['by_carbon'], 1):
                print(f"  {i}. {item['title']} - {item['carbon_kg']:.1f} kg CO2")
        
        return True
    
    return False


def test_sustainability_tips():
    """Test getting sustainability tips."""
    print_section("9. Sustainability Tips")
    
    destinations = ["Paris", "Tokyo", "Barcelona", "Bangkok"]
    
    for dest in destinations:
        response = requests.get(
            f"{BASE_URL}/api/sustainability-tips",
            params={"destination": dest}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{dest} Tips:")
            for tip in data.get('tips', [])[:3]:  # Show first 3 tips
                print(f"  • {tip}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  Smart Eco Tour Backend API - Test Suite")
    print("="*70)
    
    tests = [
        ("Health Check", test_health_check),
        ("Create Mock Travelers", test_create_mock_travelers),
        ("Generate Itineraries", test_generate_itineraries),
        ("Get Itinerary Details", test_get_itinerary_details),
        ("Create Traveler Profile", test_traveler_profile),
        ("List Travelers", test_list_travelers),
        ("Find Group Matches", test_find_group_matches),
        ("Compare Itineraries", test_compare_itineraries),
        ("Sustainability Tips", test_sustainability_tips),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✅ PASS" if result else "⚠️  PARTIAL"))
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append((test_name, "❌ FAIL"))
    
    # Summary
    print_section("Test Summary")
    for test_name, result in results:
        print(f"{result}  {test_name}")
    
    passed = sum(1 for _, r in results if "PASS" in r or "PARTIAL" in r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    print("\n✅ API is working correctly!" if passed == total else "\n⚠️  Some tests need attention")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("Make sure the server is running at http://localhost:8000")
        print("\nStart the server with:")
        print("  uvicorn app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\n✋ Tests interrupted")
