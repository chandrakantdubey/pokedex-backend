# Pokédex RPG Backend Engine Documentation

This project is a high-performance REST backend API constructed with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. It operates the game loops, transaction queries, account state, and math mechanics for a complete Pokémon RPG system.

---

## 1. System Architecture

The server is structured as a layered, modular API using FastAPI's routing system:
- **Presentation Layer (`app/routers/`)**: Receives HTTP requests, executes validation, maps Pydantic schemas, and coordinates controller logic.
- **Service & Calculation Layer (`app/game_logic.py`)**: Runs core mathematical models (experience curves, stat derivation, breeding matching rules).
- **Data Access Layer (`app/crud.py`)**: Coordinates database operations, transaction commits, record inserts, and states updating.
- **Data Layer (`app/models.py`)**: Defines physical PostgreSQL schemas, index mappings, and relational tables.

---

## 2. Environment Configurations (`.env`)

Configure the backend variables in a local `.env` file copied from `.env.example`:

| Environment Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DB_USER` | String | `user` | Username credential for the PostgreSQL service. |
| `DB_PASSWORD` | String | `password` | Password credential for the PostgreSQL service. |
| `DB_HOST` | String | `db` | Network hostname of the database server. Set to `localhost` for local environments. |
| `DB_PORT` | Integer | `5432` | Incoming port for the PostgreSQL daemon. |
| `DB_DATABASE` | String | `pokedex` | Physical database name to connect or target. |
| `SECRET_KEY` | String | *Auto-generated* | HMAC-SHA256 signature salt key used to sign Auth JWTs. |
| `DATABASE_URL` | String | `""` | Optional connection URI override string (e.g., in production). |
| `PGADMIN_EMAIL` | String | `admin@example.com` | Access credential for pgAdmin container admin panel. |
| `PGADMIN_PASSWORD` | String | `admin` | Access password for pgAdmin container panel. |
| `PGADMIN_PORT` | Integer | `5050` | HTTP proxy port exposed to access pgAdmin panel locally. |

---

## 3. Database Schema Blueprint

```
            +------------------+         +-----------------+
            |      users       | <-----+ |  user_pokemon   |
            +------------------+         +-----------------+
            | id (PK)          |         | id (PK)         |
            | username (Unique)|         | user_id (FK)    |
            | email (Unique)   |         | pokemon_id (FK) |
            | money            |         | level           |
            | is_champion      |         | experience      |
            +------------------+         | current_hp      |
                     |                   | is_in_party     |
                     |                   +-----------------+
                     v
            +------------------+
            |   user_badges    |
            +------------------+
            | id (PK)          |
            | user_id (FK)     |
            | gym_id (FK)      |
            +------------------+
