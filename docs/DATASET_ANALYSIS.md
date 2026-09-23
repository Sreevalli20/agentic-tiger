# Dataset Analysis - TigerGraph Agentic GraphRAG Hackathon

## Dataset Location

The official hackathon resources were found at:
```
C:\Users\Sreevalli\Downloads\tiger\hackathon-resources
```

## Directory Structure

```
hackathon-resources/
├── README.md
├── corpus/
│   └── corpus.jsonl
└── questions/
    ├── eval_public.jsonl
    └── eval_hidden.jsonl
```

## Files Discovered

### 1. `corpus/corpus.jsonl`
- **Format**: JSONL (one JSON object per line)
- **Record Count**: 2,951 documents
- **Total Tokens**: ~5,471,565 tokens
- **Purpose**: Official corpus - the only source of truth for answers
- **Content**: English Wikipedia articles about Olympic events (1987-2023)

#### Document Schema
```json
{
  "doc_id": "Q303623",              // Wikidata QID (primary key)
  "title": "Canoeing at the 2012 Summer Olympics – Men's K-2 1000 metres",
  "url": "https://en.wikipedia.org/wiki/...",
  "wikidata_qid": "Q303623",       // Wikidata identifier
  "wikipedia_pageid": 35771859,    // Wikipedia page ID
  "approx_tokens": 704,           // Estimated token count
  "text": "Full document text in plain text format"
}
```

#### Document Structure Analysis
- Documents are English Wikipedia articles converted to plain text
- Coverage spans 1987-2023
- Subject matter is narrow (Olympic events)
- Documents contain structured infobox data (events, venues, dates, competitors, medalists)
- Text includes competition format, schedules, results tables, and background information
- Each document has a unique `doc_id` (Wikidata QID)
- Source URLs are provided for attribution

#### Key Entity Types Observed
- **Events**: Olympic competitions (e.g., "Men's K-2 1000 metres")
- **Athletes/Competitors**: Medalists and participants
- **Nations**: Countries represented by NOC codes
- **Venues**: Competition locations
- **Dates**: Event timing (Olympic years, specific dates)
- **Medals**: Gold, silver, bronze winners
- **Sports**: Athletics, swimming, cycling, etc.
- **Games**: Summer/Winter Olympics by year

### 2. `questions/eval_public.jsonl`
- **Format**: JSONL
- **Record Count**: 100 questions
- **Purpose**: Visible evaluation questions with gold answers
- **Access**: Public - can be used for benchmarking and testing

#### Question Schema
```json
{
  "qid": "pub-001",                    // Question ID
  "question": "According to the provided corpus, how many biathlon events at the 2018 Winter Olympics had more than 73 competitors?",
  "qtype": "aggregation",             // Question type
  "answer_named_in_question": false,  // Whether answer is in question text
  "guess_baseline": 0.0,              // Baseline guess rate
  "gold_doc_ids": ["Q47091419", ...],  // Relevant document IDs
  "answer_verified": true,            // Answer verification status
  "answer": ["5"]                     // Gold answer(s)
}
```

#### Question Types Observed
- **aggregation**: Count-based questions requiring aggregation across documents
- **temporal**: Time-based questions requiring temporal reasoning
- **superlative**: Questions requiring finding maximum/minimum values
- **multi_hop**: Complex questions requiring multiple reasoning steps
- **lookup**: Simple fact retrieval questions

#### Public Evaluation Characteristics
- 100 questions with verified gold answers
- Gold document IDs provided for each question
- Questions cover multiple Olympic sports and time periods
- Requires both retrieval and reasoning capabilities
- Suitable for benchmarking and comparison

### 3. `questions/eval_hidden.jsonl`
- **Format**: JSONL
- **Record Count**: 50 questions
- **Purpose**: Hidden evaluation questions without answers
- **Access**: **PRIVATE** - for final hackathon evaluation only

#### Hidden Question Schema
```json
{
  "qid": "eval-001",
  "question": "Who won the gold medal in the event held at Olympic Tennis Centre on 15 to 22 August 2004?",
  "qtype": "multi_hop"
}
```

#### Hidden Evaluation Characteristics
- 50 questions WITHOUT gold answers
- Used for final hackathon scoring
- Must remain private - never expose in frontend, API, or documentation
- Same question types as public set
- Evaluation workflow must be private

## Corpus Content Analysis

### Document Themes
The corpus focuses on Olympic events with rich structured data:
- Competition results and medalists
- Venues and locations
- Dates and schedules
- Competitor counts and nation participation
- Competition formats and rules
- Historical context and background

### Data Quality Observations
- Documents are well-structured with consistent schema
- Infobox data provides structured entities and relationships
- Text is clean (Wikipedia plain text conversion)
- Source URLs enable verification
- Token counts vary widely (hundreds to thousands per document)
- Some documents have truncated results tables (original Wikipedia limitation)

## Graph Modeling Strategy

### Potential Vertex Types
Based on corpus analysis:

1. **Document** (Vertex)
   - Primary key: `doc_id` (QID)
   - Attributes: title, url, approx_tokens, text snippet

