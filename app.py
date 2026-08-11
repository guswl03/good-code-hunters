from __future__ import annotations

from goodcode.core.service import scan_file
from goodcode.gui.main_window import MainWindow


def main() -> None:
    app = MainWindow(scan_service=scan_file)
    app.mainloop()


if __name__ == "__main__":
    main()
