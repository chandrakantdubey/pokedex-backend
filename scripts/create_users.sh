#!/bin/bash

BASE_URL="http://localhost:8000"

echo "Creating user 'ash'..."
curl -s -X POST "$BASE_URL/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"username": "ash", "email": "ash@pallet.town", "password": "pikachu"}'
echo -e "\nUser 'ash' created (or already exists)."

echo "Creating user 'chan'..."
curl -s -X POST "$BASE_URL/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"username": "chan", "email": "chan@fire.red", "password": "raichu"}'
echo -e "\nUser 'chan' created (or already exists)."
