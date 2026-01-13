import os
import sys

# Add local path to sys.path
sys.path.insert(0, os.getcwd())

try:
    print("Importing WorkflowService...")
    from Income_Statement_App.services.workflow_service import WorkflowService

    print("WorkflowService imported successfully.")

    print("Importing AliasRepository...")
    from Income_Statement_App.data.repositories.alias_repository import AliasRepository

    print("AliasRepository imported successfully.")

except ImportError as e:
    print(f"ImportError: {e}")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
