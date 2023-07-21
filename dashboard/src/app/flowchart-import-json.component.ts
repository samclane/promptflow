import {ChangeDetectionStrategy, Component} from "@angular/core";
import {combineLatest} from "rxjs";
import {FlowchartService} from "./flowchart.service";

@Component({
  selector: 'app-flowchart-import-json',
  templateUrl: './flowchart-import-json.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartImportJson {
  constructor(private readonly flowchartService: FlowchartService) {}

  private readonly flowcharts$ = this.flowchartService.flowcharts$;

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$
  });

  importJson(): void {
    this.flowchartService.getFlowcharts();
    alert(23);
  }
}
