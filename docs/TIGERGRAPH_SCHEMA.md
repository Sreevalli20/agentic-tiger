# TigerGraph Schema Design

## Overview

This schema is designed for the TigerGraph Agentic GraphRAG Hackathon 2026, based on the official hackathon dataset containing 2,951 Olympic event documents from Wikipedia (1987-2023).

**Important Note**: The actual TigerGraph instance uses the graph name `Transaction_Fraud` as per hackathon requirements. The schema design below reflects the Olympic dataset structure, but the implementation will adapt to the existing Transaction_Fraud graph schema.

## Schema Goals

1. **Support Multi-hop Reasoning**: Enable complex queries that require traversing multiple entity types
2. **Enable Temporal Queries**: Support time-based questions about Olympic events
3. **Facilitate Aggregation**: Allow counting and filtering events by various criteria
4. **Link Documents to Entities**: Maintain traceability from answers to source documents
5. **Optimize for Performance**: Design efficient query patterns for common question types

## Vertex Types

### 1. Document
**Purpose**: Represents each Wikipedia article in the corpus

**Primary Key**: `doc_id` (STRING)

**Attributes**:
- `doc_id` (STRING) - Wikidata QID (e.g., "Q303623")
- `title` (STRING) - Full document title
- `url` (STRING) - Source Wikipedia URL
- `wikidata_qid` (STRING) - Wikidata identifier
- `wikipedia_pageid` (INT) - Wikipedia page ID
- `approx_tokens` (INT) - Estimated token count
- `text_snippet` (STRING) - First 500 characters for display

**Rationale**: Documents are the source of truth. All answers must be traceable to specific documents.

---

### 2. Event
**Purpose**: Represents Olympic competition events

**Primary Key**: `event_id` (STRING) - Format: `{sport}_{event_name}_{year}`

**Attributes**:
- `event_id` (STRING) - Unique identifier
- `name` (STRING) - Event name (e.g., "Men's K-2 1000 metres")
- `sport` (STRING) - Sport category (e.g., "Canoeing")
- `games` (STRING) - Olympic games (e.g., "2012 Summer")
- `year` (INT) - Year of Olympics
- `season` (STRING) - "Summer" or "Winter"
- `date` (STRING) - Event date(s)
- `venue` (STRING) - Competition venue
- `competitors` (INT) - Number of competitors
- `nations` (INT) - Number of participating nations
- `event_type` (STRING) - Competition format

**Rationale**: Events are central to most questions. This vertex type supports:
- Temporal queries (by year, games)
- Venue-based queries
- Competitor/nation aggregation
- Sport-specific queries

---

### 3. Athlete
**Purpose**: Represents Olympic athletes and medalists

**Primary Key**: `athlete_id` (STRING) - Format: `{name_normalized}`

**Attributes**:
- `athlete_id` (STRING) - Unique identifier
- `name` (STRING) - Full athlete name
- `noc` (STRING) - National Olympic Committee code
- `sport` (STRING) - Primary sport

**Rationale**: Athletes are the subject of many "who won" questions. This enables:
- Medalist lookups
- Nationality-based queries
- Multi-medalist identification

---

### 4. Nation
**Purpose**: Represents countries participating in Olympics

**Primary Key**: `noc` (STRING) - 3-letter NOC code

**Attributes**:
- `noc` (STRING) - NOC code (e.g., "USA", "HUN", "GER")
- `country_name` (STRING) - Full country name

**Rationale**: Nations are used for aggregation (e.g., "how many nations competed") and filtering.

---

### 5. Venue
**Purpose**: Represents Olympic competition venues

**Primary Key**: `venue_id` (STRING) - Format: `{venue_name_normalized}`

**Attributes**:
- `venue_id` (STRING) - Unique identifier
- `name` (STRING) - Venue name
- `location` (STRING) - City/region
- `type` (STRING) - Venue type (stadium, arena, etc.)

**Rationale**: Venues support location-based queries and multi-hop questions (venue → event → medalist).

---

### 6. Games
**Purpose**: Represents Olympic Games instances

**Primary Key**: `games_id` (STRING) - Format: `{year}_{season}`

**Attributes**:
- `games_id` (STRING) - Unique identifier
- `year` (INT) - Year
- `season` (STRING) - "Summer" or "Winter"
- `host_city` (STRING) - Host city
- `host_country` (STRING) - Host country

