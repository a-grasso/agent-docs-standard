# CenterSight infrastructure - topology entry point.
#
# Governing docs (see ./AGENTS.md and the ADRs it cites):
#   - root ADR-0003 : telemetry store is append-only -> lifecycle rule forbids destroy, adds
#                      cold-tiering of old partitions.
#   - functions ADR-0001 : idempotent ingestion needs a unique index on reading_id.

module "event_bus" {
  source = "./modules/event-bus"
  env    = var.env
}

module "telemetry_store" {
  source = "./modules/telemetry-store"
  env    = var.env

  # Append-only: never let Terraform destroy or replace the readings table (root ADR-0003).
  lifecycle_prevent_destroy = true
  dedupe_unique_key         = "reading_id" # functions ADR-0001
  cold_tier_after_days      = 90
}
