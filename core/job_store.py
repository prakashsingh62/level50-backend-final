import os

class JobStore:
    def create_job(self, *args, **kwargs):
        return True

    def update_job(self, *args, **kwargs):
        # Yahan humne absolute import use kiya hai taaki ModuleNotFoundError na aaye
        try:
            from google_sheets import sheet_manager
        except ImportError:
            try:
                from core.google_sheets import sheet_manager
            except:
                return False
        
        trace_id = kwargs.get('job_id') or kwargs.get('trace_id')
        status = kwargs.get('status', 'UNKNOWN')
        result = kwargs.get('result', {})

        if trace_id:
            try:
                sheet_manager.append_audit_log(
                    trace_id=trace_id,
                    status=status,
                    details=str(result)
                )
            except:
                pass
        return True

job_store = JobStore()
