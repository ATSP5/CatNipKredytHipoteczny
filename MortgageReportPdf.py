import math
from pathlib import Path
from typing import List, Sequence

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from MortgageReportSnapshot import MortgageReportSnapshot
from PlnFormat import PlnFormat
from ReportTable import ReportTable


class MortgageReportPdf:
    """Zapisuje analizę kredytu hipotecznego jako nowy plik PDF w folderze output projektu."""

    PAGE_SIZE = (8.27, 11.69)                   # A4 w calach
    LEFT, WIDTH, TOP, BOTTOM = 0.08, 0.84, 0.905, 0.06
    ROW_HEIGHT = 0.0175
    ACCENT, TEXT, MUTED, STRIPE = "#1f4e8c", "#1d2433", "#6b7585", "#eef2f8"
    KIND_COLORS = {"ok": "#1e8449", "warning": "#b9770e", "error": "#c0392b"}
    SERIES = ["#3366cc", "#ff9900", "#9aa5b1", "#109618"]

    def __init__(self, snapshot: object, formatter: PlnFormat, output_dir: str = "output"):
        # Przy błędnych parametrach strona nie tworzy migawki i akcja przekazuje sam stan strony.
        self.snapshot = snapshot if isinstance(snapshot, MortgageReportSnapshot) else None
        self.formatter = formatter
        self.output_dir = output_dir
        self._pages: List[Figure] = []
        self._top = 0.0

    def pdf_path(self) -> str:
        """Tworzy PDF i zwraca jego ścieżkę; bez migawki (błędne parametry) niczego nie zapisuje."""
        if self.snapshot is None:
            return ""
        self._pages = []
        self._summary()
        for table in self.snapshot.tables[:-1]:          # krótkie tabele pod wskaźnikami i na stronie 2
            self._flow_table(table)
        self._charts()
        self._flow_table(self.snapshot.tables[-1])       # harmonogram — na końcu, na wielu stronach
        path = self._new_file_path()
        with PdfPages(path) as pdf:
            for number, figure in enumerate(self._pages, start=1):
                self._footer(figure, number, len(self._pages))
                pdf.savefig(figure)
            info = pdf.infodict()
            info["Title"] = self.snapshot.title
            info["CreationDate"] = self.snapshot.created_at
        print("[Zapis PDF] zapisano %s (%d stron)" % (path, len(self._pages)), flush=True)
        return str(path)

    # ── Plik ──────────────────────────────────────────────────────────────────

    def _new_file_path(self) -> Path:
        folder = Path(self.output_dir)
        if not folder.is_absolute():
            folder = self._project_folder() / folder
        folder.mkdir(parents=True, exist_ok=True)
        stamp = self.snapshot.created_at.strftime("%Y-%m-%d_%H%M%S")
        path, copy = folder / ("kredyt_hipoteczny_%s.pdf" % stamp), 2
        while path.exists():
            path, copy = folder / ("kredyt_hipoteczny_%s_%d.pdf" % (stamp, copy)), copy + 1
        return path

    @staticmethod
    def _project_folder() -> Path:
        here = Path(__file__).resolve().parent
        for folder in (Path.cwd(), here, here.parent):
            if any(folder.glob("*.catnip")):
                return folder
        return Path.cwd()

    # ── Strony ────────────────────────────────────────────────────────────────

    def _new_page(self) -> Figure:
        figure = Figure(figsize=self.PAGE_SIZE)
        figure.text(self.LEFT, 0.955, self.snapshot.title, fontsize=14, fontweight="bold", color=self.ACCENT)
        figure.text(self.LEFT, 0.937, "Wygenerowano " + self.snapshot.created_at.strftime("%d.%m.%Y, godz. %H:%M"),
                    fontsize=8.5, color=self.MUTED)
        figure.add_artist(Rectangle((self.LEFT, 0.928), self.WIDTH, 0.0012, color=self.ACCENT,
                                    transform=figure.transFigure))
        self._pages.append(figure)
        self._top = self.TOP
        return figure

    def _footer(self, figure: Figure, number: int, total: int) -> None:
        figure.text(self.LEFT, 0.03, "Ocena zdolności według uproszczonych reguł KNF; oferty banków orientacyjne.",
                    fontsize=6.5, color=self.MUTED)
        figure.text(self.LEFT + self.WIDTH, 0.03, "strona %d / %d" % (number, total), fontsize=7,
                    color=self.MUTED, ha="right")

    def _summary(self) -> None:
        figure = self._new_page()
        for text, kind in self.snapshot.messages:
            for line in self._wrap(("✔ " if kind == "ok" else "⚠ ") + text, 110):
                figure.text(self.LEFT, self._top, line, fontsize=8, color=self.KIND_COLORS.get(kind, self.TEXT))
                self._top -= 0.016
            self._top -= 0.004
        self._top -= 0.01
        self._kpi_grid(figure)
        self._top -= 0.02
        for note in self.snapshot.notes:
            for line in self._wrap(note, 130):
                figure.text(self.LEFT, self._top, line, fontsize=7, color=self.MUTED)
                self._top -= 0.014

    def _kpi_grid(self, figure: Figure) -> None:
        columns, height, gap = 2, 0.058, 0.008
        width = (self.WIDTH - gap) / columns
        for index, (label, value, note, bad) in enumerate(self.snapshot.kpis):
            row, column = divmod(index, columns)
            left = self.LEFT + column * (width + gap)
            bottom = self._top - (row + 1) * height - row * gap
            color = self.KIND_COLORS["error"] if bad else self.TEXT
            figure.add_artist(Rectangle((left, bottom), width, height, facecolor=self.STRIPE,
                                        edgecolor=color if bad else "#d0d7e2", linewidth=0.8,
                                        transform=figure.transFigure))
            figure.text(left + 0.01, bottom + height - 0.015, label, fontsize=7.5, color=self.MUTED)
            figure.text(left + 0.01, bottom + 0.022, value, fontsize=12.5, fontweight="bold", color=color)
            figure.text(left + 0.01, bottom + 0.008, note, fontsize=6.5, color=self.MUTED)
        rows = math.ceil(len(self.snapshot.kpis) / columns)
        self._top -= rows * (height + gap)

    def _charts(self) -> None:
        figure = self._new_page()
        self._heading(figure, "Spłaty w kolejnych latach i saldo zadłużenia")
        self._yearly_chart(figure, [self.LEFT + 0.05, self._top - 0.36, self.WIDTH - 0.12, 0.34])
        self._top -= 0.45
        self._heading(figure, "Struktura całkowitego kosztu")
        self._cost_donut(figure)

    def _flow_table(self, table: ReportTable) -> None:
        """Tabela pod poprzednią treścią; nie mieści się — ciąg dalszy na nowej stronie z nagłówkiem."""
        rows = list(table.rows)
        title = table.title
        figure = self._pages[-1]
        full_page = int((self.TOP - 0.04 - self.BOTTOM) / self.ROW_HEIGHT) - 1
        while rows:
            space = int((self._top - 0.04 - self.BOTTOM) / self.ROW_HEIGHT) - 1
            # Krótka tabela, która zmieściłaby się na pustej stronie, nie jest dzielona.
            if space < len(rows) and (len(rows) <= full_page or space < 4):
                figure = self._new_page()
                continue
            self._heading(figure, title)
            chunk, rows = rows[:space], rows[space:]
            self._table(figure, table.header, chunk, table.widths or [1.0] * len(table.header),
                        set(table.right_columns))
            self._top -= 0.02
            title = table.title + " (cd.)"

    # ── Elementy strony ───────────────────────────────────────────────────────

    def _heading(self, figure: Figure, text: str) -> None:
        figure.text(self.LEFT, self._top - 0.012, text, fontsize=11, fontweight="bold", color=self.TEXT)
        self._top -= 0.025

    def _table(self, figure: Figure, header: Sequence[str], rows: Sequence[Sequence[str]],
               widths: Sequence[float], right: set, font: float = 7.5) -> None:
        count = len(rows) + 1
        axes = figure.add_axes([self.LEFT, self._top - count * self.ROW_HEIGHT, self.WIDTH, count * self.ROW_HEIGHT])
        axes.set_xlim(0, 1)
        axes.set_ylim(count, 0)
        axes.axis("off")
        edges = [0.0]
        for width in widths:
            edges.append(edges[-1] + width / sum(widths))
        for r, cells in enumerate([list(header)] + [list(row) for row in rows]):
            if r == 0:
                axes.add_patch(Rectangle((0, 0), 1, 1, color=self.ACCENT))
            elif r % 2 == 0:
                axes.add_patch(Rectangle((0, r), 1, 1, color=self.STRIPE))
            for c, text in enumerate(cells):
                aligned_right = c in right
                x = edges[c + 1] - 0.006 if aligned_right else edges[c] + 0.006
                axes.text(x, r + 0.55, str(text), ha="right" if aligned_right else "left", va="center",
                          fontsize=font, color="white" if r == 0 else self.TEXT,
                          fontweight="bold" if r == 0 else "normal")
        self._top -= count * self.ROW_HEIGHT

    def _yearly_chart(self, figure: Figure, rect: List[float]) -> None:
        years = self.snapshot.schedule.yearly()
        x = [y[0] for y in years]
        principal, interest, insurance = [y[1] for y in years], [y[2] for y in years], [y[3] for y in years]
        axes = figure.add_axes(rect)
        axes.bar(x, principal, color=self.SERIES[0], label="Kapitał")
        axes.bar(x, interest, bottom=principal, color=self.SERIES[1], label="Odsetki")
        axes.bar(x, insurance, bottom=[p + i for p, i in zip(principal, interest)], color=self.SERIES[2],
                 label="Ubezpieczenie")
        axes.set_xlabel("rok kredytu", fontsize=8)
        axes.set_ylabel("spłaty w roku [zł]", fontsize=8)
        balance = axes.twinx()
        balance.plot(x, [y[4] for y in years], color=self.SERIES[3], linewidth=1.8, label="Saldo na koniec roku")
        balance.set_ylabel("saldo [zł]", fontsize=8)
        for side in (axes, balance):
            side.tick_params(labelsize=7)
            side.yaxis.set_major_formatter(lambda value, _: self.formatter.num(value, 0))
            side.spines["top"].set_visible(False)
        handles = axes.get_legend_handles_labels()[0] + balance.get_legend_handles_labels()[0]
        axes.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, fontsize=7,
                    frameon=False)

    def _cost_donut(self, figure: Figure) -> None:
        s = self.snapshot.schedule
        parts = [("Odsetki", s.total_interest), ("Ubezpieczenie nieruchomości", s.total_insurance),
                 ("Prowizja", s.parameters.commission)]
        parts = [(name, value) for name, value in parts if value > 0]
        top = self._top
        axes = figure.add_axes([self.LEFT, top - 0.34, 0.45, 0.32])
        axes.pie([value for _, value in parts], colors=[self.SERIES[1], self.SERIES[2], self.SERIES[0]][:len(parts)],
                 startangle=90, counterclock=False, wedgeprops={"width": 0.42, "edgecolor": "white"})
        axes.text(0, 0, self.formatter.zl(s.total_cost), ha="center", va="center", fontsize=10, fontweight="bold",
                  color=self.TEXT)
        total = sum(value for _, value in parts) or 1.0
        colors = [self.SERIES[1], self.SERIES[2], self.SERIES[0]]
        for index, (name, value) in enumerate(parts):
            y = top - 0.12 - index * 0.03
            figure.add_artist(Rectangle((0.58, y), 0.015, 0.012, color=colors[index], transform=figure.transFigure))
            figure.text(0.605, y + 0.002, "%s: %s (%s)" % (name, self.formatter.zl(value), self.formatter.pct(value / total * 100, 1)),
                        fontsize=8, color=self.TEXT)
        below = top - 0.12 - len(parts) * 0.03 - 0.01
        figure.text(0.58, below, "Kwota kredytu: %s" % self.formatter.zl(s.parameters.amount), fontsize=7.5, color=self.MUTED)
        figure.text(0.58, below - 0.018, "Do zapłaty razem: %s" % self.formatter.zl(s.total_to_pay), fontsize=7.5,
                    color=self.MUTED)
        self._top = top - 0.36

    @staticmethod
    def _wrap(text: str, width: int) -> List[str]:
        lines, current = [], ""
        for word in text.split():
            if current and len(current) + 1 + len(word) > width:
                lines.append(current)
                current = word
            else:
                current = (current + " " + word).strip()
        return lines + ([current] if current else [])
