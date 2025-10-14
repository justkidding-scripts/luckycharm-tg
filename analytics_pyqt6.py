#!/usr/bin/env python3
"""
PyQt6 Analytics Dashboard (standalone window)
- Uses PyQt6 for graphics; prefers pyqtgraph, falls back to QtCharts, otherwise shows textual stats.
- Reads from telegram_automation.db to display live metrics for scrape/invite/message operations.
"""
import sys
import os
import sqlite3
import math
from datetime import datetime, timedelta

# Prefer pyqtgraph for high FPS plots
USE_PG = False
try:
    import pyqtgraph as pg  # type: ignore
    USE_PG = True
except Exception:
    USE_PG = False

from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMessageBox, QGridLayout
)

# Optional QtCharts fallback
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    HAVE_CHARTS = True
except Exception:
    HAVE_CHARTS = False

DB_PATH = os.path.join(os.path.dirname(__file__), 'telegram_automation.db')

class AnalyticsData:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # ensure db exists
        if not os.path.exists(self.db_path):
            # create empty file to avoid errors; charts will show no data
            open(self.db_path, 'a').close()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def metrics_last_minutes(self, minutes: int = 60):
        """Return counts per minute for operations within last N minutes."""
        end = datetime.now()
        start = end - timedelta(minutes=minutes)
        rows = []
        try:
            with self._conn() as conn:
                cur = conn.cursor()
                # account_usage has (session_name, date, operation_type, count). Not timestamped per event.
                # We use operation_states.last_checkpoint as a proxy for recent work, plus scraped_members.scraped_at.
                cur.execute("""
                    SELECT started_at, operation_type, completed_items, failed_items
                    FROM operation_states
                    WHERE started_at >= ?
                """, (start.isoformat(),))
                rows = cur.fetchall()
        except Exception:
            pass
        return rows

    def scraped_series(self, minutes: int = 120):
        """Return timestamps of scraped members for last N minutes."""
        end = datetime.now()
        start = end - timedelta(minutes=minutes)
        stamps = []
        try:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT scraped_at FROM scraped_members WHERE scraped_at >= ? ORDER BY scraped_at ASC",
                    (start.isoformat(),)
                )
                stamps = [datetime.fromisoformat(r[0]) for r in cur.fetchall() if r and r[0]]
        except Exception:
            pass
        return stamps

    def totals(self):
        """Total rows and success/failure from operation_states."""
        totals = {
            'operations': 0,
            'completed': 0,
            'failed': 0,
            'scraped_members': 0,
        }
        try:
            with self._conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM operation_states")
                totals['operations'] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM operation_states WHERE status='completed'")
                totals['completed'] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM operation_states WHERE status='failed'")
                totals['failed'] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM scraped_members")
                totals['scraped_members'] = cur.fetchone()[0]
        except Exception:
            pass
        return totals

class AnalyticsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Analytics Dashboard")
        self.resize(960, 600)
        self.data = AnalyticsData(DB_PATH)

        root = QWidget(self)
        self.setCentralWidget(root)
        self.vbox = QVBoxLayout(root)
        root.setLayout(self.vbox)

        # Header
        header = QHBoxLayout()
        title = QLabel("Analytics (PyQt6)")
        title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch(1)
        self.vbox.addLayout(header)

        # Info row
        self.info_row = QHBoxLayout()
        self.lbl_ops = QLabel("Operations: 0")
        self.lbl_comp = QLabel("Completed: 0")
        self.lbl_fail = QLabel("Failed: 0")
        self.lbl_scraped = QLabel("Scraped: 0")
        for w in [self.lbl_ops, self.lbl_comp, self.lbl_fail, self.lbl_scraped]:
            w.setStyleSheet("color: #cccccc; padding-right: 12px;")
            self.info_row.addWidget(w)
        self.info_row.addStretch(1)
        self.vbox.addLayout(self.info_row)

        # Charts area
        self.grid = QGridLayout()
        self.vbox.addLayout(self.grid)

        if USE_PG:
            pg.setConfigOption('background', '#2b2b2b')
            pg.setConfigOption('foreground', 'w')
            # Plot 1: Scraped per minute (last 120 minutes)
            self.pg_plot1 = pg.PlotWidget(title="Scraped members (last 120m)")
            self.pg_curve1 = self.pg_plot1.plot([], [], pen=pg.mkPen('#00ff00', width=2))
            # Plot 2: Operation completion vs failure (cumulative)
            self.pg_plot2 = pg.PlotWidget(title="Operations (completed vs failed)")
            self.pg_curve2a = self.pg_plot2.plot([], [], pen=pg.mkPen('#4caf50', width=2))
            self.pg_curve2b = self.pg_plot2.plot([], [], pen=pg.mkPen('#f44336', width=2))
            self.grid.addWidget(self.pg_plot1, 0, 0)
            self.grid.addWidget(self.pg_plot2, 0, 1)
        elif HAVE_CHARTS:
            # Fallback to QtCharts
            self.chart1 = QChart(); self.chart1.setTitle("Scraped members (last 120m)")
            self.series1 = QLineSeries(); self.chart1.addSeries(self.series1)
            self.axisX1 = QValueAxis(); self.axisX1.setTitleText("t"); self.chart1.addAxis(self.axisX1, Qt.AlignmentFlag.AlignBottom); self.series1.attachAxis(self.axisX1)
            self.axisY1 = QValueAxis(); self.axisY1.setTitleText("count"); self.chart1.addAxis(self.axisY1, Qt.AlignmentFlag.AlignLeft); self.series1.attachAxis(self.axisY1)
            self.chartview1 = QChartView(self.chart1)

            self.chart2 = QChart(); self.chart2.setTitle("Operations (completed vs failed)")
            self.series2a = QLineSeries(); self.series2b = QLineSeries();
            self.chart2.addSeries(self.series2a); self.chart2.addSeries(self.series2b)
            self.axisX2 = QValueAxis(); self.axisX2.setTitleText("t"); self.chart2.addAxis(self.axisX2, Qt.AlignmentFlag.AlignBottom); self.series2a.attachAxis(self.axisX2); self.series2b.attachAxis(self.axisX2)
            self.axisY2 = QValueAxis(); self.axisY2.setTitleText("count"); self.chart2.addAxis(self.axisY2, Qt.AlignmentFlag.AlignLeft); self.series2a.attachAxis(self.axisY2); self.series2b.attachAxis(self.axisY2)
            self.chartview2 = QChartView(self.chart2)

            self.grid.addWidget(self.chartview1, 0, 0)
            self.grid.addWidget(self.chartview2, 0, 1)
        else:
            # Text-only fallback
            self.txt_fallback = QLabel("PyQt6 charts unavailable. Install 'pyqtgraph' or 'PyQt6-Qt6-Charts'.")
            self.txt_fallback.setStyleSheet("color: #ff9800;")
            self.grid.addWidget(self.txt_fallback, 0, 0, 1, 2)

        # Dark style
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QLabel { color: #ffffff; }
        """)

        # Timer to refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)
        self.refresh()

        # Menu action to quit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.menuBar().addAction(exit_action)

    def refresh(self):
        totals = self.data.totals()
        self.lbl_ops.setText(f"Operations: {totals['operations']}")
        self.lbl_comp.setText(f"Completed: {totals['completed']}")
        self.lbl_fail.setText(f"Failed: {totals['failed']}")
        self.lbl_scraped.setText(f"Scraped: {totals['scraped_members']}")

        # Build scraped series per minute
        stamps = self.data.scraped_series(120)
        if stamps:
            # Aggregate per 1-minute buckets
            start = datetime.now() - timedelta(minutes=120)
            xs = list(range(0, 121))
            counts = [0] * len(xs)
            for ts in stamps:
                diff = int((ts - start).total_seconds() // 60)
                if 0 <= diff <= 120:
                    counts[diff] += 1
            if USE_PG:
                self.pg_curve1.setData(xs, counts)
            elif HAVE_CHARTS:
                self.series1.clear()
                for i, c in enumerate(counts):
                    self.series1.append(float(i), float(c))
                self.axisX1.setRange(0, 120)
                self.axisY1.setRange(0, max(1, max(counts)))

        # Build operations time series from operation_states (approximate by started_at)
        rows = self.data.metrics_last_minutes(120)
        if rows:
            # Cumulative counts over time
            times = []
            comp = []
            fail = []
            csum = 0
            fsum = 0
            for (started_at, op_type, completed, failed) in rows:
                try:
                    t = datetime.fromisoformat(started_at)
                except Exception:
                    continue
                times.append(t)
                csum += int(completed or 0)
                fsum += int(failed or 0)
                comp.append(csum)
                fail.append(fsum)
            # Normalize X to index (simple)
            xs = list(range(len(times)))
            if USE_PG:
                self.pg_curve2a.setData(xs, comp)
                self.pg_curve2b.setData(xs, fail)
            elif HAVE_CHARTS:
                self.series2a.clear(); self.series2b.clear()
                for i in range(len(xs)):
                    self.series2a.append(float(xs[i]), float(comp[i]))
                    self.series2b.append(float(xs[i]), float(fail[i]))
                self.axisX2.setRange(0, max(1, len(xs)))
                ymax = max(1, max(comp + fail))
                self.axisY2.setRange(0, ymax)


def main():
    app = QApplication(sys.argv)
    win = AnalyticsWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
