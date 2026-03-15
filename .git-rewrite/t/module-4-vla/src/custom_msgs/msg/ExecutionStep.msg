# Single action step within a task plan
# Represents one actionable step (navigate, perceive, manipulate, request_clarification)

int32 step_index                    # Order in execution (1-indexed)
string action_type                  # One of: navigate, perceive, manipulate, request_clarification
string parameters_json              # JSON object with action-specific parameters
string expected_outcome             # What success looks like
int32 timeout_seconds               # Max time to wait (default: 30)
