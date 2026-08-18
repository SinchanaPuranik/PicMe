# Implementation Plan: Photo Deletion Feature

## Overview

This implementation plan breaks down the photo deletion feature into discrete coding tasks. Each task builds incrementally on previous work, with testing integrated throughout. The feature adds a DELETE endpoint, UI components for photo deletion, and comprehensive error handling.

## Tasks

- [ ] 1. Create DELETE route handler in admin blueprint
  - Add `delete_photo(photo_id)` function to `app/routes/admin.py`
  - Apply `@login_required` and `@admin_required` decorators
  - Implement photo file deletion with error handling
  - Implement database deletion with cascade to embeddings
  - Return JSON response with success/error status
  - Add structured logging for all deletion attempts
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 6.4, 10.1, 10.2_

- [ ]* 1.1 Write unit tests for DELETE route authorization
  - Test admin user can delete photos (200 response)
  - Test non-admin user receives 403 error
  - Test unauthenticated user redirects to login
  - _Requirements: 1.1, 1.2, 1.3, 10.4_

- [ ]* 1.2 Write unit tests for DELETE route deletion logic
  - Test photo record deleted from database
  - Test face embeddings cascade deleted
  - Test file removed from filesystem
  - Test missing file doesn't prevent database deletion
  - Test invalid photo ID returns 404
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.3_

- [ ] 2. Add path traversal protection to file deletion
  - Validate file path is within UPLOAD_FOLDER using `os.path.abspath()`
  - Return 400 error for invalid paths
  - Log security warnings for path traversal attempts
  - _Requirements: 6.1, 6.2_

- [ ]* 2.1 Write unit test for path traversal protection
  - Test malicious paths (../../../etc/passwd) are blocked
  - Test valid paths within UPLOAD_FOLDER succeed
  - Test security warnings are logged
  - _Requirements: 6.1, 6.2_

- [ ] 3. Add CSRF protection for AJAX DELETE requests
  - Add CSRF token meta tag to `app/templates/base.html`
  - Ensure Flask-WTF CSRFProtect is initialized in `app/__init__.py`
  - _Requirements: 10.1_

- [ ]* 3.1 Write unit test for CSRF protection
  - Test DELETE request without CSRF token fails (400 error)
  - Test DELETE request with valid CSRF token succeeds
  - _Requirements: 10.1_

- [ ] 4. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Add delete button to photo cards in event view
  - Modify `app/templates/admin/view_event.html` photo card template
  - Add delete button with red danger styling
  - Add trash icon from Font Awesome
  - Include data attributes: `data-photo-id` and `data-photo-filename`
  - Add CSS for hover effects (darker shade)
  - _Requirements: 3.1, 7.1, 7.2, 7.3, 7.4_

- [ ] 6. Create confirmation modal in event view template
  - Add Bootstrap modal HTML to `app/templates/admin/view_event.html`
  - Display photo filename in modal body
  - Show warning that action cannot be undone
  - Add Cancel button (closes modal)
  - Add Delete button (confirms deletion)
  - _Requirements: 3.2, 8.1, 8.2, 8.3, 8.4_

- [ ] 7. Implement JavaScript delete handler
  - Add JavaScript to `{% block extra_js %}` in `app/templates/admin/view_event.html`
  - Handle delete button click event (show modal)
  - Handle confirm button click event (send AJAX DELETE)
  - Include CSRF token in AJAX request headers
  - Remove photo card from DOM on success with fade animation
  - Display success message on successful deletion
  - Display error message on failure with details
  - Disable confirm button during request (prevent double-clicks)
  - Handle network errors gracefully
  - Update photo count statistics after deletion
  - Show empty state when last photo deleted
  - _Requirements: 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3_

- [ ]* 7.1 Write integration test for full deletion workflow
  - Test complete flow: upload photo → process photo → delete photo
  - Verify photo record removed from database
  - Verify face embeddings cascade deleted
  - Verify photo file removed from filesystem
  - _Requirements: 2.1, 2.2, 2.3, 3.3, 3.4_

- [ ]* 7.2 Write integration test for UI state updates
  - Test deleting last photo shows empty state
  - Test photo count updates after deletion
  - Test sequential deletion of multiple photos
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 8. Add database transaction safety
  - Ensure database rollback on errors in delete route
  - Add exception handling with rollback in `delete_photo()` function
  - _Requirements: 6.3, 9.3, 9.4_

- [ ]* 8.1 Write unit tests for transaction safety
  - Test database error triggers rollback
  - Test photo still exists after failed deletion
  - Test concurrent deletion (first succeeds, second gets 404)
  - _Requirements: 6.3, 9.1, 9.2, 9.3, 9.4_

- [ ] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP delivery
- The design uses Python (Flask framework) with SQLAlchemy ORM for database operations
- JavaScript uses jQuery for AJAX calls and DOM manipulation
- Bootstrap 5 provides modal component and styling
- File deletion is non-critical; database deletion succeeds even if file deletion fails
- SQLAlchemy cascade deletion automatically removes face embeddings when photos are deleted
- CSRF protection is required for all DELETE requests to prevent cross-site attacks
- Path traversal protection prevents malicious file path manipulation
- All deletion attempts are logged with timestamp, photo ID, user ID, and outcome for audit purposes

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "3.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["5.1", "6.1"] },
    { "id": 3, "tasks": ["7.1"] },
    { "id": 4, "tasks": ["7.2", "8.1"] }
  ]
}
```
