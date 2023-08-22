import { Component, Input } from '@angular/core';
import { FormControl } from '@angular/forms';
import { debounceTime } from 'rxjs/operators';

@Component({
  selector: 'app-slider',
  templateUrl: './slider.component.html',
  styleUrls: ['./slider.component.css']
})
export class SliderComponent {
    @Input() min: number = 0;
    @Input() max: number = 100;
    @Input() start: number = 50;
    sliderControl = new FormControl(this.start);
    
  constructor() {
    this.sliderControl.valueChanges.pipe(
      debounceTime(300)
    ).subscribe(value => {
      console.log("Slider Value:", value);
    });
  }
}
