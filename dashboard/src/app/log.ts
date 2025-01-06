export interface LogWrapper {
    // log: Optional[Dict[str, Any]]
    // job_id: conint(gt=0)
    // created: datetime
    log: Log;
    job_id: number;
    created: Date;
}

export interface Log {
    message: string;
}