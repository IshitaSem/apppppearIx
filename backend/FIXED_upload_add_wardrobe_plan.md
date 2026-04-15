# Upload → BG Remove → Wardrobe Fix Plan

## Root Causes
1. add_item_page.dart: Local image pick + bg_remove → local WardrobeItem return (no backend /upload/)
2. wardrobe_page.dart: _loadWardrobe() uses API but addNewItem() expects local Navigator return → no refresh
3. app_data.dart: Local mock wardrobeItems → overrides API data
4. wardrobe_item_card.dart: Image.network but local paths fail
5. fashion_tools.outfit_generator: Calls API but wardrobe empty (local vs backend mismatch)

## File Changes

**Backend (no change needed)**
- upload.py: Works (multipart → uploads/ → wardrobe_collection)
- wardrobe.py: Works (GET /all?user_id)
- fashion_tools.py: Works (uses wardrobe_collection)

**Frontend fixes**
1. `add_item_page.dart`: After bg_remove, call ApiService.uploadImage(userId, image, true) → get backend item → WardrobeItem.fromBackend → Navigator.pop
2. `wardrobe_page.dart`: After _addNewItem Navigator.pop, call _loadWardrobe()
3. `app_data.dart`: Remove wardrobeItems mock, load in constructor or on login
4. `api_service.dart`: Add fromBackendItem(Map) factory
5. `wardrobe_item_card.dart`: Prefer Image.network(backend URL) → fallback asset/local

**Fashion tools**
- outfit_generator_page.dart: Calls generateOutfit → mock local → fix to use real backend wardrobe
- cat_judge_page.dart: Calls judgeOutfit → good, uses wardrobeItems indices

**Followup**
1. Test upload → wardrobe show
2. Test fashion tools w/ real wardrobe data
3. Remove local mocks

Ready to implement?
