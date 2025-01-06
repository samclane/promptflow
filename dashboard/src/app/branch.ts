import { PFNode } from './node';

export interface Branch {
    id: string;
    label: string;
    prev: PFNode;
    next: PFNode;
    conditional: string;
}