from dataclasses import dataclass


from income_statement_app.common.types import PathLike


@dataclass
class FileSource:
    """
    Represents a unified source for a file, abstracting away the difference
    between a local file path (Native) and an in-memory/uploaded file (Web).
    """

    # For Native: The absolute path to the file
    path: PathLike | None = None

    # For Web: The unique ID or token referencing the uploaded temp file
    # (Infrastructure layer knows how to resolve this ID to a real file or bytes)
    upload_id: str | None = None

    # Optional: Original filename for display purposes
    filename: str = "unknown.xlsx"

    @property
    def is_local(self) -> bool:
        return self.path is not None

    def __str__(self):
        if self.path:
            return f"LocalFile({self.path})"
        return f"UploadedFile({self.upload_id})"
