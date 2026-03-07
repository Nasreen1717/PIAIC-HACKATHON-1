# Result record for a single executed step
# Nested within ExecutionTrace to record actual outcome vs expected

int32 step_index                    # Which step in the plan
string action_type                  # Type of action executed
string status                       # One of: SUCCESS, FAILED, TIMEOUT, SKIPPED
float64 actual_duration_seconds     # How long it actually took
string outcome                      # What actually happened (vs expected)
string error_message                # If failed, error details (empty if success)
