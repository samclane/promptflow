export interface Job {
    job_id: number;
    job_status: string;
    status: string;
    created: string;
    updated: string; 
    metadata: object;
    graph_id: number;
    graph_uid: string;
}

export interface JobLog {
    job_id: string;
    job_status: string;
}