-- pdf_redaction_audits — every PDF redaction operation produces one row.
--
-- The matrx-utils RedactionEngine yields a `RedactionAudit` payload; the
-- host (aidream) is responsible for persisting this row via matrx-orm
-- before returning the post-redaction file to the user.
--
-- Per design §7.3 + the per-user-resource-ownership contract in root
-- CLAUDE.md, the row is owned by user_id and gated by RLS via
-- public.is_resource_owner / public.check_resource_access.
--
-- Apply as a matrx-orm migration when wiring this into a project.

create schema if not exists pdf;

create table if not exists pdf.pdf_redaction_audits (
    id                       uuid primary key default gen_random_uuid(),
    parent_file_id           uuid references public.cld_files(id) on delete set null,
    file_id                  uuid references public.cld_files(id) on delete cascade,
    user_id                  uuid not null references auth.users(id) on delete cascade,
    reason                   text not null,
    redaction_kind           text not null
        check (redaction_kind in (
            'regions','pattern','entities','repeated_regions',
            'metadata','forms','attachments','javascript',
            'annotations','composite'
        )),
    redaction_params         jsonb not null default '{}'::jsonb,
    tier_used                text not null default 'stream_rewrite'
        check (tier_used in ('stream_rewrite','rasterize','mixed','n/a')),
    status                   text not null default 'success'
        check (status in ('success','verification_failed','no_targets')),
    bytes_removed_estimate   bigint not null default 0,
    regions_count            integer not null default 0,
    created_at               timestamptz not null default now()
);

create index if not exists pdf_redaction_audits_user_idx
    on pdf.pdf_redaction_audits (user_id, created_at desc);
create index if not exists pdf_redaction_audits_file_idx
    on pdf.pdf_redaction_audits (file_id);
create index if not exists pdf_redaction_audits_parent_idx
    on pdf.pdf_redaction_audits (parent_file_id);

-- Enable RLS so the per-user ownership contract applies.
alter table pdf.pdf_redaction_audits enable row level security;

-- SELECT — only the owner (or a registered admin) may read.
create policy pdf_redaction_audits_select on pdf.pdf_redaction_audits
    for select using (
        public.is_resource_owner('pdf_redaction_audits', id, auth.uid())
    );

-- INSERT — only the row owner.
create policy pdf_redaction_audits_insert on pdf.pdf_redaction_audits
    for insert with check (user_id = auth.uid());

-- The audit row is intentionally append-only.  No update / delete policies.

-- Register the resource type so check_resource_access knows about it.
insert into public.shareable_resource_registry
    (resource_type, owner_column, ownership_check)
values (
    'pdf_redaction_audits',
    'user_id',
    'standard'
) on conflict do nothing;
