# Global Trends Feed Fix TODO

## Plan Steps (Approved & Focused)

### 1. [ ] Create this TODO.md ✅
### 2. [✅] Update api_service.dart 
   - Enhanced getFeedPosts parsing for all shapes
   - Added debug prints: FEED RAW/PARSED
### 3. [✅] Update app_data.dart
   - Added GLOBAL POSTS COUNT debug print
### 4. [✅] Update global_page.dart
   - Added BUILD debug print
### 5. [ ] Test & Verify
   - Create post → check console logs
   - Global Trends shows posts
### 6. [ ] Mark complete & cleanup prints if desired

**Expected Debug Flow:**
```
FEED RAW RESPONSE: {...}
PARSED POSTS COUNT: 3
[DEBUG] Loaded 3 feed posts
GLOBAL POSTS COUNT IN UI: 3
BUILD: globalPosts.length = 3
```

