import timeit
import random

data = []
for _ in range(50):
    measurement = {}
    for i in range(100):
        if i % 10 == 0:
            measurement[f"key_{i}_str"] = "string_value"
        elif i % 2 == 0:
            measurement[f"key_{i}"] = random.choice([True, False])
        else:
            measurement[f"key_{i}"] = random.random() * 100
    data.append(measurement)

def original_send_data(data):
    items = data
    lines = []
    tags = ",installation_id=test,model=test,manufacturer=test"

    for measurements in items:
        fields = []
        for key, value in measurements.items():
            if key.endswith("_str"):
                continue
            if isinstance(value, bool):
                value = int(value)
            if isinstance(value, (int, float)):
                fields.append(f"{key}={value}")

        if fields:
            field_str = ",".join(fields)
            lines.append(f"idm_heatpump{tags} {field_str}")
    return lines

def optimized_send_data(data):
    items = data
    lines = []
    tags = ",installation_id=test,model=test,manufacturer=test"
    prefix = f"idm_heatpump{tags} "

    for measurements in items:
        fields = []
        for key, value in measurements.items():
            if key.endswith("_str"):
                continue
            if isinstance(value, bool):
                fields.append(f"{key}={1 if value else 0}")
            elif isinstance(value, (int, float)):
                fields.append(f"{key}={value}")

        if fields:
            field_str = ",".join(fields)
            lines.append(f"{prefix}{field_str}")
    return lines

orig_time = timeit.timeit(lambda: original_send_data(data), number=1000)
opt_time = timeit.timeit(lambda: optimized_send_data(data), number=1000)

print(f"Original: {orig_time:.4f}s")
print(f"Optimized: {opt_time:.4f}s")
print(f"Improvement: {(orig_time - opt_time) / orig_time * 100:.2f}%")
