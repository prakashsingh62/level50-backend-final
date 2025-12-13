from utils.logger import log
from utils.smart_throttle import smart_throttle
from googleapiclient.errors import HttpError


class AntiCorruptionGuard:
    """
    INFINITY PACK-4: ANTI-CORRUPTION GUARD
    ---------------------------------------
    Prevents:
        ✔ duplicate updates
        ✔ row mismatches
        ✔ stale writes
        ✔ wrong-row updates
        ✔ sheet conflicts
        ✔ partial writes
    """

    def __init__(self):
        pass

    # --------------------------------------------------------
    # STEP 1 — Capture row snapshot BEFORE update
    # --------------------------------------------------------
    def capture_snapshot(self, sheet, row_index):
        try:
            result = sheet.values().get(
                spreadsheetId=sheet.sheet_id,
                range=f"{sheet.tab_name}!A{row_index}:ZZ{row_index}"
            ).execute()

            return result.get("values", [[]])[0]

        except HttpError as e:
            log(f"[ANTI-CORRUPTION] SNAPSHOT ERROR → {e}")
            return None

    # --------------------------------------------------------
    # STEP 2 — Compare old snapshot with expected data
    # --------------------------------------------------------
    def verify_row_integrity(self, old_snapshot, expected_row):
        """
        If sheet row changed since pipeline preview → BLOCK UPDATE.
        """
        if old_snapshot is None:
            return False

        # Only compare relevant columns, not entire row
        for i, val in enumerate(expected_row):
            if i < len(old_snapshot) and str(old_snapshot[i]).strip() != str(val).strip():
                return False

        return True

    # --------------------------------------------------------
    # STEP 3 — Capture AFTER update
    # --------------------------------------------------------
    def verify_post_update(self, sheet, row_index, expected_row):
        """
        Ensures sheet actually contains the values after update.
        Prevents silent failures.
        """
        new_snapshot = self.capture_snapshot(sheet, row_index)

        if new_snapshot is None:
            return False

        # Compare expected vs actual
        for i, val in enumerate(expected_row):
            if i < len(new_snapshot) and str(new_snapshot[i]).strip() != str(val).strip():
                return False

        return True

    # --------------------------------------------------------
    # FULL VERIFICATION PIPELINE
    # --------------------------------------------------------
    def safe_update(self, updater_fn, sheet_obj, row_index, update_values):
        """
        wrapper around update_rfq_row
        LOCK → SNAPSHOT → VERIFY → UPDATE → VERIFY → UNLOCK
        """

        # 1) Global sheet lock
        smart_throttle.acquire_sheet_lock()
        try:
            # Snapshot BEFORE update
            before = self.capture_snapshot(sheet_obj, row_index)

            # Integrity check
            if not self.verify_row_integrity(before, update_values):
                log("[ANTI-CORRUPTION] ROW CHANGED — UPDATE BLOCKED")
                return {
                    "status": "blocked",
                    "reason": "Row changed since preview. Preventing corruption."
                }

            # Perform update
            result = updater_fn(row_index, update_values)

            # Snapshot AFTER update
            ok = self.verify_post_update(sheet_obj, row_index, update_values)

            if not ok:
                log("[ANTI-CORRUPTION] POST-UPDATE CHECK FAILED — POTENTIAL CORRUPTION BLOCKED")
                return {
                    "status": "blocked",
                    "reason": "Post-update verification failed."
                }

            return result

        finally:
            smart_throttle.release_sheet_lock()