**Rationale**: Games vertex enables temporal reasoning and event aggregation by Olympic edition.

---

### 7. Sport
**Purpose**: Represents Olympic sports

**Primary Key**: `sport_id` (STRING) - Format: `{sport_name_normalized}`

**Attributes**:
- `sport_id` (STRING) - Unique identifier
- `name` (STRING) - Sport name
- `category` (STRING) - Sport category

**Rationale**: Sports enable category-based queries and event organization.

---

## Edge Types

### 1. DOCUMENT_ABOUT_EVENT
**Direction**: Document → Event

**Attributes**:
- `relevance_score` (FLOAT) - How relevant the document is to the event

**Purpose**: Links source documents to the events they describe. Critical for citation and traceability.

**Use Case**: "What document discusses the men's marathon in 2008?"

---

### 2. EVENT_PART_OF_GAMES
**Direction**: Event → Games

**Attributes**: None

**Purpose**: Links events to their Olympic Games edition.

**Use Case**: "How many events were in the 2012 Summer Olympics?"

---

### 3. EVENT_IN_SPORT
**Direction**: Event → Sport

**Attributes**: None

**Purpose**: Categorizes events by sport.

**Use Case**: "List all swimming events in 2016."

---

### 4. EVENT_HELD_AT_VENUE
**Direction**: Event → Venue

**Attributes**:
- `date` (STRING) - Event date at this venue

**Purpose**: Links events to their competition venues.

**Use Case**: "Who won gold at Olympic Tennis Centre on August 15, 2004?"

---

### 5. ATHLETE_WON_MEDAL_IN_EVENT
**Direction**: Athlete → Event

**Attributes**:
- `medal_type` (STRING) - "gold", "silver", or "bronze"
- `result` (STRING) - Performance result (time, score, etc.)

**Purpose**: Records medalists and their achievements.

**Use Case**: "Who won the gold medal in the men's 100m sprint?"

---

### 6. ATHLETE_REPRESENTS_NATION
**Direction**: Athlete → Nation

**Attributes**: None

**Purpose**: Links athletes to their countries.

**Use Case**: "Which athletes represented Hungary in 2012?"

---

### 7. NATION_PARTICIPATED_IN_GAMES
**Direction**: Nation → Games

**Attributes**:
- `athlete_count` (INT) - Number of athletes from this nation

**Purpose**: Tracks national participation in Olympic Games.

**Use Case**: "How many nations participated in the 2018 Winter Olympics?"

---

### 8. VENUE_LOCATED_IN_CITY
**Direction**: Venue → Games (via host city)

**Attributes**: None

**Purpose**: Links venues to the Olympic Games they hosted.

**Use Case**: "What venues were used in the 2008 Beijing Olympics?"

---

## Graph Creation Script (GSQL)

```sql
-- Create schema
CREATE VERTEX Document(PRIMARY_ID doc_id STRING, title STRING, url STRING, wikidata_qid STRING, wikipedia_pageid INT, approx_tokens INT, text_snippet STRING)
CREATE VERTEX Event(PRIMARY_ID event_id STRING, name STRING, sport STRING, games STRING, year INT, season STRING, date STRING, venue STRING, competitors INT, nations INT, event_type STRING)
CREATE VERTEX Athlete(PRIMARY_ID athlete_id STRING, name STRING, noc STRING, sport STRING)
CREATE VERTEX Nation(PRIMARY_ID noc STRING, country_name STRING)
CREATE VERTEX Venue(PRIMARY_ID venue_id STRING, name STRING, location STRING, type STRING)
CREATE VERTEX Games(PRIMARY_ID games_id STRING, year INT, season STRING, host_city STRING, host_country STRING)
CREATE VERTEX Sport(PRIMARY_ID sport_id STRING, name STRING, category STRING)

-- Create edges
CREATE DIRECTED EDGE DOCUMENT_ABOUT_EVENT(FROM Document, TO Event, relevance_score FLOAT)
CREATE DIRECTED EDGE EVENT_PART_OF_GAMES(FROM Event, TO Games)
CREATE DIRECTED EDGE EVENT_IN_SPORT(FROM Event, TO Sport)
CREATE DIRECTED EDGE EVENT_HELD_AT_VENUE(FROM Event, TO Venue, date STRING)
CREATE DIRECTED EDGE ATHLETE_WON_MEDAL_IN_EVENT(FROM Athlete, TO Event, medal_type STRING, result STRING)
CREATE DIRECTED EDGE ATHLETE_REPRESENTS_NATION(FROM Athlete, TO Nation)
CREATE DIRECTED EDGE NATION_PARTICIPATED_IN_GAMES(FROM Nation, TO Games, athlete_count INT)
CREATE DIRECTED EDGE VENUE_LOCATED_IN_CITY(FROM Venue, TO Games)

-- Create graph
-- Note: For the hackathon, the actual graph name is "Transaction_Fraud"
-- The schema below would need to be adapted to match the existing Transaction_Fraud graph structure
CREATE GRAPH graphrag_hackathon(Document, Event, Athlete, Nation, Venue, Games, Sport, DOCUMENT_ABOUT_EVENT, EVENT_PART_OF_GAMES, EVENT_IN_SPORT, EVENT_HELD_AT_VENUE, ATHLETE_WON_MEDAL_IN_EVENT, ATHLETE_REPRESENTS_NATION, NATION_PARTICIPATED_IN_GAMES, VENUE_LOCATED_IN_CITY)
```

