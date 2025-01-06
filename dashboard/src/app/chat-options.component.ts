import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { BehaviorSubject } from 'rxjs';
import { ChatOptions, DEFAULT_OPTIONS } from './chat';

@Component({
  selector: 'app-chat-options',
  templateUrl: './chat-options.component.html',
  styleUrls: ['./chat-options.component.css']
})
export class ChatOptionsComponent implements OnInit {
  optionsForm: FormGroup;
  options$ = new BehaviorSubject<ChatOptions>(this.loadOptions());
  @Output() saveOptions = new EventEmitter<ChatOptions>();

  constructor(private fb: FormBuilder) {
    this.optionsForm = this.fb.group({
        model: [DEFAULT_OPTIONS.model],
        temperature: [DEFAULT_OPTIONS.temperature],
        top_p: [DEFAULT_OPTIONS.top_p],
        n: [DEFAULT_OPTIONS.n],
        max_tokens: [DEFAULT_OPTIONS.max_tokens],
        presence_penalty: [DEFAULT_OPTIONS.presence_penalty],
        frequency_penalty: [DEFAULT_OPTIONS.frequency_penalty]
    });

    this.optionsForm.valueChanges.subscribe(options => {
      localStorage.setItem('chatOptions', JSON.stringify(options));
      this.options$.next(options);
    });
  }

  ngOnInit(): void {
    this.optionsForm.patchValue(this.loadOptions());
  }

  private loadOptions(): ChatOptions {
    const options = localStorage.getItem('chatOptions');
    return options ? JSON.parse(options) : {};
  }

  onSave() {
    this.saveOptions.emit(this.optionsForm.value);
  }
}
