import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormControl } from '@angular/forms';

@Component({
    selector: 'app-slider',
    templateUrl: './slider.component.html',
    styleUrls: ['./slider.component.css'],
    providers: [
        {
          provide: NG_VALUE_ACCESSOR,
          useExisting: forwardRef(() => SliderComponent),
          multi: true
        }
    ]
})
export class SliderComponent implements ControlValueAccessor {
    @Input() min: number = 0;
    @Input() max: number = 100;
    @Input() stepSize: number = 0.1;
    @Input() start = 0;
  
    sliderControl = new FormControl(this.start);
  
    onChange: any = () => {};
    onTouch: any = () => {};
  
    constructor() {
      this.sliderControl.valueChanges.subscribe(value => {
        this.onChange(value);
      });
    }
  
    writeValue(value: any): void {
      this.sliderControl.setValue(value, { emitEvent: false });
    }
  
    registerOnChange(fn: any): void {
      this.onChange = fn;
    }
  
    registerOnTouched(fn: any): void {
      this.onTouch = fn;
    }
  }
  