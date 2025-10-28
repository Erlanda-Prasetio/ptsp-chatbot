## Rate Limit Handling (429 Too Many Requests)

**Problem:** 
OpenRouter API returning `HTTP 429: Too Many Requests` errors, causing API failures.

**Solution Implemented:**

### 1. **LLM Query (ask.py)**
- Added explicit rate limit delay: `rate_limit_delay = 30` seconds
- When 429 error is detected, wait 30 seconds before retry
- Maintains exponential backoff for other server errors
- Max retries: 3 attempts

**Code Changes:**
```python
# Retry configuration
max_retries = 3
base_delay = 2
rate_limit_delay = 30  # Longer wait for 429 rate limits

# In exception handling:
elif status_code == 429:  # Rate limit
    print(f"⏳ Rate limit hit (429), waiting {rate_limit_delay}s before retry...")
    time.sleep(rate_limit_delay)
```

### 2. **Embedding (embed.py)**
- Added full retry logic with rate limit handling
- Implements exponential backoff for server errors (5xx)
- 30-second wait for rate limit (429) errors
- Max retries: 3 attempts
- Proper error propagation if all retries fail

**Code Changes:**
```python
# Retry loop for embedding
for attempt in range(max_retries):
    try:
        r = requests.post(...)
        r.raise_for_status()
        return embeddings
    except HTTPError as e:
        if status_code == 429:
            time.sleep(rate_limit_delay)  # 30 seconds
        elif status_code >= 500:
            time.sleep(base_delay * (2 ** attempt))  # Exponential backoff
```

### 3. **Strategy**

| Error | Delay | Action |
|-------|-------|--------|
| **429** (Rate Limit) | 30s | Wait, then retry immediately |
| **503** (Service Down) | 2s, 4s, 8s | Exponential backoff retries |
| **500+** (Server Error) | 2s, 4s, 8s | Exponential backoff retries |
| **4xx** (Client Error) | - | Return error immediately |

### 4. **Timeout Protection**
- LLM calls: 60 second timeout
- Embedding calls: 30 second timeout
- These ensure stuck requests don't block the system

### 5. **Fallback Mechanism**
- If all retries exhaust: Return fallback response
- Fallback includes DPMPTSP contact info and service hours
- User is informed of temporary service unavailability

### Testing
Run single query test to verify rate limit handling:
```bash
python test_api_limit.py
```

If you hit rate limit again, the system will now:
1. Detect 429 error ✅
2. Wait 30 seconds ✅
3. Retry the request ✅
4. Return response on success or fallback on failure ✅
