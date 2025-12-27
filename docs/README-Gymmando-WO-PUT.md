# Gymmando PUT Architecture - Full Implementation Guide

## Overview
This document outlines the complete architecture for handling workout logging (PUT operations) in Gymmando, from voice input to database storage.

---

## System Architecture

```
Voice Input (LiveKit)
    ↓
[Router Agent] → Determines module + intent
    ↓
[Workout Logger Agent] → Extracts workout data
    ↓
[State Machine] → Tracks completion
    ↓
[Response Generator] → Asks for missing data
    ↓
[Confirmation] → Shows summary
    ↓
[Database] → Saves to Supabase
```

---

## Components

### 1. Router Agent
**Purpose:** Classify user intent and route to correct module

**LLM:** Groq Llama 3.1 8B (fast, cheap classification)

**Input:**
```python
{
    "user_input": "save my squats for today"
}
```

**Output:**
```json
{
    "module": "workout",
    "intent": "log"
}
```

**Prompt Template:**
```
You are a router agent for Gymmando fitness app.
Classify the user's intent into:
- module: "workout" | "nutrition" | "measurement" | "general"
- intent: "log" | "query" | "question"

User input**Prompt Strategy:**
- Show current state to LLM
- Ask to extract ANY new data from user input
- Merge with existing state (don't overwrite filled fields)
- Return complete updated state as JSON

**Key Instructions for LLM:**
1. Preserve all previously filled fields
2. Only update fields mentioned in new input
3. Recognize variations (e.g., "bodyweight", "BW", "no weight")
4. Handle units (lbs, kg, pounds, kilograms)
5. Extract implicit info (e.g., "3x12" means sets=3, reps=12)

**Key Settings:**
- Model: `llama-3.1-70b-versatile`
- Temperature: 0.2 (slightly creative for variation handling)
- Response format: JSON
- Max tokens: 200

---

### 4. State Machine

**Purpose:** Orchestrate the conversation flow

**States:**
1. **INIT** - Starting state
2. **EXTRACTING** - Gathering data from user
3. **CONFIRMING** - Showing summary
4. **SAVING** - Writing to database
5. **COMPLETE** - Workout logged

**Flow Logic:**

**State: INIT**
- Trigger: User starts logging
- Action: Call Logger Agent with empty state
- Next: EXTRACTING

**State: EXTRACTING**
- Check: `state.is_complete()`
- If FALSE:
  - Get missing fields
  - Generate question asking for ALL missing required fields
  - Wait for user response
  - Call Logger Agent with user input + current state
  - Loop back to EXTRACTING
- If TRUE:
  - Move to CONFIRMING

**State: CONFIRMING**
- Action: Generate summary of all workout data
- Ask: "Save this workout?"
- Wait for user confirmation (yes/no)
- If YES: Move to SAVING
- If NO: Ask what to change, move back to EXTRACTING

**State: SAVING**
- Action: Call database save function
- On success: Move to COMPLETE
- On error: Retry or notify user

**State: COMPLETE**
- Action: Send success message
- Reset state
- End conversation

---

### 5. Response Generator

**Purpose:** Create natural questions to collect missing data

**Input:**
```
missing_fields: ["sets", "reps", "weight"]
```

**Output:**
```
"Great! Can you tell me the sets, reps, and weight you used?"
```

**Question Templates:**

For 3+ missing fields:
- "Can you tell me the {field1}, {field2}, and {field3}?"

For 2 missing fields:
- "What about the {field1} and {field2}?"

For 1 missing field:
- "And what {field} did you use?"

**Friendly variations:**
- "Great! Now I need..."
- "Got it! Tell me about..."
- "Perfect! Last thing - what's the..."

**Tone:** Conversational, encouraging, concise

---

### 6. Confirmation Display

**Purpose:** Show workout summary before saving

**Format:**
```
Summary:
• Exercise: Squats
• Sets: 3
• Reps: 20
• Weight: Bodyweight
• Rest time: 60 seconds
• Comments: Felt strong today