## Example Multi-hop Reasoning Paths

### Path 1: Venue-based Multi-hop
**Question**: "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?"

**Path**: Venue → Event → Athlete

**Query Pattern**:
```sql
SELECT t1.name, t2.medal_type
FROM Venue:t1 - (EVENT_HELD_AT_VENUE) -> Event:t2 - (ATHLETE_WON_MEDAL_IN_EVENT) <- Athlete:t3
WHERE t1.name == "Olympic Tennis Centre" AND t2.date CONTAINS "2004" AND t2.medal_type == "gold"
```

---

### Path 2: Aggregation Path
**Question**: "How many biathlon events at the 2018 Winter Olympics had more than 73 competitors?"

**Path**: Games → Event (filter and count)

**Query Pattern**:
```sql
SELECT COUNT(t1)
FROM Games:t - (EVENT_PART_OF_GAMES) <- Event:t1
WHERE t.year == 2018 AND t.season == "Winter" AND t1.sport == "Biathlon" AND t1.competitors > 73
```

---

### Path 3: Temporal Path
**Question**: "Who won the gold medal in the men's 20 kilometres walk athletics event at the Summer Olympics held immediately before 2016?"

**Path**: Games (2012) → Event → Athlete

**Query Pattern**:
```sql
SELECT t3.name
FROM Games:t1 - (EVENT_PART_OF_GAMES) <- Event:t2 - (ATHLETE_WON_MEDAL_IN_EVENT) <- Athlete:t3
WHERE t1.year == 2012 AND t1.season == "Summer" AND t2.name CONTAINS "20 kilometres walk"
```

---

### Path 4: Superlative Path
**Question**: "Which athletics event at the 2008 Summer Olympics had the highest number of competitors?"

**Path**: Games → Event (find max)

**Query Pattern**:
```sql
SELECT t2.name, t2.competitors
FROM Games:t - (EVENT_PART_OF_GAMES) <- Event:t2
WHERE t.year == 2008 AND t.season == "Summer" AND t2.sport == "Athletics"
ORDER BY t2.competitors DESC
LIMIT 1
```

---

## Indexes for Performance

```sql
-- Indexes for common query patterns
CREATE INDEX ON Event(year)
CREATE INDEX ON Event(season)
CREATE INDEX ON Event(sport)
CREATE INDEX ON Event(competitors)
CREATE INDEX ON Games(year)
CREATE INDEX ON Games(season)
CREATE INDEX ON Athlete(noc)
CREATE INDEX ON Venue(name)
```

## Schema Validation

### Expected Vertex Counts (based on dataset analysis)
- **Document**: ~2,951 (one per corpus document)
- **Event**: ~2,951 (one per document, assuming one event per doc)
- **Athlete**: ~3,000-5,000 (estimated medalists)
- **Nation**: ~200 (all NOC codes)
- **Venue**: ~200-300 (unique venues)
- **Games**: ~20-30 (Olympic editions 1987-2023)
- **Sport**: ~30-50 (Olympic sports)

