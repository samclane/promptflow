import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges } from "@angular/core";
import { catchError, combineLatest, filter, map, merge, of, startWith, Subject, take } from "rxjs";
import { FlowchartService } from "./flowchart.service";
import { AbstractControl, FormBuilder, FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import {Flowchart} from "./flowchart";

@Component({
  selector: 'app-flowchart-import-json',
  templateUrl: './flowchart-import-json.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartImportJson implements OnChanges {
  constructor(
    private readonly flowchartService: FlowchartService,
    private readonly formBuilder: FormBuilder
  ) {}

  public readonly flowchartForm = this.formBuilder.nonNullable.control('', [Validators.required, this.jsonValidator]);

  @Input() set flowchartJson(j: string | undefined | null) {
    if (!j) return;
    this.flowchartForm.setValue(j);
  }

  private readonly flowcharts$ = this.flowchartService.flowcharts$;
  
  private readonly responseErrors = new Subject<string>();

  public readonly vm$ = combineLatest({
    flowcharts: this.flowcharts$,
    userHasTyped: this.flowchartForm.valueChanges.pipe(
      map((x) => x.length > 0),
      startWith(false),
    ),
    inputValid: this.flowchartForm.statusChanges.pipe(
      map((x) => x === 'VALID'),
      startWith(false)
    ),
    errorMessage: merge(
      this.flowchartForm.statusChanges.pipe(
        map(() => {
          const errors = this.flowchartForm.errors;
          if (errors === null) return '';

          if (errors['jsonInvalid']) {
            return 'JSON object is invalid';
          }

          return '';
        }),
        startWith(''),
      ),
      this.responseErrors.asObservable()
    ) 
  });

  ngOnChanges(changes: SimpleChanges) {
    if (changes['flowchartJson'] && changes['flowchartJson'].currentValue) {
      this.flowchartForm.get('flowchartJson')?.setValue(this.flowchartJson);
    }
  }

  importJson(): void {
    if (!this.flowchartForm.valid) return;
    const json = this.flowchartForm.value;
    const parsedFlowchart = JSON.parse(json);
    this.flowchartService.upsertFlowchart(parsedFlowchart)
    .pipe(
      take(1),
      catchError((e) => {
        this.responseErrors.next(e.message);
        return of({ error: true });
      }),
      filter((x): x is Flowchart => !('error' in x))
    ).subscribe(() => {
      this.flowchartForm.reset();
      this.flowchartService.getFlowcharts();
    });
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
