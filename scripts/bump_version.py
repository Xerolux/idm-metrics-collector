# Xerolux 2026
import sys
from pathlib import Path
import json


def update_version(new_version):
    # Read current version first
    current_version = "1.0.0"  # Default fallback
    if Path("VERSION").exists():
        current_version = Path("VERSION").read_text().strip()

    print(f"Bumping version from {current_version} to {new_version}...")

    # Update VERSION file
    Path("VERSION").write_text(new_version)
    print(f"Updated VERSION to {new_version}")

    # Update package.json
    if Path("package.json").exists():
        try:
            pkg_json = json.loads(Path("package.json").read_text())
            pkg_json["version"] = new_version
            Path("package.json").write_text(json.dumps(pkg_json, indent=2) + "\n")
            print(f"Updated package.json to {new_version}")
        except Exception as e:
            print(f"Error updating package.json: {e}")

    # Update frontend/package.json
    if Path("frontend/package.json").exists():
        try:
            fe_pkg_json = json.loads(Path("frontend/package.json").read_text())
            fe_pkg_json["version"] = new_version
            Path("frontend/package.json").write_text(
                json.dumps(fe_pkg_json, indent=2) + "\n"
            )
            print(f"Updated frontend/package.json to {new_version}")
        except Exception as e:
            print(f"Error updating frontend/package.json: {e}")

    # Update idm_logger/web.py
    if Path("idm_logger/web.py").exists():
        web_py = Path("idm_logger/web.py").read_text()
        # Replace current version string dynamically
        web_py = web_py.replace(
            f'"version": "{current_version}"', f'"version": "{new_version}"'
        )
        Path("idm_logger/web.py").write_text(web_py)
        print(f"Updated idm_logger/web.py to {new_version}")

    # Update idm_logger/update_manager.py
    if Path("idm_logger/update_manager.py").exists():
        um_py = Path("idm_logger/update_manager.py").read_text()
        um_py = um_py.replace(
            f'base_ver = "{current_version}"', f'base_ver = "{new_version}"'
        )
        Path("idm_logger/update_manager.py").write_text(um_py)
        print(f"Updated idm_logger/update_manager.py to {new_version}")

    # Update README.md
    if Path("README.md").exists():
        readme = Path("README.md").read_text()
        readme = readme.replace(f"v{current_version}", f"v{new_version}")
        readme = readme.replace(f"Version {current_version}", f"Version {new_version}")
        readme = readme.replace(
            f"Collector {current_version}", f"Collector {new_version}"
        )
        # Table update
        readme = readme.replace(f"| v{current_version} |", f"| v{new_version} |")
        readme = readme.replace(f"({current_version})", f"({new_version})")

        Path("README.md").write_text(readme)
        print(f"Updated README.md to {new_version}")

    # Update ROADMAP.md
    if Path("ROADMAP.md").exists():
        roadmap = Path("ROADMAP.md").read_text()
        roadmap = roadmap.replace(f"v{current_version}", f"v{new_version}")
        roadmap = roadmap.replace(current_version, new_version)

        Path("ROADMAP.md").write_text(roadmap)
        print(f"Updated ROADMAP.md to {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <new_version>")
        sys.exit(1)

    update_version(sys.argv[1])
