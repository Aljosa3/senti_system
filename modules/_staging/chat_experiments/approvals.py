import os

MODULE_STRUCTURES = {
    "trading_intel": {
        "base": "modules/trading_intel",
        "files": [
            "__init__.py",
            "README.md",
            "strategies/ema_rsi.md",
            "indicators/macd.md",
            "scenarios/range_market.md",
        ]
    },
    "notes": {
        "base": "modules/notes",
        "files": [
            "__init__.py",
            "README.md",
            "topics/trading.md",
            "topics/research.md",
            "topics/ideas.md",
        ]
    }
}


def approve_module(module_name: str) -> dict:
    if module_name not in MODULE_STRUCTURES:
        return {"error": "Unknown module proposal"}

    structure = MODULE_STRUCTURES[module_name]
    base_path = structure["base"]

    if os.path.exists(base_path):
        return {"error": f"Module directory already exists: {base_path}"}

    created_paths = []

    try:
        os.makedirs(base_path, exist_ok=False)
        created_paths.append(base_path + "/")

        for file_path in structure["files"]:
            full_path = os.path.join(base_path, file_path)
            dir_name = os.path.dirname(full_path)

            if dir_name and dir_name != base_path:
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=False)
                    created_paths.append(dir_name + "/")

            with open(full_path, "x") as f:
                pass

            created_paths.append(full_path)

        return {
            "approved": True,
            "module": module_name,
            "created_paths": created_paths
        }

    except FileExistsError as e:
        return {"error": f"File or directory already exists: {e}"}
    except Exception as e:
        return {"error": f"Failed to create module: {e}"}
