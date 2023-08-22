import { Component } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-toggle-slider',
  templateUrl: './toggle-slider.component.html',
  styleUrls: ['./toggle-slider.component.css']
})
export class ToggleSliderComponent {
  isToggled: BehaviorSubject<boolean> = new BehaviorSubject(false);

  toggle() {
    this.isToggled.next(!this.isToggled.value);
  }
}
