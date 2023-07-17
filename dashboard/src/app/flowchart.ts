import { PFNode } from './node';
import { Branch } from './branch';

export interface Flowchart {
    id: string;
    name: string;
    nodes: PFNode[];
    branches: Branch[];
    status: string;
    created_at: string;
    updated_at: string;
}

export interface FlowchartConfirmation {
    message: string;
    task_id: string;
}