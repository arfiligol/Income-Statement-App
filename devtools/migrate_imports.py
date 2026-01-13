import os

TARGET_DIR = "Income_Statement_App"


def migrate_imports():
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = content.replace("from src.", "from Income_Statement_App.")
                new_content = new_content.replace(
                    "import src.", "import Income_Statement_App."
                )

                if new_content != content:
                    print(f"Updating {path}")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)


if __name__ == "__main__":
    migrate_imports()
