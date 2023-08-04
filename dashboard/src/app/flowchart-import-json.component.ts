import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges } from "@angular/core";
import { combineLatest, take } from "rxjs";
import { FlowchartService } from "./flowchart.service";
import { AbstractControl, FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';

@Component({
  selector: 'app-flowchart-import-json',
  templateUrl: './flowchart-import-json.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartImportJson implements OnChanges {
  public flowchartForm: FormGroup;
  @Input() public flowchartJson: string | undefined;
  public userHasTyped: boolean = false;

  constructor(private readonly flowchartService: FlowchartService) {
    this.flowchartForm = new FormGroup({
      flowchartJson: new FormControl('', [Validators.required, this.jsonValidator])
    });
  }

  private readonly flowcharts$ = this.flowchartService.flowcharts$;

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$
  });

  ngOnChanges(changes: SimpleChanges) {
    if (changes['flowchartJson'] && changes['flowchartJson'].currentValue) {
      this.flowchartForm.get('flowchartJson')?.setValue(this.flowchartJson);
    }
  }

  importJson(): void {
    if (this.flowchartForm.valid) {
      const parsedFlowchart = JSON.parse(this.flowchartForm.get('flowchartJson')?.value);
      this.flowchartService.upsertFlowchart(parsedFlowchart).pipe(take(1)).subscribe(() => {
        this.flowchartForm.reset();
        this.flowchartService.getFlowcharts();
      });
    }
  }

  jsonValidator(control: AbstractControl): ValidationErrors | null {
    try {
      JSON.parse(control.value);
    } catch (e) {
      return { jsonInvalid: true };
    }

    return null;
  };

}
