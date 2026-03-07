# Decomposed task plan from LLM
# Represents a high-level goal broken into actionable steps

string id                           # Unique plan identifier (UUID)
builtin_interfaces/Time timestamp   # When plan was generated
string voice_command_id             # Reference to originating VoiceCommand
string goal                         # High-level goal from user
custom_msgs/ExecutionStep[] steps   # Ordered steps to execute
string metadata_json                # LLM reasoning, alternatives, confidence (JSON)
float64 estimated_duration_seconds  # Predicted execution time
