# Enforcer for the "Write-once telemetry grant" constraint in ../AGENTS.md.
#
# Governing doc: root ADR-0003 - the readings table grants insert and read, and nothing else.
# The application-side counterpart is ../../functions/test/ingest.contract.test.ts. Both are
# needed: this one holds even for a client that bypasses the handler.

run "telemetry_grant_is_write_once" {
  command = plan

  assert {
    condition     = alltrue([for a in module.telemetry_store.readings_actions :
                    contains(["store:PutItem", "store:Query", "store:GetItem"], a)])
    error_message = "readings grant must not include update or delete actions (root ADR-0003)"
  }

  assert {
    condition     = module.telemetry_store.prevent_destroy == true
    error_message = "the readings table must not be destroyable by a plan (root ADR-0003)"
  }
}
