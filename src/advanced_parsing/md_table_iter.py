from markdown_it import MarkdownIt


def parse_markdown_tables(text: str):
    """
    Parse markdown tables from `text` and return a list of tables.
    Each table is a list of rows (each row is a list of cell strings).
    The first row in each table is the header. Repeated header rows
    (e.g. multipage header repeats) are skipped.
    """
    md = MarkdownIt("gfm-like")
    tokens = md.parse(text)

    current_table = None
    header = None

    # per-row / per-cell working state
    row = None
    current_cell = None
    current_cell_is_header = False
    row_header_flags = None

    def is_separator_row(cells):
        """Return True if all cells are made only of '-', ':', or spaces."""
        return all(cell.strip() and all(ch in "-: " for ch in cell.strip()) for cell in cells)


    for token in tokens:
        t = token.type

        if t == "table_open":
            current_table = []
            header = None

        elif t == "tr_open":
            row = []
            row_header_flags = []
            current_cell = None
            current_cell_is_header = False

        elif t == "th_open":
            current_cell = ""
            current_cell_is_header = True

        elif t == "td_open":
            current_cell = ""
            current_cell_is_header = False

        elif t == "inline":
            # inline text inside a cell (we only collect it when a cell is open)
            if current_cell is not None:
                # accumulate (strip to remove surrounding whitespace)
                current_cell += token.content.strip()

        elif t in ("th_close", "td_close"):
            # cell finished — append its content and whether it was a header cell
            text_cell = (current_cell or "").strip()
            row.append(text_cell)
            row_header_flags.append(bool(current_cell_is_header))
            current_cell = None

        elif t == "tr_close":
            # decide whether to treat this row as header or data
            normalized_row = tuple(c.strip() for c in row)
            if header is None:
                # first row of this table — treat as header and keep it
                header = normalized_row
                current_table.append(list(row))
            else:
                # skip rows that look like a repeated header
                if all(row_header_flags) or normalized_row == header or is_separator_row(normalized_row):
                    pass
                else:
                    current_table.append(list(row))


    return current_table