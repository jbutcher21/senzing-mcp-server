# Response Formatting Guide for Senzing MCP Server

This guide provides instructions for AI assistants on how to interpret and present results from the Senzing MCP Server's HOW and WHY explanation tools.

## Overview

The Senzing MCP Server provides two key explanation tools:
- **`explain_entity_resolution`** - Returns HOW trace data showing how records were resolved into an entity
- **`explain_relationship`** - Returns WHY trace data showing why two entities are related or not

These tools return raw JSON from the Senzing SDK. This guide explains how to interpret and present that data to users in a clear, professional manner.

## Reference Documentation

For background on HOW and WHY outputs, refer to:
- [Senzing EDA Basic Exploration Guide](https://www.senzing.com/docs/tutorials/eda/eda_basic_exploration/)
- See sections: "Using How" and "Using Why"

---

## Interpreting HOW Results (`explain_entity_resolution`)

### Purpose
Shows the step-by-step process of how source records were merged together to form a resolved entity.

### Presentation Format

**1. Start with a Clear Summary**

Begin with a high-level overview that explains:
- Which records (data source + record ID) were resolved into the entity
- How many merge steps occurred in the resolution process
- The overall drivers of resolution (e.g., email match, phone match, DOB match)
- Any conflicts that were overridden during resolution

**2. Show Step-by-Step Breakdown**

After the summary, present each resolution step:

**Step Header Verb Rules:**
- If both sides are single records → use **"with"**
  - Example: "Step 1: Merged CUSTOMERS:1001 **with** CUSTOMERS:1002"
- If one side is a single record and the other is a group → use **"into"**
  - Example: "Step 2: Merged CUSTOMERS:1003 **into** existing entity"
- If both sides are groups → use **"with"**
  - Example: "Step 3: Merged entity group **with** another entity group"

**Group Notation:**
- For groups, show as `CUSTOMERS:1002 +n more` instead of listing every record ID
- Example: "CUSTOMERS:1002 +3 more" means record 1002 plus 3 other CUSTOMERS records

**For Each Step:**
- Show the compared features (from `match_key_details` only) with scores
- Highlight **confirming features** with ✅
- Highlight **denying features** with ❌
- Do NOT repeat "Outcome" inside each step (it's clear from the step header)

**3. End with Bottom Line**

Close with: **➡️ Bottom line:** [concise final decision statement]

### Example Format

```
## Summary
Entity 1234 was resolved from 4 CUSTOMERS records through 3 merge steps.
Primary match drivers: Email address and phone number matches.
No conflicts encountered.

## Resolution Steps

**Step 1: Merged CUSTOMERS:1001 with CUSTOMERS:1002**
- ✅ EMAIL: user@example.com (Score: 95)
- ✅ PHONE: +1-555-0100 (Score: 90)
- Match Key: EMAIL+PHONE

**Step 2: Merged CUSTOMERS:1003 into existing entity (CUSTOMERS:1001 +1 more)**
- ✅ NAME: John Smith (Score: 85)
- ✅ DOB: 1980-01-15 (Score: 100)
- Match Key: NAME+DOB

**Step 3: Merged CUSTOMERS:1004 into existing entity (CUSTOMERS:1001 +2 more)**
- ✅ ADDRESS: 123 Main St (Score: 80)
- Match Key: ADDRESS

➡️ **Bottom line**: 4 records successfully merged based on strong email, phone, name, and address matches with no conflicts.
```

---

## Interpreting WHY Results (`explain_relationship`)

### Purpose
Shows why two entities are or are not related, including matching features and conflicts.

### Presentation Format

**1. Start with a Clear Summary**

Begin with a high-level overview:
- **Confirmations**: ✅ features that matched between entities
- **Denials**: ❌ features that conflicted
- **Match Key** used for comparison
- **➡️ Bottom line**: [final decision statement]

**2. Show Side-by-Side Comparison Table**

Present entities in a comparison table with these columns:
- **Feature** | **Entity 1** | **Entity 2** | **Result**

**Important table rules:**
- Always include `DATA_SOURCE` row with record counts
  - Example: "CUSTOMERS:4, WATCHLIST:1" means 4 CUSTOMERS records + 1 WATCHLIST record
- For features with multiple values, separate them with commas
- Only highlight features from `match_key_details` with ✅ or ❌
- Do NOT show `ERRULE_CODE` or attempt to explain it

**3. Keep Tone Concise and Professional**

Write in a clear, documentation-appropriate style suitable for technical users.

### Example Format

```
## Summary

**Comparison: Entity 1001 vs Entity 1002**

✅ **Confirmations:**
- EMAIL: Both have user@example.com
- PHONE: Both have +1-555-0100

❌ **Denials:**
- NAME: Different spellings (John Smith vs Jon Smith)

**Match Key:** EMAIL+PHONE
**➡️ Bottom line:** Entities match on strong identifiers (email and phone) despite minor name variation. Likely the same person.

## Feature Comparison

| Feature      | Entity 1001           | Entity 1002           | Result |
|--------------|----------------------|----------------------|--------|
| DATA_SOURCE  | CUSTOMERS:3          | CUSTOMERS:2          | -      |
| NAME         | John Smith           | Jon Smith            | ❌     |
| EMAIL        | user@example.com     | user@example.com     | ✅     |
| PHONE        | +1-555-0100          | +1-555-0100          | ✅     |
| ADDRESS      | 123 Main St          | 456 Oak Ave          | -      |
```

---

## Interpreting SEARCH Results (`search_entities`)

### Purpose
Returns entities that match the search criteria, ranked by match score.

### Presentation Format

**1. Start with Search Summary**

Begin with a high-level overview:
- Number of entities found
- Search criteria used
- Score range (if applicable)

**2. Present Results in a Clear Table**

Use a table format with these columns:
- **Entity ID** - The entity identifier
- **Name** - Entity's resolved name
- **Match Score** - Percentage or score indicating match strength
- **Data Sources** - Which sources contributed records (e.g., CUSTOMERS:2, WATCHLIST:1)
- **Key Attributes** - Most relevant matching attributes

**For each entity:**
- Show the most important identifying information
- Highlight match scores prominently
- Group by score ranges if many results (e.g., "Strong Matches (90-100%)", "Good Matches (70-89%)")

**3. Provide Context**

After the table, explain:
- What the scores mean
- Why certain entities scored higher
- Any notable patterns in the results

### Example Format

```
## Search Results: "John Smith"

Found 8 entities matching search criteria.
Score range: 62% - 95%

### Strong Matches (90-100%)

| Entity ID | Name        | Score | Data Sources     | Key Matches                    |
|-----------|-------------|-------|------------------|--------------------------------|
| 1001      | John Smith  | 95%   | CUSTOMERS:3      | Name, DOB (1980-01-15), Phone  |
| 1005      | John Smith  | 92%   | CUSTOMERS:1, HR:1| Name, Email, Address           |

### Good Matches (70-89%)

| Entity ID | Name         | Score | Data Sources  | Key Matches           |
|-----------|--------------|-------|---------------|-----------------------|
| 1008      | Jon Smith    | 85%   | CUSTOMERS:2   | Name (variant), Phone |
| 1012      | John Smyth   | 78%   | WATCHLIST:1   | Name (variant), DOB   |

**Analysis:**
- Top matches have exact name and multiple attribute matches
- Lower scored entities show name variations or fewer matching attributes
- Entity 1001 has the most supporting data (3 source records)
```

---

## Interpreting ENTITY Details (`get_entity`)

### Purpose
Returns comprehensive information about a single entity, including all source records, features, and relationships.

### Presentation Format

**1. Entity Overview Section**

Start with key information:
- Entity ID
- Resolved name
- Number of source records and data sources
- Last activity/update date (if relevant)

**2. Source Records Section**

Show which records were resolved into this entity:

```
## Source Records (4 records from 2 data sources)

**CUSTOMERS**
- Record 1001: John Smith, DOB: 1980-01-15
- Record 1002: John A. Smith, Added: 2023-05-12
- Record 1003: J. Smith, Email: john@example.com

**HR**
- Record HR-5432: John Smith, Emp ID: E12345
```

**3. Resolved Features Section**

Show the entity's resolved/deduplicated attributes in a clear list:

```
## Resolved Features

**Names:**
- Primary: John Smith
- Also known as: John A. Smith, J. Smith

**Contact Information:**
- Email: john@example.com
- Phone: +1-555-0100, +1-555-0199
- Address: 123 Main St, Springfield, IL 62701

**Identifiers:**
- Date of Birth: 1980-01-15
- Employee ID: E12345
```

**4. Relationships Section (if present)**

Show related entities clearly:

```
## Related Entities

**Possibly Related (2 entities)**
- Entity 1205: Jane Smith - Shared address
- Entity 1844: John Smith Jr. - Name similarity, different DOB

**Possibly Same (1 entity)**
- Entity 988: J.A. Smith - High feature overlap, awaiting additional data
```

**5. Keep It Organized**

- Use collapsible sections for very detailed data
- Prioritize most important information at the top
- Group similar features together
- Use icons or indicators for feature confidence levels

### Example Format

```
## Entity 1001: John Smith

**Overview:**
- 4 source records from 2 data sources (CUSTOMERS, HR)
- Last updated: 2024-01-15
- Resolution confidence: High

## Source Records

**CUSTOMERS (3 records)**
- 1001: Added 2022-03-10 - Name, DOB, Phone
- 1002: Added 2023-05-12 - Name, Email, Address
- 1003: Added 2023-11-20 - Name variant, Phone

**HR (1 record)**
- HR-5432: Added 2022-06-01 - Name, Employee ID, DOB

## Resolved Features

**Identity:**
- Name: John Smith (also: John A. Smith, J. Smith)
- DOB: 1980-01-15
- SSN: [Last 4: 1234]

**Contact:**
- Email: john@example.com
- Phone: +1-555-0100 (primary), +1-555-0199
- Address: 123 Main St, Springfield, IL 62701

**Employment:**
- Employee ID: E12345
- Department: Engineering

## Related Entities

**Possibly Related:**
- Entity 1205: Jane Smith - Shared home address, possibly spouse
```

---

## Interpreting RELATIONSHIP PATHS (`find_relationship_path`)

### Purpose
Shows how two entities are connected through intermediate entities and shared attributes.

### Presentation Format

**1. Path Summary**

Begin with overview:
- Number of degrees of separation
- Total entities in path
- Primary connection types (e.g., shared address, shared phone)

**2. Visualize the Path**

Show the path clearly with arrows and connection reasons:

```
Entity 1001 (John Smith)
    ↓
    [Shared Phone: +1-555-0100]
    ↓
Entity 1205 (Jane Smith)
    ↓
    [Shared Address: 123 Main St]
    ↓
Entity 2033 (Robert Johnson)
```

**Alternative table format for complex paths:**

| From Entity | Connection Type | To Entity |
|-------------|-----------------|-----------|
| 1001: John Smith | Shared Phone: +1-555-0100 | 1205: Jane Smith |
| 1205: Jane Smith | Shared Address: 123 Main St | 2033: Robert Johnson |

**3. Provide Context**

Explain what the path means:
- Relationship strength/confidence
- Whether this is a direct or indirect connection
- Notable patterns or concerns (e.g., fraud risk indicators)

### Example Format

```
## Relationship Path: Entity 1001 → Entity 2033

**Path Summary:**
- 2 degrees of separation (connected through 1 intermediate entity)
- Connection types: Phone sharing, Address sharing

## Path Visualization

**Entity 1001: John Smith**
- Data Sources: CUSTOMERS:3, HR:1
- Key Info: +1-555-0100, john@example.com

    ↓ [Shared Phone: +1-555-0100]

**Entity 1205: Jane Smith** (Intermediate)
- Data Sources: CUSTOMERS:2
- Key Info: 123 Main St, Springfield

    ↓ [Shared Address: 123 Main St, Springfield]

**Entity 2033: Robert Johnson**
- Data Sources: WATCHLIST:1
- Key Info: 456 Oak Ave (previous), 123 Main St (current)

**Analysis:**
- Entity 1001 and 1205 share a phone number (likely same household)
- Entity 1205 and 2033 share an address (current/previous residents or household members)
- This suggests Entity 1001 and 2033 may be in the same social/household network
```

---

## Interpreting NETWORK Results (`find_network`)

### Purpose
Shows a network of related entities, useful for analyzing connection clusters and identifying entity groups.

### Presentation Format

**1. Network Summary**

Begin with overview:
- Number of entities in network
- Number of relationships
- Degrees of separation explored
- Key clusters or groups identified

**2. Organize by Connection Strength**

Group entities by how they're connected:

```
## Core Entities (Starting Points)
- Entity 1001: John Smith (CUSTOMERS:3)
- Entity 1205: Jane Smith (CUSTOMERS:2)

## Direct Connections (1 degree)
- Entity 2033: Robert Johnson - Shared address with 1205
- Entity 3421: Mary Smith - Shared phone with 1001
- Entity 4102: Global Corp - Employer relationship with 1001

## Secondary Connections (2 degrees)
- Entity 5201: Alice Brown - Shared employer with 1001 (via 4102)
- Entity 6340: Tom Wilson - Shared address with 2033
```

**3. Visualize Key Relationships**

For complex networks, show a simplified diagram or table:

| Entity | Connections | Relationship Types |
|--------|-------------|-------------------|
| 1001: John Smith | 3 direct | Phone, Employer, Name |
| 1205: Jane Smith | 2 direct, 1 indirect | Phone, Address |
| 2033: Robert Johnson | 1 direct | Address |

**4. Highlight Clusters**

Identify meaningful groups:

```
## Identified Clusters

**Household Cluster (3 entities)**
- 1001: John Smith
- 1205: Jane Smith
- 3421: Mary Smith
- Common: Shared phone and address, likely family unit

**Business Cluster (2 entities)**
- 1001: John Smith
- 5201: Alice Brown
- Common: Same employer (Global Corp)
```

### Example Format

```
## Network Analysis: Starting from Entity 1001

**Network Summary:**
- 7 entities in network
- 9 relationships identified
- 2 degrees of separation explored
- 2 distinct clusters identified

## Core Entity

**Entity 1001: John Smith**
- Data Sources: CUSTOMERS:3, HR:1
- Direct Connections: 3

## Network Map

### 1-Degree Connections (Direct)

**Entity 1205: Jane Smith**
- Connection: Shared phone +1-555-0100
- Relationship: Likely household member/spouse
- Data Sources: CUSTOMERS:2

**Entity 3421: Mary Smith**
- Connection: Shared address, name similarity
- Relationship: Likely family member
- Data Sources: CUSTOMERS:1

**Entity 4102: Global Corp**
- Connection: Employer relationship
- Relationship: Employment
- Data Sources: HR:1

### 2-Degree Connections (Indirect)

**Entity 5201: Alice Brown**
- Connection: Through Entity 4102 (Global Corp)
- Relationship: Co-worker
- Data Sources: HR:1

**Entity 2033: Robert Johnson**
- Connection: Through Entity 1205 (shared address)
- Relationship: Neighbor or previous resident
- Data Sources: WATCHLIST:1, CUSTOMERS:1

## Key Findings

**Household Cluster:**
Entities 1001, 1205, and 3421 appear to form a household unit with shared phone and address.

**Employment Network:**
Entities 1001 and 5201 work for the same employer (Entity 4102: Global Corp).

**Note:**
Entity 2033 appears in WATCHLIST data source and has indirect connection through household members - may warrant additional review.
```

---

## General Guidelines

### Do's
- ✅ Use clear section headers
- ✅ Highlight matching (✅) and conflicting (❌) features
- ✅ Show data sources with record counts
- ✅ Provide a bottom-line summary
- ✅ Use tables for comparisons
- ✅ Reference only features from `match_key_details`

### Don'ts
- ❌ Don't show internal codes like `ERRULE_CODE`
- ❌ Don't list every record ID in large groups
- ❌ Don't repeat "Outcome" redundantly in step descriptions
- ❌ Don't use overly technical jargon
- ❌ Don't include features that weren't part of the match process

---

## For AI Assistants Using This MCP Server

When responding to user queries, call the appropriate tool and format results accordingly:

### Tool Selection Guide

- **`search_entities`** - For "find entities matching..." or "search for..." queries
- **`get_entity`** - For "tell me about entity X" or "show details for..." queries
- **`find_relationship_path`** - For "how are entity X and Y connected?" queries
- **`find_network`** - For "show me the network around entity X" queries
- **`explain_entity_resolution`** - For "how was entity X resolved?" (HOW analysis)
- **`explain_relationship`** - For "why are entities X and Y related?" (WHY analysis)

### Formatting Steps

1. **Call the appropriate tool** based on the user's question
2. **Parse the JSON response** from the MCP server
3. **Format the output** following the templates in this guide
4. **Provide context** - explain what the results mean in plain language
5. **Be concise** - users want insights, not raw data dumps
6. **Use visual elements** - tables, arrows, section headers, and emojis (✅/❌) for clarity

---

## Notes

- This formatting guide is for **presentation only** - it does not modify the MCP server's behavior
- The MCP server returns raw Senzing SDK JSON - interpretation happens client-side
- These guidelines ensure consistency across different AI assistants using this server
