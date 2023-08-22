import { Component } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-toggle-button',
  templateUrl: './toggle-button.component.html',
  styleUrls: ['./toggle-button.component.css']
})
export class ToggleButtonComponent {
  isToggled: BehaviorSubject<boolean> = new BehaviorSubject(false);

  toggle() {
    this.isToggled.next(!this.isToggled.value);
  }
}
