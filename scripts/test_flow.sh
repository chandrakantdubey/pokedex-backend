#!/bin/bash

BASE_URL="http://localhost:8000"

echo "1. Signup"
curl -X POST "$BASE_URL/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"username": "ash", "email": "ash@pallet.town", "password": "pikachu"}'
echo -e "\n"

echo "2. Login"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=ash&password=pikachu")
echo "Token Response: $TOKEN_RESPONSE"
TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"
echo -e "\n"

echo "3. Get Profile"
curl -X GET "$BASE_URL/users/me" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "4. Catch Pokemon (Bulbasaur - ID 1)"
curl -X POST "$BASE_URL/game/catch" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"pokemon_id": 1, "nickname": "Bulby"}'
echo -e "\n"

echo "5. List My Pokemon"
curl -X GET "$BASE_URL/game/my-pokemon" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "6. Record Battle"
curl -X POST "$BASE_URL/game/battle" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"opponent_name": "Gary", "result": "win", "money_earned": 500}'
echo -e "\n"

echo "7. Check Money (Profile again)"
curl -X GET "$BASE_URL/users/me" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"
