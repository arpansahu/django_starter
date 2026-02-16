# Changelog

## [1.1.0] - 2026-02-17
### Fixed
- Fixed incorrect mock paths in user_account tests (11 instances changed from 'account.views.*' and 'account.forms.*' to 'user_account.views.*' and 'user_account.forms.*')
- Fixed CSS selectors in notes_app UI tests to avoid matching hidden notification badges:
  - TestTagListUI.test_link: Scoped badge selector to main/content areas
  - TestNotesByTagUI.test_link: Added main scope to avoid navbar badges
  - TestNoteListUIExtended.test_note_badges: Used `:not(#notif-badge)` to explicitly exclude notification badge

### Changed
- Enabled RUN_TESTS parameter by default in Jenkinsfile-build to run automated tests on every build
- Updated test suite reliability to ensure consistent CI/CD pipeline results

## [1.0.0] - 2024-06-27
### Added
- Initial release of the project.
- User authentication module.