Save this workout?
```

**Display Rules:**
- Show all filled fields (required + optional)
- Skip null optional fields
- Use bullet points for readability
- Clear yes/no prompt

**Possible User Responses:**
- "yes" / "yeah" / "sure" / "correct" → SAVE
- "no" / "nope" / "wait" → Ask what to change
- "change the weight" → Update specific field

---

### 7. Database Schema

**Table:** `workouts`

**Columns:**
- `id` (UUID, primary key, auto-generated)
- `user_id` (string, indexed) - Firebase UID
- `exercise` (string, required)
- `sets` (integer, required)
- `reps` (integer, required)
- `weight` (string, required)
- `rest_time` (integer, nullable)
- `duration` (integer, nullable)
- `comments` (text, nullable)
- `muscle_group` (string, nullable)
- `created_at` (timestamp, auto-generated)
- `updated_at` (timestamp, auto-updated)

**Indexes:**
- `user_id` (for filtering user's workouts)
- `created_at` (for date-based queries)
- Composite: `(user_id, created_at)` (for recent workouts)

**Row Level Security (RLS):**
- Users can only INSERT/SELECT their own workouts
- Filter: `user_id = auth.uid()`

---

## Complete Flow Example

### Example 1: Partial Initial Input

**User:** "Gymmando, save my squats for today"

**Step 1 - Router Agent**
- Input: "save my squats for today"
- Output: `{module: "workout", intent: "log"}`

**Step 2 - Logger Agent (Call #1)**
- Input: user_input + empty state
- Output: `{exercise: "squats", sets: null, reps: null, weight: null}`

**Step 3 - State Machine**
- Check: `is_complete()` → FALSE
- Missing: ["sets", "reps", "weight"]
- State: EXTRACTING

**Step 4 - Response Generator**
- Output: "Got it! Can you tell me the sets, reps, and weight?"

**User:** "Sure, reps 20, sets 3"

**Step 5 - Logger Agent (Call #2)**
- Input: "reps 20, sets 3" + current state
- Output: `{exercise: "squats", sets: 3, reps: 20, weight: null}`

**Step 6 - State Machine**
- Check: `is_complete()` → FALSE
- Missing: ["weight"]
- State: EXTRACTING

**Step 7 - Response Generator**
- Output: "And what weight did you use?"

**User:** "Bodyweight"

**Step 8 - Logger Agent (Call #3)**
- Input: "bodyweight" + current state
- Output: `{exercise: "squats", sets: 3, reps: 20, weight: "bodyweight"}`

**Step 9 - State Machine**
- Check: `is_complete()` → TRUE
- State: CONFIRMING

**Step 10 - Confirmation**
- Display summary
- Ask: "Save this workout?"

**User:** "Yes"

**Step 11 - Database Save**
- Insert workout into Supabase
- State: SAVING → COMPLETE

**Step 12 - Success Response**
- Output: "Logged! Great work! 💪"

---

### Example 2: Complete Initial Input

**User:** "Log 3 sets of 12 bench press at 135 pounds"

**Step 1 - Router Agent**
- Output: `{module: "workout", intent: "log"}`

**Step 2 - Logger Agent (Call #1)**
- Output: `{exercise: "bench press", sets: 3, reps: 12, weight: "135 lbs"}`

**Step 3 - State Machine**
- Check: `is_complete()` → TRUE
- State: CONFIRMING

**Step 4 - Confirmation**
- Show summary
- Ask: "Save this workout?"

**User:** "Yes"

**Step 5 - Database Save**
- Insert and confirm

**Total LLM calls: 2** (Router + Logger)

---

## Implementation Checklist

### Phase 1: Core Components
- [ ] Set up Groq API integration
- [ ] Create WorkoutState class with validation methods
- [ ] Implement Router Agent
- [ ] Implement Logger Agent
- [ ] Build State Machine logic

### Phase 2: Conversation Flow
- [ ] Create Response Generator with templates
- [ ] Build Confirmation display formatter
- [ ] Handle user confirmation responses (yes/no/change)

### Phase 3: Database
- [ ] Create Supabase `workouts` table
- [ ] Set up RLS policies
- [ ] Create database save function
- [ ] Add error handling for DB operations

### Phase 4: Integration
- [ ] Connect LiveKit voice input
- [ ] Wire all components together
- [ ] Add conversation state persistence
- [ ] Implement timeout handling (if user goes silent)

### Phase 5: Testing
- [ ] Test with complete initial input
- [ ] Test with partial input (multiple rounds)
- [ ] Test edge cases (ambiguous units, typos)
- [ ] Test confirmation changes
- [ ] Test database failures

### Phase 6: Optimization
- [ ] Set up rate limiting per user
- [ ] Add usage tracking
- [ ] Monitor LLM costs
- [ ] Optimize prompts for token efficiency

---

## Cost Estimates (100 Users)

**Groq LLM Calls:**
- Free tier: 14,400 requests/day
- Average: 2-3 calls per workout logged
- 100 users × 10 workouts/month = 1,000 workouts
- Total calls: ~2,500/month
- **Cost: FREE** (well within limits)

**Supabase:**
- Storage: ~10KB per workout
- 1,000 workouts = 10MB
- **Cost: FREE** (within 500MB limit)

**Total monthly cost for PUT operations: $0**

---

## Error Handling

**LLM Failures:**
- Retry up to 3 times
- If all fail: "Sorry, I'm having trouble. Can you try again?"

**Database Failures:**
- Retry connection
- Save state locally temporarily
- Notify user: "Saved locally, will sync when connection returns"

**Ambiguous Input:**
- Logger can't extract data
- Response: "I didn't catch that. Can you repeat the {missing_field}?"

**User Abandons Flow:**
- Timeout after 2 minutes of silence
- Save partial state
- Next time: "Want to finish logging your squats from earlier?"

---

## Future Enhancements

**Quick Log:**
- Recognize frequent exercises
- Pre-fill previous weights/reps
- User just confirms or adjusts

**Voice Shortcuts:**
- "Same as last time" → Copy previous workout
- "Add 5 pounds" → Increment weight
- "Drop set" → Automatically log progressive sets

**Smart Defaults:**
- Learn user's typical rest times
- Suggest weights based on history
- Auto-detect muscle groups

**Multi-Exercise Sessions:**
- "Log my leg day" → Multiple exercises in one session
- Track entire workout as single session

---

## Key Design Principles

1. **Minimize LLM Calls** - Batch questions, extract everything possible in one call
2. **Natural Conversation** - Don't make users learn specific formats
3. **Forgiving Parsing** - Handle variations, typos, different units
4. **Clear Feedback** - Always confirm what was understood
5. **Fail Gracefully** - Never lose user's data
6. **Cost Conscious** - Stay within free tiers for testing phase

---

## Tech Stack Summary

**LLM:** Groq (Llama 3.1 8B + 70B)
**Framework:** LangGraph (state management)
**Database:** Supabase (PostgreSQL)
**Voice:** LiveKit (already handled)
**Language:** Python (FastAPI backend)

---

## Next Steps

1. Review this architecture with your team
2. Set up Groq API account and get API key
3. Create Supabase workouts table
4. Start with Router Agent implementation
5. Build Logger Agent with test prompts
6. Wire State Machine logic
7. Test end-to-end with mock voice inputs
8. Deploy to staging
9. Test with real users on TestFlight

---

**Questions or clarifications needed? Let me know which section to expand!**

Return ONLY valid JSON with module and intent.
```