```

### Table Definitions

1. **`users`**: Trainer account profiles.
   - `id` (PK, Integer, Unique index)
   - `username` (String, Indexed, Unique)
   - `email` (String, Indexed, Unique)
   - `hashed_password` (String)
   - `money` (Integer, Default `3000`)
   - `elite_four_progress` (Integer, `0` to `4`)
   - `is_champion` (Boolean, Default `False`)
   - `created_at` (DateTime)

2. **`pokemon`**: Statistical and resource index of specific Pokémon variants.
   - `id` (PK, Integer)
   - `name` (String, Indexed)
   - `species_id` (Integer, FK -> `pokemon_species.id`)
   - `height` (Integer) - Decimetres
   - `weight` (Integer) - Hectograms
   - `base_experience` (Integer)
   - `sprites` (JSON string map of asset links)
   - `stats` (JSON map of base status attributes: `{hp, attack, defense, specialized attack, specialized defense, speed}`)

3. **`pokemon_species`**: Taxonomic details for evolutionary links.
   - `id` (PK, Integer)
   - `name` (String)
   - `gender_rate` (Integer: -1 genderless, 0 always male, 8 always female, 1-7 ratio in eighths)
   - `capture_rate` (Integer: 1-255 catch probability multiplier)
   - `growth_rate_id` (FK -> `growth_rates.id`)
   - `evolves_from_species_id` (FK -> `pokemon_species.id` self-reference)
   - `evolution_level` (Integer) - Level requirement for evolution trigger
   - `evolution_species_id` (Integer, FK -> `pokemon_species.id` target)

4. **`user_pokemon`**: Individual instance elements captured by players.
   - `id` (PK, Integer)
   - `user_id` (FK -> `users.id`)
   - `pokemon_id` (FK -> `pokemon.id`)
   - `nickname` (String, Optional)
   - `level` (Integer, Default `1`)
   - `experience` (Integer, Default `0`)
   - `is_in_party` (Boolean, Default `False`)
   - `gender` (String: Male, Female, Genderless)
   - `individual_values` (JSON map of IV stat variables: `0` to `31` per attribute)
   - `is_shiny` (Boolean)
   - Stats fields: `current_hp`, `max_hp`, `attack`, `defense`, `special_attack`, `special_defense`, `speed` (Calculated on instantiation/level-up)

5. **`moves`**: Combat actions.
   - `id` (PK, Integer)
   - `name` (String)
   - `type_id` (FK -> `types.id`)
   - `power` (Integer, Optional)
   - `pp` (Integer)
   - `accuracy` (Integer, Optional)
   - `damage_class` (String: special, physical, status)

6. **`user_berry_plots`**: Berry nursery engine.
   - `id` (PK, Integer)
   - `user_id` (FK -> `users.id`)
   - `berry_id` (FK -> `berries.id`, Nullable)
   - `planted_at` (DateTime, Nullable)
   - `last_watered_at` (DateTime, Nullable)
   - `growth_stage` (Integer: `0` Empty, `1` Seedling, `2` Growing, `3` Mature, `4` Harvestable)

7. **`breeding_sessions`**: Active Daycare records.
   - `id` (PK, Integer)
   - `user_id` (FK -> `users.id`)
   - `parent_one_id` (FK -> `user_pokemon.id`)
   - `parent_two_id` (FK -> `user_pokemon.id`)
   - `started_at` (DateTime)
   - `egg_available_at` (DateTime) - Timestamp check for claim window
   - `is_claimed` (Boolean, Default `False`)

---

## 4. In-Game Math & Physics Engines (`app/game_logic.py`)

### Stat Calculations (Gen 3 Mechanics)
Stats are dynamically re-calculated when leveling up or capturing a Pokémon:
- **Maximum HP (excluding Shedinja)**:
  $$\text{max\_hp} = \left\lfloor 0.01 \times (2 \times \text{BaseHP} + 31) \times \text{Level} \right\rfloor + \text{Level} + 10$$
- **Combat Stats (Attack, Defense, Special Attack, Special Defense, Speed)**:
  $$\text{Stat} = \left\lfloor 0.01 \times (2 \times \text{BaseStat} + 31) \times \text{Level} \right\rfloor + 5$$
*(Formula simplifies standard formulas by setting IVs to 31 and ignoring nature multipliers for uniform gameplay).*

### Experience Growth Math
The server supports the six main core experience formulas matching PokéAPI values:
- **Fast**:
  $$XP(L) = \left\lfloor \frac{4 \times L^3}{5} \right\rfloor$$
- **Medium-Fast**:
  $$XP(L) = L^3$$
- **Medium-Slow**:
  $$XP(L) = \frac{6}{5}L^3 - 15L^2 + 100L - 140$$
- **Slow**:
  $$XP(L) = \left\lfloor \frac{5 \times L^3}{4} \right\rfloor$$
- **Erratic & Fluctuating**: Piecewise curves determined by level bracket boundaries. Refer directly to code routines in `app/game_logic.py`.

---

## 5. API Routing Directory

All requests must specify appropriate headers. Paths protected with JWT require an `Authorization: Bearer <token>` header payload.

### Authentication Router (`/auth`)
- `POST /auth/register`: Create user account.
  - *Payload*: `{"username": "TrainerRed", "email": "red@pallet.org", "password": "secure_password"}`
  - *Response*: User detail structure. Generates initial items (3 Poke Balls, 5 Potions) and a randomized starter Pokémon at level 5.
- `POST /auth/token`: OAuth2 compatibility login route. Form URL-Encoded request context.
  - *Payload*: `username=TrainerRed&password=secure_password`
  - *Response*: `{"access_token": "JWT_TOKEN", "token_type": "bearer"}`

### Pokémon Library Router (`/pokemon`)
- `GET /pokemon/`: Return paginated directory lists. Query params: `skip` (int), `limit` (int).
- `GET /pokemon/{pokemon_id}`: Return structured stats, species evolution trees, abilities, and type relationships for a specific entry.

### Active Gameplay Router (`/game`)
- `GET /game/encounter`: Query wild encounter. Selects a random Gen 1 ID.
- `POST /game/catch`: Try to register capture. Checks if User owns Poke Balls, decrements inventory by 1, and inserts new user pokemon record with dynamic level 1 base calculations.
- `GET /game/my-pokemon`: Fetch entire user trainer box collection database.
- `GET /game/party`: Retrieve current active party (list of max 6 slot allocations).
- `POST /game/party/set`: Assign or remove Pokémon to active party slots. Checks for party cap of 6.
- `POST /game/pokemon/{user_pokemon_id}/xp`: Inject experience values. Handles multiple level up thresholds, stat adjustments, and database updates.
- `POST /game/breeding/start`: Initiate breeding daycare. Validates gender compatibility and egg group matching.
- `POST /game/breeding/claim/{session_id}`: Claims ready daycare egg, appending a level 1 offspring to box collection.

### Gardening Router (`/berries`)
- `GET /berries/`: Get item details for berry list.
- `GET /berries/plots`: Read the 4 farming plots. Auto-creates them if empty.
- `POST /berries/plant`: Plant a berry. Checks player inventory, decrements item, and initiates seedling stage.

---

## 6. Setup & Local Initialization

### Prerequisites
- **Python 3.10+**
- **Docker Engine** & **Docker Compose**
- **Postgres dev header dependencies** (e.g. `libpq-dev` on Debian/Ubuntu systems for pg_config support)

### Installation
1. Move to backend workspace:
   ```bash
   cd pokedex-backend
   ```
2. Copy configuration configuration block:
   ```bash
   cp .env.example .env
   ```
3. Initialize the development PostgreSQL instance via Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. Build Python Environment structures:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Execute the PokeAPI ETL seed script. This drops database schemas, creates fresh physical tables, and scrapes complete datasets:
   ```bash
   python seed_db.py
   ```
6. Start the API local uvicorn host:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
7. Verify table properties or diagnostics if needed:
   ```bash
   python inspect_db.py
   ```
