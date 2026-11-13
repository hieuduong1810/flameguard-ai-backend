# Runtime storage setup and rollback

T062's accepted chat boundary uses the same database with separate credentials.
`DATABASE_URL` retains a SELECT-only scientific reader. Set the secret
`RUNTIME_DATABASE_URL` to a separate PostgreSQL writer on the same host, port and
database. Runtime identity checks also compare database OIDs. Keep credentials
in ignored local settings or server secret management.

The operator must configure a dedicated role with schema USAGE, SELECT on chat
tables and required source/investigation tables, and INSERT on exactly
`chat_session`, `chat_message`, `message_citation`. No table UPDATE, DELETE,
TRUNCATE or TRIGGER rights are permitted. The runtime role cannot own tables,
create databases/roles/schema, bypass RLS, replicate, or belong to another role.
Review inherited and PUBLIC privileges. Runtime requests reject invalid grants.
FK enforcement retains references to original source and investigation IDs.

Enable the explicit admission configuration fields below only after reviewing
the existing scientific snapshot. Every runtime table must have an empty array
in that snapshot. The manifest still declares all 21 table schemas. The v2 reader
checks exact values/membership of the remaining 18 tables, preserving origin,
review, source and identity rules. Its scientific fingerprint includes the
boundary version and ignores only the three declared runtime tables.

```json
{
  "admissionVersion": 2,
  "runtimeTables": ["chat_message", "chat_session", "message_citation"]
}
```

Existing v1 manifests keep all-table exact admission. A v1 manifest continues to
reject extra runtime rows. Unknown exclusions and nonempty runtime snapshot rows
are rejected. Runtime scenario writes remain outside this chat-only boundary.

Rollback disables `RUNTIME_DATABASE_URL` and stops chat writes, while retaining
existing runtime records and the reviewed v2 scientific boundary. Switching a
populated database back to v1 needs a separately planned data/configuration
transition. Operator cleanup requires exact-target authorization. Tests create
fresh isolated databases and roles and retain them for inspection.
