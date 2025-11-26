#!/bin/bash

BASE_URL="http://localhost:8000"

# Login to get token (using existing user 'ash')
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=ash&password=pikachu")
TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "1. List Gyms"
curl -X GET "$BASE_URL/world/gyms" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "2. List Elite Four"
curl -X GET "$BASE_URL/world/elite-four" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "3. Challenge Pewter Gym (ID 1)"
curl -X POST "$BASE_URL/world/gyms/1/challenge" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "4. List My Badges"
curl -X GET "$BASE_URL/world/my-badges" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"