### Expected Edge Counts
- **DOCUMENT_ABOUT_EVENT**: ~2,951
- **EVENT_PART_OF_GAMES**: ~2,951
- **EVENT_IN_SPORT**: ~2,951
- **EVENT_HELD_AT_VENUE**: ~2,951
- **ATHLETE_WON_MEDAL_IN_EVENT**: ~6,000-9,000 (3 medalists per event)
- **ATHLETE_REPRESENTS_NATION**: ~3,000-5,000
- **NATION_PARTICIPATED_IN_GAMES**: ~4,000-6,000 (200 nations × 20-30 games)
- **VENUE_LOCATED_IN_CITY**: ~200-300

## Ingestion Strategy

### Phase 1: Document Loading
1. Load all 2,951 documents from `corpus.jsonl`
2. Create Document vertices
3. Extract event information from document text
4. Create Event vertices

### Phase 2: Entity Extraction
1. Parse infobox data from document text
2. Extract athlete names and NOC codes
3. Create Athlete vertices
4. Create Nation vertices (deduplicate by NOC)
5. Create Venue vertices
6. Create Games vertices
7. Create Sport vertices

### Phase 3: Relationship Creation
1. Link Document → Event
2. Link Event → Games, Sport, Venue
3. Link Athlete → Event (with medal type)
4. Link Athlete → Nation
5. Link Nation → Games
6. Link Venue → Games

### Phase 4: Validation
1. Verify vertex counts match expectations
2. Verify edge connectivity
3. Test sample queries against known gold answers
4. Validate multi-hop paths

## Query Optimization

### Common Query Patterns

1. **Direct Lookups**: Use primary key lookups for known entities
2. **Range Queries**: Use indexes on year, competitors for filtering
3. **Multi-hop**: Limit traversal depth to 2-3 hops for performance
4. **Aggregation**: Use TigerGraph's built-in aggregation functions

### Performance Considerations

- The graph is relatively small (< 10K vertices), so most queries should complete in < 100ms
- Multi-hop queries may require 2-3 edge traversals
- Aggregation queries benefit from indexes on numeric attributes
- Document retrieval should use direct vertex lookup by doc_id

## Schema Evolution

### Future Enhancements (Round 2+)
- Add temporal edges for event sequences
- Add performance result attributes for numerical comparisons
- Add discipline/category hierarchy for sports
- Add venue capacity and historical significance
- Add athlete career timeline edges

---

## Implementation Status

**Current Graph**: Transaction_Fraud (as per hackathon requirements)

**Implementation Notes**:
- The system is configured to connect to the `Transaction_Fraud` graph
- The graph service dynamically adapts to the existing schema of Transaction_Fraud
- If the Transaction_Fraud graph has a different schema than the Olympic-focused design above, the system will query whatever vertex and edge types are available
- The entity extraction and graph traversal components are designed to work with flexible schemas
- The health check verifies actual connectivity to the Transaction_Fraud graph

**Schema Adaptation Strategy**:
1. The graph service first queries the existing schema of Transaction_Fraud
2. Entity extraction uses heuristic-based methods that work with various graph structures
3. Graph traversal adapts to available vertex and edge types
4. The system logs the actual schema discovered for transparency

**Future Schema Alignment**:
- If the Transaction_Fraud graph needs to be populated with Olympic data, the schema design above provides a blueprint
- The ingestion pipeline in `backend/app/tigergraph/ingestion.py` implements the schema creation and data loading process
- The current implementation can work with either the existing Transaction_Fraud schema or a newly created Olympic-focused schema

## Summary

This schema is designed to:
1. ✅ Support all question types in the evaluation dataset (lookup, aggregation, temporal, superlative, multi-hop)
2. ✅ Enable efficient multi-hop reasoning through TigerGraph
3. ✅ Maintain traceability from answers to source documents
4. ✅ Support dynamic agent tool selection (entity linking, graph traversal)
5. ✅ Scale to the full corpus (2,951 documents)
6. ✅ Provide clear semantics for relationship-based queries
7. ✅ Adapt to existing Transaction_Fraud graph structure

The schema directly reflects the structure of the hackathon dataset and is optimized for the specific question patterns found in the evaluation set, while maintaining flexibility to work with the required Transaction_Fraud graph.
