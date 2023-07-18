export interface Job {
    job_id: number;
    job_status: string;
    status: string;
    created: string;
    updated: string; 
    metadata: Object;
    graph_id: number;
}

export interface JobLog {
    job_id: string;
    job_status: string;
}