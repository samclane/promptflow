import { PFNode } from './node';
import { Branch } from './branch';

export interface Flowchart {
    uid: string;
    label: string;
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

export interface FlowchartJSResponse {
    flowchart_js: string;
}