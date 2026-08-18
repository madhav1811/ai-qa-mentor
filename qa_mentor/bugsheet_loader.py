"""Loads a bug-sheet-only spreadsheet (no accompanying documentation) into a
flat list of bug records. Used by analyze_bugsheet.py for the mode where
there's real bug history but no written docs to run Stage 1-2 against.
"""
import openpyxl


def load_bug_rows(
    xlsx_path: str,
    sheet_name: str = None,
    summary_col: str = "Bug Summary",
    path_col: str = "Path",
    reported_by_col: str = "Reported by",
    status_col: str = "Status",
) -> list:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() if h else "" for h in rows[0]]

    def col_index(name):
        return header.index(name) if name in header else None

    idx = {
        "summary": col_index(summary_col),
        "path": col_index(path_col),
        "reported_by": col_index(reported_by_col),
        "status": col_index(status_col),
    }

    bugs = []
    for r in rows[1:]:
        summary = r[idx["summary"]] if idx["summary"] is not None else None
        if not summary or not str(summary).strip():
            continue

        path = r[idx["path"]] if idx["path"] is not None else None
        reported_by = r[idx["reported_by"]] if idx["reported_by"] is not None else None
        status = r[idx["status"]] if idx["status"] is not None else None

        path = str(path).strip() if path else ""
        section = path.split(">")[0].strip() if path else "uncategorized"

        bugs.append(
            {
                "summary": str(summary).strip(),
                "path": path,
                "section": section,
                "reported_by": str(reported_by).strip() if reported_by else "unknown",
                "status": str(status).strip() if status else "",
            }
        )
    return bugs
