import sys
import os

# Path fix taaki 'core' folder mil jaye
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class JobStore:
    def create_job(self, *args, **kwargs): return True
    def update_job(self, *args, **kwargs):
        try:
            # Direct import from the current folder
            import google_sheets
            from google_sheets import sheet_manager
            
            t_id = kwargs.get('job_id') or kwargs.get('trace_id')
            if t_id:
                sheet_manager.append_audit_log(
                    trace_id=t_id,
                    status=kwargs.get('status', 'UPDATE'),
                    details=str(kwargs.get('result', {}))
                )
        except Exception as e:
            print(f"Audit Error: {e}")
        return True

job_store = JobStore()