**Key Settings:**
- Model: `llama-3.1-8b-instant`
- Temperature: 0.1 (deterministic)
- Response format: JSON
- Max tokens: 100

---

### 2. Workout State Schema

**Purpose:** Track workout data throughout conversation

**Required Fields:**
- `exercise` (string) - Name of exercise
- `sets` (integer) - Number of sets
- `reps` (integer) - Repetitions per set
- `weight` (string) - Weight used (e.g., "50 lbs", "bodyweight")

**Optional Fields:**
- `rest_time` (integer) - Rest between sets in seconds
- `duration` (integer) - Total exercise duration in seconds
- `comments` (string) - User notes
- `muscle_group` (string) - Target muscle group

**Metadata:**
- `user_id` (string) - Firebase UID
- `timestamp` (string) - ISO format datetime

**State Methods:**
- `get_missing_required_fields()` → Returns list of unfilled required fields
- `is_complete()` → Boolean check if all required fields filled

---

### 3. Logger Agent

**Purpose:** Extract workout information from natural language

**LLM:** Groq Llama 3.1 70B (better extraction accuracy)

**Input Format:**
```
user_input: "reps 20, sets 3"
current_state: {exercise: "squats", sets: null, reps: null, weight: null}
```

**Output Format:**
```
{exercise: "squats", sets: 3, reps: 20, weight: null}
```

**Prompt Strategy:**