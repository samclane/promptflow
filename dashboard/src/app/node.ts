export interface PFNode {
    id: string;
    name: string;
    type: string;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface NodeTypes { 
    node_types: string[];
}