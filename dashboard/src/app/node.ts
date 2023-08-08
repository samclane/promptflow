export interface PFNode {
    id: string;
    label: string;
    type: string;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface NodeType {
    name: string;
    description: string;
    options: string[];
}

export interface NodeTypes { 
    node_types: NodeType[];
}