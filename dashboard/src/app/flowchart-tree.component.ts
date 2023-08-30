import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, OnInit, Output, EventEmitter } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: 'app-flowchart-tree',
    templateUrl: './flowchart-tree.component.html',
    styleUrls: ['./flowchart-tree.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartTreeComponent implements OnInit, OnChanges {
  @Input() treeData: string | undefined | null;
  @Output() updatedJson = new EventEmitter<string>();
  parsedJson: any;
  constructor() {}
  private _vm$ = new BehaviorSubject<any>(null);
  public readonly vm$ = this._vm$.asObservable();

  ngOnInit() {
    console.log('Component initialized');
  }
  ngOnChanges(changes: SimpleChanges): void {
    console.log('Component changed');
    if (changes['treeData'] && changes['treeData'].currentValue) {
      this.parsedJson = JSON.parse(this.treeData as string);
      this._vm$.next(this.parsedJson);
    }
  }
  objectKeys(obj: any): string[] {
    return Object.keys(obj);
  }
  safeStringify(obj: any, cache = new Set()): string | null {
    return JSON.stringify(obj, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (cache.has(value)) {
          // Remove cyclic reference
          return;
        }
        cache.add(value);
      }
      return value;
    });
  }  
  emitChange() {
    this.updatedJson.emit(this.safeStringify(this.vm$) as string);
  }
}


