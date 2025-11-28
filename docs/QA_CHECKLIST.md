---------------------------------------
FILE START: ~/senti_system/docs/QA_CHECKLIST.md
---------------------------------------
# Senti System — QA CHECKLIST (Human Quality Assurance)
Version: 1.0
Location: ~/senti_system/docs/QA_CHECKLIST.md

This document defines the complete manual QA procedure
that must be performed when reviewing Senti OS, Senti Core,
and all Senti Modules.

It complements:
- PROJECT_RULES.md
- SENTI_CORE_AI_RULES.md
- self_check_schema.json
- SELF_CHECK_PROMPT.md


=========================================================
   SECTION 1 — PROJECT STRUCTURE QA
=========================================================

[ ] 1. All required root folders exist:
      senti_os/
      senti_core/
      modules/
      config/
      docs/
      tests/
      scripts/

[ ] 2. No unauthorized root folder exists.
[ ] 3. No immutable directory has been modified:
      senti_os/kernel/
      senti_os/system/
      senti_os/boot/
      senti_core/runtime/
      senti_core/api/
      senti_core/services/
      modules/_templates/

[ ] 4. All __init__.py files are present in Python packages.


=========================================================
   SECTION 2 — ARCHITECTURE QA
=========================================================

[ ] 5. Architecture flow is respected:
      modules → senti_core → senti_os

[ ] 6. No module directly accesses OS layer.
[ ] 7. No cross-layer imports exist.
[ ] 8. All imports are absolute (no relative imports).
[ ] 9. No directory traversal (“../”) is used.


=========================================================
   SECTION 3 — CODE GENERATION QA
=========================================================

[ ] 10. All generated files are listed clearly.
[ ] 11. Each file is output in full (never in patch form).
[ ] 12. No mock data or placeholder content.
[ ] 13. No lorem ipsum or incomplete stubs.
[ ] 14. All file paths are valid and inside senti_system.


=========================================================
   SECTION 4 — SECURITY QA
=========================================================

[ ] 15. No .env file has been created or modified.
[ ] 16. No API keys, secrets, passwords, tokens generated.
[ ] 17. No external filesystem access.
[ ] 18. No network calls unless explicitly allowed.
[ ] 19. No critical system logic overwritten.


=========================================================
   SECTION 5 — MODULE QA
=========================================================

If a module is created:

[ ] 20. module.json exists.
[ ] 21. module.json conforms to config/modules/schema.json.
[ ] 22. Module inherits from correct base class.
[ ] 23. Module provides load(), start(), stop(), metadata.

If no module is created — skip.


=========================================================
   SECTION 6 — TESTS QA
=========================================================

[ ] 24. Tests are deterministic (no randomness).
[ ] 25. Tests do not use mock data.
[ ] 26. Tests cover loader, registry, system_health, etc.


=========================================================
   SECTION 7 — CONFIG QA
=========================================================

[ ] 27. config/system/config.yaml exists and is valid.
[ ] 28. config/modules/schema.json is valid.
[ ] 29. All modules meet schema requirements.


=========================================================
   SECTION 8 — RELEASE QA
=========================================================

[ ] 30. CHANGELOG.md updated.
[ ] 31. All generated files have clean formatting.
[ ] 32. No unused imports.
[ ] 33. No commented-out blocks.
[ ] 34. Version identifiers correctly incremented.


=========================================================
 END OF QA CHECKLIST
=========================================================
---------------------------------------
FILE END: ~/senti_system/docs/QA_CHECKLIST.md
---------------------------------------
