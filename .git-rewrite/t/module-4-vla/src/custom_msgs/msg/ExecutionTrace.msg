# Complete execution record of a task plan
# Records actual outcomes, latencies, and debugging information

string id                           # Unique trace identifier (UUID)
string plan_id                      # Reference to executed TaskPlan
builtin_interfaces/Time start_timestamp   # When execution started
builtin_interfaces/Time end_timestamp     # When execution completed
float64 total_duration_seconds      # Actual execution time
custom_msgs/ExecutedStep[] executed_steps # Results for each step
float64 success_rate                # Percentage of steps successful (0.0-1.0)
string failure_reason               # If failed, why (empty if success)
int32 safety_incidents              # Count of collisions or safety violations
string[] logs                       # Debug/diagnostic logs with timestamps
