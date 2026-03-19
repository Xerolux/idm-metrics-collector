import re
with open("tests/test_ml_pooling.py", "r") as f:
    text = f.read()

# Ruff complains about E402 module level import not at top of file
# for `import ml_service.main as main`

# We can tell ruff to ignore it:
text = text.replace("import ml_service.main as main", "import ml_service.main as main  # noqa: E402")

with open("tests/test_ml_pooling.py", "w") as f:
    f.write(text)
