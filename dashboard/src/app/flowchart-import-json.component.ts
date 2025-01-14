import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges, EventEmitter, Output } from "@angular/core";
import { catchError, combineLatest, filter, map, merge, of, startWith, Subject, take } from "rxjs";
import { FlowchartService } from "./flowchart.service";
import { AbstractControl, FormBuilder, ValidationErrors, Validators } from '@angular/forms';
import { Flowchart } from "./flowchart";

@Component({
  selector: 'app-flowchart-import-json',
  templateUrl: './flowchart-import-json.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartImportJson implements OnChanges {
  @Output() jsonImported = new EventEmitter<void>();

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
      this.flowchartService.getFlowcharts();
      this.jsonImported.emit();
    });
  }

  jsonValidator(control: AbstractControl): ValidationErrors | null {
    try {
      JSON.parse(control.value);
    } catch (e) {
      return { jsonInvalid: true };
    }

    return null;
  }
  
  public importJsonFile(event: Event): void {
    const input = event.target as HTMLInputElement;
  
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      const reader = new FileReader();
  
      reader.onload = (e) => {
        const contents = e.target?.result as string;
        this.flowchartForm.setValue(contents);
        this.importJson();
      };
  
      reader.readAsText(file);
    }
  }

  formatJson(): void {
    try {
      const json = JSON.parse(this.flowchartForm.value);
      const formattedJson = JSON.stringify(json, null, 2);
      this.flowchartForm.setValue(formattedJson);
    } catch (e) {
      this.vm$.pipe(
        take(1),
        map((x) => x.errorMessage),
        filter((x) => x === ''),
      ).subscribe(() => {
        this.responseErrors.next('JSON object is invalid');
      });
    }
  }
  handleUpdatedJson(updatedJson: string) {
    let updatedJsonJson = JSON.parse(updatedJson);

    this.flowchartJson = JSON.stringify(updatedJsonJson['source']['_value']);

    this.formatJson();
  }
}
