#!/bin/bash

BASE_URL="http://localhost:8000"

# Login (using existing user 'red')
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=red&password=...")
TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "1. List Shop Items"
curl -X GET "$BASE_URL/shop/items" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "2. Buy Poke Ball (ID 1)"
# Need money first, let's win a battle
curl -X POST "$BASE_URL/game/battle" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"opponent_name": "Rich Boy", "result": "win", "money_earned": 1000}' > /dev/null

curl -X POST "$BASE_URL/shop/buy" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"item_id": 1, "quantity": 5}'
echo -e "\n"

echo "3. Check Bag"
curl -X GET "$BASE_URL/shop/bag" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "4. Wild Encounter"
curl -X GET "$BASE_URL/game/encounter" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"

echo "5. Set Party (Add Charmander)"
# Catch Charmander first
curl -X POST "$BASE_URL/game/catch" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"pokemon_id": 4, "nickname": "PartyZard"}' > /dev/null

# First get pokemon ID from my-pokemon
MY_POKEMON=$(curl -s -X GET "$BASE_URL/game/my-pokemon" -H "Authorization: Bearer $TOKEN")
POKEMON_ID=$(echo $MY_POKEMON | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])")

curl -X POST "$BASE_URL/game/party/set" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"user_pokemon_id\": $POKEMON_ID, \"is_in_party\": true}"
echo -e "\n"

echo "6. Check Party"
curl -X GET "$BASE_URL/game/party" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"
