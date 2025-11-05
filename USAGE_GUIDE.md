# How to Use the Senzing MCP Server

Once the MCP server is connected to your AI assistant (Claude Desktop, etc.), you can use natural language to interact with Senzing. Here are examples of what to say:

## 🔍 Search for Entities

**What to say:**
```
Search for entities with the name "John Smith"
```

```
Find people named "Jane Doe" with phone number "555-1234"
```

```
Search for entities with email "john@example.com" and address "123 Main St"
```

**Available search attributes:**
- `NAME_FULL` - Full name
- `NAME_FIRST` - First name
- `NAME_LAST` - Last name
- `ADDR_FULL` - Full address
- `PHONE_NUMBER` - Phone number
- `EMAIL_ADDRESS` - Email address
- `DATE_OF_BIRTH` - Date of birth (YYYY-MM-DD)

---

## 📄 Get Entity Details

**What to say:**
```
Get details for entity ID 100
```

```
Show me information about entity 42
```

```
What records are in entity 1000?
```

---

## ➕ Add Records

### Single Record

**What to say:**
```
Add a record to the CUSTOMERS data source with ID "CUST-001", name "John Smith",
and phone "555-1234"
```

```
Create a new record in TEST_DATA with ID "REC-123", email "jane@example.com",
and address "456 Oak Ave"
```

### Bulk Import from File

**What to say:**
```
Import records from /path/to/customers.jsonl into the CUSTOMERS data source
```

```
Load all records from /data/people.jsonl into PEOPLE_SOURCE using 10 workers
```

**File format (JSONL - one JSON per line):**
```jsonl
{"RECORD_ID": "001", "NAME_FULL": "John Smith", "PHONE_NUMBER": "555-1234"}
{"RECORD_ID": "002", "NAME_FULL": "Jane Doe", "EMAIL_ADDRESS": "jane@example.com"}
```

---

## 🗑️ Delete Records

**What to say:**
```
Delete record "CUST-001" from the CUSTOMERS data source
```

```
Remove record ID "REC-123" from TEST_DATA
```

---

## 🔗 Relationship Analysis

### Find Path Between Entities

**What to say:**
```
Find the relationship path between entity 100 and entity 200
```

```
How are entity 50 and entity 75 connected? Search up to 4 degrees
```

```
Show me the connection between entities 10 and 20
```

### Find Network

**What to say:**
```
Find the network around entities 100, 200, and 300
```

```
Show me all entities connected to entity 50 within 2 degrees
```

```
Analyze the network for entities [10, 20, 30] with max 100 entities
```

### Explain Relationships

**What to say:**
```
Why are entities 100 and 200 related?
```

```
Explain the relationship between entity 50 and entity 75
```

```
What attributes match between entities 10 and 20?
```

### Explain Entity Resolution

**What to say:**
```
How was entity 100 resolved?
```

```
Explain the resolution for entity 42
```

```
Show me why the records in entity 1000 were grouped together
```

---

## 📊 Statistics and Configuration

### Get Stats

**What to say:**
```
Show me Senzing statistics
```

```
Get engine stats
```

```
How many entities and records are in the system?
```

### Get Configuration Info

**What to say:**
```
What's the current Senzing configuration?
```

```
Show me the active config version
```

```
Get Senzing product version
```

---

## 💡 Real-World Examples

### Customer Deduplication
```
Search for customers named "Robert Johnson" with phone "555-0100"

[If multiple entities found]
Why are entities 150 and 151 related?
Explain how entity 150 was resolved
```

### Fraud Investigation
```
Find the network around entity 500 within 3 degrees with max 50 entities

[Analyze results]
Find the path between entity 500 and entity 520
Why are these two entities connected?
```

### Data Quality Check
```
Get Senzing statistics

[Check counts]
Search for entities with email "test@example.com"
Get details for entity 999
```

### Bulk Data Loading
```
Import records from /data/new_customers.jsonl into CUSTOMERS using 8 workers

[Monitor progress, then verify]
Show me Senzing statistics
Search for entities with name "Test Customer"
```

---

## 🎯 Tips for Best Results

1. **Be specific**: Include data source codes, entity IDs, and record IDs exactly as they appear
2. **Use natural language**: The AI understands intent - you don't need exact syntax
3. **Combine queries**: Ask follow-up questions to drill down into results
4. **Check before bulk operations**: Search first, then add/delete in bulk

---

## 🛠️ Available Tools (Technical Reference)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_entities` | Search by attributes | attributes (name, phone, email, etc.) |
| `get_entity` | Get entity details | entity_id |
| `add_record` | Add single record | data_source_code, record_id, record_data |
| `add_records_from_file` | Bulk import | file_path, data_source_code, max_workers |
| `delete_record` | Delete record | data_source_code, record_id |
| `find_relationship_path` | Find path | start_entity_id, end_entity_id, max_degrees |
| `find_network` | Find network | entity_ids, max_degrees, max_entities |
| `explain_relationship` | Explain why related | entity_id_1, entity_id_2 |
| `explain_entity_resolution` | Explain resolution | entity_id |
| `get_stats` | Get statistics | (none) |
| `get_config_info` | Get configuration | (none) |

---

## 🚀 Quick Start Conversation

Try this conversation flow:

**You:** "Show me Senzing statistics"

**You:** "Search for entities named 'John Smith'"

**You:** "Get details for entity 1" *(use actual entity ID from search results)*

**You:** "Find the network around entity 1 within 2 degrees"

**You:** "How was entity 1 resolved?"

---

## ❓ Common Questions

**Q: What if I don't know the entity ID?**
A: Search first using attributes (name, phone, etc.), then use the entity IDs from the results

**Q: Can I search with partial matches?**
A: Yes, Senzing's fuzzy matching handles typos, abbreviations, and variations

**Q: What format for bulk import files?**
A: JSONL (JSON Lines) - one JSON object per line with RECORD_ID and entity attributes

**Q: How do I know what data sources exist?**
A: That's configured in your Senzing system - check with your admin or search existing records
