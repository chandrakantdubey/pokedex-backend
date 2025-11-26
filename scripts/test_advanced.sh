#!/bin/bash

BASE_URL="http://localhost:8000"

# Signup/Login (New user since DB reset)
curl -s -X POST "$BASE_URL/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"username": "red", "email": "red@mt.silver", "password": "..."}' > /dev/null

TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=red&password=...")
TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "1. Get Charmander (ID 4) Details (Check Evolution/Moves)"
# Note: Evolution data is nested in 'evolves_from_id' on the child, or we need to check if endpoint exposes it.
# The current endpoint just dumps the model, so we check 'moves'.
curl -X GET "$BASE_URL/pokemon/4" | grep -o "moves"
echo -e "\n"

echo "2. Catch Charmander"
curl -X POST "$BASE_URL/game/catch" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"pokemon_id": 4, "nickname": "Zard"}'
echo -e "\n"

echo "3. Check My Pokemon (Verify XP)"
curl -X GET "$BASE_URL/game/my-pokemon" \
     -H "Authorization: Bearer $TOKEN"
echo -e "\n"
