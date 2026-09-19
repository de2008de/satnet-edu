"""Initial contract guard; expanded at M2 with JSON schema and path checks."""
def validate_trace(data):
    if data.get("format") != "satnet-edu.trace" or data.get("schema_version") != "1.0.0":
        raise ValueError("trace: expected satnet-edu.trace version 1.0.0")
    if not data.get("frames"):
        raise ValueError("frames: expected at least one sample")
    return data
