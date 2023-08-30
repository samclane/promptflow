import { Component, ChangeDetectionStrategy, Input, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
import { trigger, transition, style, animate, state } from '@angular/animations';
import { BehaviorSubject } from 'rxjs';

@Component({
    selector: 'app-flowchart-tree',
    templateUrl: './flowchart-tree.component.html',
    styleUrls: ['./flowchart-tree.component.css'],
    animations: [
        trigger('slideInOut', [
            state('in', style({ height: '*', opacity: 1, overflow: 'hidden' })),
            transition(':enter', [
              style({ height: '0', opacity: 0, overflow: 'hidden' }),
              animate('200ms ease-in', style({ height: '*', opacity: 1, overflow: 'hidden' }))
            ]),
            transition(':leave', [
              style({ height: '*', opacity: 1, overflow: 'hidden' }),
              animate('200ms ease-in', style({ height: '0', opacity: 0, overflow: 'hidden' }))
            ])
          ])
          
    ],   
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class FlowchartTreeComponent implements OnChanges {
    @Input() treeData: string | undefined | null;
    @Output() updatedJson = new EventEmitter<string>();
    parsedJson: any;
    constructor() { }
    private _vm$ = new BehaviorSubject<any>(null);
    public readonly vm$ = this._vm$.asObservable();

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
    isObject(value: any): boolean {
        return typeof value === 'object';
    }

    parseJson(value: string): any {
        try {
            return JSON.parse(value);
        } catch (e) {
            return '';
        }
    }
}


