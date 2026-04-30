This code builds an **AI-powered medical appointment booking chatbot** using:

* **LangGraph** → manages the conversation workflow as a graph/state machine
* **Groq LLM** → understands user intent and extracts information
* **Interrupts** → pauses the workflow and waits for user input
* **State management** → stores booking progress
* **Guardrails** → prevents off-topic conversations
* **Email + DB integration** → confirms appointments

---

# 1. IMPORTS

```python
import os
from typing import TypedDict, Annotated, List, Optional
from datetime import datetime
import re
```

These are standard Python libraries.

* `TypedDict` → defines structured state object
* `Optional` → value can be None
* `datetime` → handles appointment dates

---

## LangGraph Imports

```python
from langgraph.graph import StateGraph, END
```

Used to create the workflow graph.

Example:

```text
Greeting
   ↓
Select Specialty
   ↓
Select Doctor
   ↓
Select Date
   ↓
Select Slot
   ↓
Confirm
   ↓
Completed
```

---

## LLM Imports

```python
from groq import Groq
```

This connects to Groq LLM API.

---

## Memory & Interrupts

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
```

### `interrupt()`

Pauses the graph and waits for user input.

Example:

```python
user_input = interrupt("Choose a doctor")
```

Execution pauses until the user responds.

---

# 2. INITIALIZE LLM

```python
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

Creates Groq client.

---

# 3. BOOKING STATE

```python
class BookingState(TypedDict):
```

This is the chatbot memory.

It stores:

```python
{
    "stage": "select_slot",
    "selected_doctor": {...},
    "selected_date": "2026-04-20",
    "selected_slot": "10:00 AM"
}
```

---

## Important Fields

### messages

```python
messages: List[dict]
```

Chat history.

Example:

```python
[
  {"role":"user","content":"I need a cardiologist"},
  {"role":"assistant","content":"Choose a doctor"}
]
```

---

### stage

Tracks current step.

```python
stage: str
```

Possible values:

* greeting
* select_speciality
* select_doctor
* select_date
* select_slot
* confirm
* completed

---

# 4. INITIAL STATE

```python
def create_initial_state():
```

Creates empty conversation state.

---

# 5. call_llm()

```python
def call_llm(...)
```

Central helper function for all LLM calls.

---

## What it does

Sends prompts to Groq:

```python
response = client.chat.completions.create(
```

---

## Example

```python
call_llm(
   system_prompt="You extract dates",
   user_prompt="tomorrow evening"
)
```

---

# 6. TOPIC GUARDRAIL

```python
def is_message_on_topic(...)
```

Prevents unrelated conversations.

---

## Example

Allowed:

```text
"I need a neurologist"
```

Blocked:

```text
"Who won the football match?"
```

---

## How?

LLM classifies:

```text
yes → medical related
no → unrelated
```

---

# 7. ROUTER FUNCTION

```python
def llm_router(state)
```

This is the brain of routing.

It decides:

```text
Where should conversation go next?
```

---

## Example

If user says:

```text
"I want a cardiologist"
```

Router returns:

```python
"select_doctor"
```

---

# 8. STATE-BASED BYPASS

```python
if current_stage == "select_speciality" and state.get("selected_speciality"):
```

Optimization.

If specialty already selected:

```text
Skip asking again
```

---

# 9. ROUTING PROMPTS

Each stage has its own routing logic.

Example:

```python
"confirm": """
Did user confirm?
"""
```

LLM returns:

```text
collect_details
```

or

```text
cancelled
```

---

# 10. NODES

Each node = one conversation step.

---

# greeting_node()

```python
def greeting_node(state)
```

Greets user.

---

## interrupt()

```python
user_input = interrupt(...)
```

Pauses workflow.

---

# select_speciality_node()

Shows medical specialties.

---

## Example

```text
Cardiology
Neurology
Orthopedics
```

---

## LLM Extraction

User may type:

```text
"I need heart doctor"
```

LLM converts to:

```text
Cardiology
```

---

# select_doctor_node()

Gets doctor info.

```python
doctor = get_doctor_info(speciality)
```

---

# select_date_node()

Handles appointment date.

---

## Example

User:

```text
tomorrow
```

LLM converts:

```text
2026-04-21
```

---

# select_slot_node()

Shows available slots.

Example:

```text
10 AM
11 AM
2 PM
```

---

# confirm_node()

Shows final summary.

---

## Example

```text
Doctor: Dr Smith
Date: 2026-04-21
Time: 10 AM
```

---

# collect_details_node()

Collects:

* name
* phone
* email

using interrupts.

---

# completed_node()

Final booking logic.

---

## Saves booking

```python
confirm_booking(...)
```

Stores appointment in DB.

---

## Sends email

```python
send_confirmation_email(...)
```

---

# cancelled_node()

Handles cancellation.

---

# 11. BUILDING THE GRAPH

```python
workflow = StateGraph(BookingState)
```

Creates workflow engine.

---

# ADDING NODES

```python
workflow.add_node(...)
```

Registers nodes.

---

# ENTRY POINT

```python
workflow.set_entry_point("greeting")
```

Conversation starts here.

---

# CONDITIONAL EDGES

```python
workflow.add_conditional_edges(...)
```

Dynamic routing.

Example:

```text
Greeting
  ├── greeting
  ├── select_speciality
  └── cancelled
```

---

# GRAPH FLOW

Full flow:

```text
Greeting
   ↓
Select Specialty
   ↓
Select Doctor
   ↓
Select Date
   ↓
Select Slot
   ↓
Confirm
   ↓
Collect Details
   ↓
Completed
```

---

# 12. MEMORY

```python
MemorySaver()
```

Stores conversation state.

So user can continue after interruption.

---

# 13. process_message()

Main entry function.

---

## What it does

### Step 1

Checks if graph is paused.

```python
current_state.tasks[0].interrupts
```

---

### Step 2

If paused:

```python
Command(resume=user_message)
```

Resumes workflow.

---

### Step 3

Otherwise starts graph normally.

---

# INTERRUPT FLOW EXAMPLE

```text
Assistant:
Choose doctor
```

↓

Workflow pauses.

↓

User:

```text
Dr John
```

↓

Graph resumes from exact point.

---

# COMPLETE ARCHITECTURE

```text
User
  ↓
process_message()
  ↓
LangGraph Workflow
  ↓
Router
  ↓
Conversation Node
  ↓
Groq LLM
  ↓
State Update
  ↓
Interrupt / Continue
  ↓
Database + Email
```

---

production-grade use cases:

✅ state management
✅ workflow orchestration
✅ interrupt/resume
✅ guardrails
✅ structured routing
✅ memory persistence
✅ LLM extraction
✅ dynamic transitions
✅ backend integrations

---


## Hybrid AI Architecture

Instead of letting LLM do everything:

* deterministic workflow handles structure
* LLM handles understanding

This is much more reliable.

---

# Example Conversation Flow

```text
User: Hi

Bot: Welcome to Aurora International Clinic

User: I need skin doctor

→ select_speciality

User: tomorrow

→ select_date

User: 10 AM

→ select_slot

User: confirm

→ collect_details

User: John Doe

→ completed
```
