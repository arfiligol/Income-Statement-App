# Lawyer Code Aliases (Connected Lawyers)

To support scenarios where a single lawyer code represents a group of lawyers or a specific distribution, users can define "Connected Lawyer Codes" (aliases).

## Feature Description

Users can define a mapping where a **Source Code** is automatically associated with a list of **Target Codes**.

-   **Source Code**: The partial or primary code (e.g., "KW").
-   **Target Codes**: The full list of codes to be used (e.g., "KW, JH, JL").

## Workflow Integration

### Auto Fill Lawyer Codes
When the "Auto Fill" workflow processes a row:
1.  It identifies a potential code (e.g., finds "KW" in Summary, or user selects "KW").
2.  The system checks if this code is a "Source Code" in the Alias database.
3.  **If a match is found**: The system automatically replaces the found code with the defined **Target Codes** in the "Remark" column.
4.  **If no match**: The single code is used as is.

### Database Operations
A new management interface is provided in the **Database Page** to:
-   **View** all defined aliases.
-   **Add** a new alias (Source -> Targets).
-   **Edit** existing aliases.
-   **Delete** aliases.

## Data Model

-   **Alias/Connected Code**:
    -   `source_code` (Unique, Primary Key): e.g., "KW"
    -   `target_codes` (Text): e.g., "KW, JH, JL" (stored as comma-separated string or related entities)

## Validation Rules
-   `source_code` must be unique.
-   `target_codes` cannot be empty.
