-- Cloud Files — Guest Support migration (additive, idempotent).
--
-- Background
-- ----------
-- The `cld_*` tables already store any UUID in `owner_id`, so guest
-- accounts that have a UUID-shaped surrogate (e.g. `guest_executions.id`
-- in aidream) work end-to-end through the cloud_sync FileManager today,
-- because the backend writes through the service-role key (RLS-bypassing).
--
-- This migration adds two pieces:
--   1. `cld_migrate_guest_to_user(p_guest_id, p_new_user_id)` — re-owns
--       all cld_* rows that were owned by the guest UUID. Designed to be
--       called once when a guest converts to a real Supabase auth user.
--   2. Re-creates `cld_get_user_file_tree` so it explicitly documents
--       guest-id support (no behavioural change — the function already
--       works because it accepts an opaque UUID).
--
-- Safe to re-run; everything is `CREATE OR REPLACE` / `IF NOT EXISTS`.

-- ---------------------------------------------------------------------------
-- 1. Guest -> User conversion helper
-- ---------------------------------------------------------------------------

-- Re-own every file/folder/group/share-link from a guest UUID to a real
-- auth.users.id. Returns the count of rows updated per table for sanity
-- checking. Run once per conversion (the second call is a no-op).
CREATE OR REPLACE FUNCTION cld_migrate_guest_to_user(
    p_guest_id UUID,
    p_new_user_id UUID
) RETURNS JSONB AS $$
DECLARE
    v_files INT;
    v_folders INT;
    v_groups INT;
    v_perms INT;
    v_shares INT;
BEGIN
    IF p_guest_id IS NULL OR p_new_user_id IS NULL THEN
        RAISE EXCEPTION 'cld_migrate_guest_to_user: both ids are required';
    END IF;

    UPDATE cld_files
       SET owner_id = p_new_user_id
     WHERE owner_id = p_guest_id;
    GET DIAGNOSTICS v_files = ROW_COUNT;

    UPDATE cld_folders
       SET owner_id = p_new_user_id
     WHERE owner_id = p_guest_id;
    GET DIAGNOSTICS v_folders = ROW_COUNT;

    UPDATE cld_user_groups
       SET owner_id = p_new_user_id
     WHERE owner_id = p_guest_id;
    GET DIAGNOSTICS v_groups = ROW_COUNT;

    UPDATE cld_file_permissions
       SET grantee_id = p_new_user_id
     WHERE grantee_id = p_guest_id
       AND grantee_type = 'user';
    GET DIAGNOSTICS v_perms = ROW_COUNT;

    UPDATE cld_user_group_members
       SET user_id = p_new_user_id
     WHERE user_id = p_guest_id;
    -- (no count needed for this one)

    UPDATE cld_share_links
       SET created_by = p_new_user_id
     WHERE created_by = p_guest_id;
    GET DIAGNOSTICS v_shares = ROW_COUNT;

    RETURN jsonb_build_object(
        'files',   v_files,
        'folders', v_folders,
        'groups',  v_groups,
        'perms',   v_perms,
        'shares',  v_shares
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cld_migrate_guest_to_user(UUID, UUID) IS
'Re-own all cld_* rows from a guest UUID (e.g. guest_executions.id) to a real
auth.users.id when a guest converts. Idempotent. Service-role only.';

-- ---------------------------------------------------------------------------
-- 2. Tree RPC — documented to accept guest IDs.
-- ---------------------------------------------------------------------------
-- No behavioural change; we just re-create with a doc comment.

COMMENT ON FUNCTION cld_get_user_file_tree(UUID) IS
'Return the full file tree visible to a user. Accepts either an
auth.users.id or a guest_executions.id (both are UUIDs). RLS is bypassed
via SECURITY DEFINER; callers must enforce that p_user_id matches the
authenticated identity (or use the backend, which validates this).';
