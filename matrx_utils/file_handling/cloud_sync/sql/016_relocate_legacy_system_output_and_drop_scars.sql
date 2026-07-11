-- =============================================================================
-- 016 — One-time data cleanup: relocate legacy bare system output under
--        system-files/, and drop the empty __dedup_ duplicate-folder scars.
-- =============================================================================
--
-- Companion to migration 015. 015 makes system-files/ + generations/ hidden
-- and self-classifying. This migration moves the PRE-registry legacy output
-- that still sits at bare top-level (created before the SystemPathRegistry was
-- wired into the savers) into the system namespace so 015's filter hides it,
-- and removes the empty rename-scars left by a 2026-05-11 manual de-dup.
--
-- Provenance: these roots are all system-created, never user-uploaded:
--   crawls/        — web-crawl HTML + markdown snapshots (the 4,486-file flood)
--   sites/         — per-site crawl captures
--   tool-images/   — tool-generated images
--   ai-media/      — AI-generated media
--   browser-agent/ — browser-agent page captures
--   system/        — earlier ad-hoc system namespace (matrx-extend captures)
--
-- Re-pathing is purely LOGICAL: cld_files.file_path / cld_folders.folder_path
-- change; cld_files.storage_uri (the S3 object key) is untouched, so no bytes
-- move and every URL keeps resolving. The is_system auto-stamp trigger from
-- 015 flags the relocated folders as it rewrites folder_path.
--
-- Reversible in principle (strip the 'system-files/' prefix back off), but the
-- scar DELETE is not — those 6 folders are confirmed empty (0 files,
-- 0 subfolders) duplicates and carry no data.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 0. Drop the empty __dedup_ duplicate scars FIRST — before relocation, while
--    they are still is_system=false. (If relocated under system-files/ first,
--    the protection trigger would then block their deletion.) Guarded so we
--    only ever delete folders that are genuinely empty.
-- ---------------------------------------------------------------------------
DELETE FROM cld_folders
 WHERE folder_path ~ '__dedup_'
   AND deleted_at IS NULL
   AND NOT EXISTS (
       SELECT 1 FROM cld_files f
        WHERE f.owner_id = cld_folders.owner_id
          AND f.deleted_at IS NULL
          AND (f.file_path = cld_folders.folder_path
               OR f.file_path LIKE cld_folders.folder_path || '/%')
   )
   AND NOT EXISTS (
       SELECT 1 FROM cld_folders s
        WHERE s.owner_id = cld_folders.owner_id
          AND s.deleted_at IS NULL
          AND s.id <> cld_folders.id
          AND s.folder_path LIKE cld_folders.folder_path || '/%'
   );

-- ---------------------------------------------------------------------------
-- 1. Ensure a system-files/ root folder exists for every owner who has legacy
--    output (so the relocated top-level folders get a real parent). Covers
--    owners who have only files (no folder rows) in the bare roots too.
-- ---------------------------------------------------------------------------
INSERT INTO cld_folders (owner_id, folder_path, folder_name, parent_id, visibility)
SELECT DISTINCT owner_id, 'system-files', 'system-files', NULL::uuid, 'private'
  FROM cld_folders
 WHERE deleted_at IS NULL
   AND split_part(folder_path, '/', 1)
       IN ('crawls','sites','tool-images','ai-media','browser-agent','system')
ON CONFLICT (owner_id, folder_path) DO NOTHING;

INSERT INTO cld_folders (owner_id, folder_path, folder_name, parent_id, visibility)
SELECT DISTINCT owner_id, 'system-files', 'system-files', NULL::uuid, 'private'
  FROM cld_files
 WHERE deleted_at IS NULL
   AND split_part(file_path, '/', 1)
       IN ('crawls','sites','tool-images','ai-media','browser-agent','system')
ON CONFLICT (owner_id, folder_path) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2. Relocate the folder rows. The 015 trigger flips is_system → true as it
--    rewrites folder_path. Existing parent_id links between non-top folders
--    are id-based, so they survive the rename automatically.
-- ---------------------------------------------------------------------------
UPDATE cld_folders
   SET folder_path = 'system-files/' || folder_path
 WHERE deleted_at IS NULL
   AND split_part(folder_path, '/', 1)
       IN ('crawls','sites','tool-images','ai-media','browser-agent','system');

-- ---------------------------------------------------------------------------
-- 3. Re-parent the formerly-top-level folders (now at system-files/<root>,
--    exactly two segments deep, parent_id still NULL) onto the system-files
--    root folder.
-- ---------------------------------------------------------------------------
UPDATE cld_folders d
   SET parent_id = root.id
  FROM (
        SELECT owner_id, id
          FROM cld_folders
         WHERE folder_path = 'system-files' AND deleted_at IS NULL
       ) root
 WHERE d.owner_id = root.owner_id
   AND d.deleted_at IS NULL
   AND d.parent_id IS NULL
   AND d.folder_path LIKE 'system-files/%'
   AND d.folder_path <> 'system-files'
   AND split_part(d.folder_path, '/', 3) = '';   -- exactly system-files/<one segment>

-- ---------------------------------------------------------------------------
-- 4. Relocate the file rows (logical path only; storage_uri untouched). After
--    this they are hidden by 015's file-leg filter.
-- ---------------------------------------------------------------------------
UPDATE cld_files
   SET file_path = 'system-files/' || file_path
 WHERE deleted_at IS NULL
   AND split_part(file_path, '/', 1)
       IN ('crawls','sites','tool-images','ai-media','browser-agent','system');

COMMIT;
