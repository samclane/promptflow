import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-chat-options-popover',
  templateUrl: './chat-options-popover.component.html',
  styleUrls: ['./chat-options-popover.component.css']
})
export class ChatOptionsPopoverComponent {
  @Output() close = new EventEmitter<void>();

  onClose() {
    this.close.emit();
  }
}
