#!/usr/bin/env python3
"""
Test script for Dino Ventures Internal Wallet Service API
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_assets():
    """Test getting assets"""
    print("\n💰 Testing get assets...")
    response = requests.get(f"{BASE_URL}/assets")
    print(f"Status: {response.status_code}")
    assets = response.json()
    print(f"Assets: {json.dumps(assets, indent=2)}")
    return response.status_code == 200

def test_get_balances():
    """Test getting user balances"""
    print("\n👛 Testing get user balances...")
    response = requests.get(f"{BASE_URL}/balance/user_001")
    print(f"Status: {response.status_code}")
    balances = response.json()
    print(f"Balances: {json.dumps(balances, indent=2)}")
    return response.status_code == 200

def test_topup_transaction():
    """Test topup transaction"""
    print("\n📈 Testing topup transaction...")
    payload = {
        "transaction_type": "topup",
        "user_id": "user_001",
        "asset_code": "GC",
        "amount": 100.00,
        "description": "API test top-up",
        "idempotency_key": f"test_topup_{int(time.time())}"
    }
    
    response = requests.post(f"{BASE_URL}/transaction", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_purchase_transaction():
    """Test purchase transaction"""
    print("\n🛒 Testing purchase transaction...")
    payload = {
        "transaction_type": "purchase",
        "user_id": "user_001",
        "asset_code": "GC",
        "amount": 25.00,
        "description": "API test purchase",
        "idempotency_key": f"test_purchase_{int(time.time())}"
    }
    
    response = requests.post(f"{BASE_URL}/transaction", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_bonus_transaction():
    """Test bonus transaction"""
    print("\n🎁 Testing bonus transaction...")
    payload = {
        "transaction_type": "bonus",
        "user_id": "user_001",
        "asset_code": "LP",
        "amount": 50.00,
        "description": "API test bonus",
        "idempotency_key": f"test_bonus_{int(time.time())}"
    }
    
    response = requests.post(f"{BASE_URL}/transaction", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_transaction_history():
    """Test transaction history"""
    print("\n📜 Testing transaction history...")
    response = requests.get(f"{BASE_URL}/transaction/user_001/history")
    print(f"Status: {response.status_code}")
    history = response.json()
    print(f"History: {json.dumps(history, indent=2)}")
    return response.status_code == 200

def test_idempotency():
    """Test idempotency by sending same request twice"""
    print("\n🔄 Testing idempotency...")
    idempotency_key = f"test_idempotency_{int(time.time())}"
    
    payload = {
        "transaction_type": "bonus",
        "user_id": "user_002",
        "asset_code": "LP",
        "amount": 10.00,
        "description": "Idempotency test",
        "idempotency_key": idempotency_key
    }
    
    # First request
    response1 = requests.post(f"{BASE_URL}/transaction", json=payload)
    print(f"First request - Status: {response1.status_code}")
    print(f"First request - Response: {json.dumps(response1.json(), indent=2)}")
    
    # Second request (should return same transaction)
    response2 = requests.post(f"{BASE_URL}/transaction", json=payload)
    print(f"Second request - Status: {response2.status_code}")
    print(f"Second request - Response: {json.dumps(response2.json(), indent=2)}")
    
    # Check if both responses have the same transaction_id
    if response1.status_code == 200 and response2.status_code == 200:
        tx1_id = response1.json().get("transaction_id")
        tx2_id = response2.json().get("transaction_id")
        success = tx1_id == tx2_id
        print(f"Idempotency test {'✅ PASSED' if success else '❌ FAILED'}")
        return success
    return False

def main():
    """Run all tests"""
    print("🚀 Starting API Tests for Dino Ventures Wallet Service")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Get Assets", test_get_assets),
        ("Get Balances", test_get_balances),
        ("Topup Transaction", test_topup_transaction),
        ("Purchase Transaction", test_purchase_transaction),
        ("Bonus Transaction", test_bonus_transaction),
        ("Transaction History", test_transaction_history),
        ("Idempotency Test", test_idempotency),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    main()
