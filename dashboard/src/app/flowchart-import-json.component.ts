import {ChangeDetectionStrategy, Component} from "@angular/core";
import {combineLatest} from "rxjs";
import {FlowchartService} from "./flowchart.service";
import {FormControl, FormGroup, Validators} from '@angular/forms';

@Component({
  selector: 'app-flowchart-import-json',
  templateUrl: './flowchart-import-json.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartImportJson {
  public flowchartForm: FormGroup;
  public flowchartJson: string = '';

  constructor(private readonly flowchartService: FlowchartService) {
    this.flowchartForm = new FormGroup({
      flowchartJson: new FormControl('', Validators.required)
    });
  }

  private readonly flowcharts$ = this.flowchartService.flowcharts$;

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$
  });

  importJson(): void {
    if (this.flowchartForm.valid) {
      const parsedFlowchart = JSON.parse(this.flowchartForm.get('flowchartJson')?.value);
      console.log(parsedFlowchart);
      this.flowchartService.upsertFlowchart(parsedFlowchart).subscribe(() => {
        // Handle successful import...
        });
    }
  }
}
