// Plant condition dashboard.
//
// Before extending this (see ../AGENTS.md `dep:`):
//   - ng-ui   : reuse <cs-chart>, <cs-card>, <cs-page> - do not hand-roll charts/layout.
//   - ng-env  : read API base URL & feature flags from EnvService, never from process.env.
//   - centersight-api-doc.com : the /v1/telemetry and /v1/alerts contracts.

import { Component, inject } from "@angular/core";
import { CsChart, CsPage } from "@centersight/ng-ui"; // dep: ng-ui
import { EnvService } from "@centersight/ng-env"; // dep: ng-env
import { TelemetryApi } from "./api/telemetry.api"; // wraps centersight-api

@Component({
  selector: "cs-dashboard",
  standalone: true,
  imports: [CsPage, CsChart],
  template: `<cs-page title="Plant condition">
    <cs-chart [series]="series()" unit="°C" />
  </cs-page>`,
})
export class DashboardComponent {
  private env = inject(EnvService);
  private api = inject(TelemetryApi);
  // series() streams from GET /v1/telemetry?plant=... against env.apiBaseUrl
  series = this.api.stream(this.env.plantId);
}
