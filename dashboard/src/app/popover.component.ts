import { Component, Input, Output, EventEmitter } from '@angular/core';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-popover',
    templateUrl: './popover.component.html',
})
export class PopoverComponent {
  showPopover$ = new Subject<boolean>();

  @Input() title: string = 'Confirm';
  @Input() message: string | null = 'Are you sure you want to do this?';
  @Input() confirmText: string = 'Confirm';
  @Input() cancelText: string = 'Cancel';

  @Output() confirmation = new EventEmitter<boolean>();

  openPopover() {
    this.showPopover$.next(true);
  }

  confirm() {
    this.confirmation.emit(true);
    this.showPopover$.next(false);
  }

  cancel() {
    this.confirmation.emit(false);
    this.showPopover$.next(false);
  }
}