2. **Event** (Vertex)
   - Primary key: event name + games year
   - Attributes: event type, date, venue, competitors count

3. **Athlete** (Vertex)
   - Primary key: athlete name
   - Attributes: nationality (NOC), sport

4. **Nation** (Vertex)
   - Primary key: NOC code
   - Attributes: country name

5. **Venue** (Vertex)
   - Primary key: venue name
   - Attributes: location, type

6. **Games** (Vertex)
   - Primary key: year + season (e.g., "2012 Summer")
   - Attributes: host city, dates

7. **Sport** (Vertex)
   - Primary key: sport name
   - Attributes: category

### Potential Edge Types
Based on corpus relationships:

1. **DOCUMENT_CONTAINS_EVENT** (Document → Event)
2. **EVENT_PART_OF_GAMES** (Event → Games)
3. **EVENT_HELD_AT_VENUE** (Event → Venue)
4. **EVENT_IN_SPORT** (Event → Sport)
5. **ATHLETE_WON_MEDAL_IN_EVENT** (Athlete → Event)
6. **ATHLETE_REPRESENTS_NATION** (Athlete → Nation)
7. **NATION_PARTICIPATED_IN_GAMES** (Nation → Games)
8. **VENUE_LOCATED_IN_CITY** (Venue → Location)

### Multi-hop Reasoning Paths
Example paths needed for questions:
- "Who won gold in event at venue on date?" → Venue → Event → Athlete
- "How many events at games had > X competitors?" → Games → Event (filter by competitors)
- "Which event had most competitors?" → All Events (find max competitors)

## Ingestion Strategy

### Phase 1: Document Parsing
- Read `corpus.jsonl` line by line
- Extract structured infobox data using regex/parsing
- Identify entities (athletes, nations, venues, events)
- Validate document completeness

### Phase 2: Entity Extraction
- Parse infobox structured data
- Extract: event names, athlete names, NOC codes, venues, dates
- Handle multi-athlete fields (e.g., "Rudolf DombiRoland Kökény")
- Normalize names and codes

### Phase 3: Relationship Building
- Link documents to events they describe
- Link events to games/venues/sports
- Link athletes to events and nations
- Build temporal relationships (dates, games years)

### Phase 4: TigerGraph Loading
- Create schema with identified vertex/edge types
- Load vertices (deduplicate by primary key)
- Load edges (ensure referential integrity)
- Validate counts match expected

### Phase 5: Verification
- Count vertices loaded vs documents processed
- Verify edge connectivity
- Test sample queries
- Validate against known gold answers

## Data Quality Issues

### Identified Issues
1. **Name Concatenation**: Some athlete names are concatenated without spaces (e.g., "Rudolf DombiRoland Kökény")
2. **Truncated Tables**: Some results tables are truncated in original Wikipedia
3. **Inconsistent Formatting**: Date formats vary across documents
4. **Missing Fields**: Some documents may lack certain infobox fields

### Mitigation Strategies
- Implement fuzzy name matching for athlete identification
- Use doc_id as canonical identifier for documents
- Normalize date formats during parsing
- Handle missing fields gracefully (optional vertices/edges)

## Privacy Requirements

### Hidden Evaluation Data
- `eval_hidden.jsonl` contains 50 private questions
- **NEVER** expose in:
  - Frontend code or UI
  - API responses
  - README or documentation
  - Public benchmark files
  - GitHub repository
  - Committed logs
- Create private evaluation workflow if needed
- Store results separately from public benchmark results

### Public Evaluation Data
- `eval_public.jsonl` can be used for:
  - Benchmarking and testing
  - Documentation examples
  - API demonstration
  - Metrics dashboard

## Graph Schema Recommendations

### Minimum Viable Schema (MVP)
For hackathon submission, focus on:

**Vertices:**
- Document (doc_id, title, url, text)
- Event (event_id, name, games, venue, date, competitors)
- Athlete (athlete_id, name, noc)
- Nation (noc, country_name)
- Venue (venue_id, name, location)

**Edges:**
- DOCUMENT_ABOUT_EVENT (Document → Event)
- EVENT_HAS_MEDALIST (Event → Athlete, with medal type)
- ATHLETE_FROM_NATION (Athlete → Nation)
- EVENT_AT_VENUE (Event → Venue)
- EVENT_IN_GAMES (Event → Games)

This schema supports:
- Multi-hop questions (venue → event → athlete)
- Aggregation questions (count events by criteria)
- Temporal questions (games → events → dates)
- Lookup questions (direct entity retrieval)

## Implementation Status

**Dataset discovered and analyzed**: ✅ Complete
- Location: `C:\Users\Sreevalli\Downloads\tiger\hackathon-resources`
- Corpus: 2,951 documents (23MB JSONL)
- Public questions: 100 with gold answers
- Hidden questions: 50 private (for final evaluation)
- Schema documented and ingestion strategy defined

**Note**: The actual TigerGraph graph name is `Transaction_Fraud` (as per hackathon requirements), not `graphrag_hackathon`. The environment configuration must be updated to use `TG_GRAPHNAME=Transaction_Fraud`.
