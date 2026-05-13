# controller/graphs.py

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QListView
from PyQt6.QtCore import Qt

from model.graph_data import (
    get_strand_enrollment_counts,
    get_registrar_performance_counts,
    get_available_slots_by_strand,
)


class StrandEnrollmentGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StrandGraphSection")

        self.bg_color = "#EBF3FA"
        self.card_bg = "#FFFFFF"
        self.border_color = "#D1E0ED"
        self.text_color = "#333333"
        self.bar_color = "#4A90E2"

        self.setup_ui()
        self.load_and_draw_data()

    def setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.card_frame = QFrame()
        self.card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(10, 10, 10, 10)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.figure.patch.set_facecolor(self.card_bg)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout.addWidget(self.canvas, 1)

        main_layout.addWidget(self.card_frame, 1)
        self.ax_bar = self.figure.add_subplot(111)

    def fetch_strand_data(self):
        return get_strand_enrollment_counts()

    def load_and_draw_data(self):
        data = self.fetch_strand_data()
        strands = list(data.keys())
        values = list(data.values())

        if sum(values) == 0:
            values = [0, 0, 0, 0, 0]

        self.ax_bar.clear()
        self.ax_bar.set_facecolor(self.card_bg)
        bars = self.ax_bar.bar(strands, values, color=self.bar_color, width=0.6)

        self.ax_bar.set_title('Total Enrolled', color=self.text_color)
        self.ax_bar.tick_params(colors=self.text_color)

        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color(self.border_color)
        self.ax_bar.spines['bottom'].set_color(self.border_color)

        for bar in bars:
            height = bar.get_height()
            self.ax_bar.annotate(f'{int(height)}',
                                 xy=(bar.get_x() + bar.get_width() / 2, height),
                                 xytext=(0, 3),
                                 textcoords="offset points",
                                 ha='center', va='bottom', color=self.text_color)

        self.figure.tight_layout()
        self.canvas.draw()


class RegistrarPerformanceGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RegistrarGraphSection")

        self.card_bg = "#FFFFFF"
        self.border_color = "#D1E0ED"
        self.text_color = "#333333"
        self.bar_color = "#17a2b8"

        self.setup_ui()
        self.load_and_draw_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.card_frame = QFrame()
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(self.card_frame)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(self.card_bg)
        self.canvas = FigureCanvas(self.figure)
        card_layout.addWidget(self.canvas)

        main_layout.addWidget(self.card_frame)
        self.ax_bar = self.figure.add_subplot(111)

    def fetch_data(self):
        return get_registrar_performance_counts()

    def load_and_draw_data(self):
        data = self.fetch_data()
        names = list(data.keys())
        values = list(data.values())

        self.ax_bar.clear()
        self.ax_bar.set_facecolor(self.card_bg)
        bars = self.ax_bar.bar(names, values, color=self.bar_color, width=0.5)

        self.ax_bar.set_title('Total Enrolled Students per Registrar Account', color=self.text_color, pad=15,
                              fontsize=12, fontweight='bold')
        self.ax_bar.tick_params(colors=self.text_color, labelsize=9)

        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color(self.border_color)
        self.ax_bar.spines['bottom'].set_color(self.border_color)

        for bar in bars:
            height = bar.get_height()
            self.ax_bar.annotate(f'{int(height)}',
                                 xy=(bar.get_x() + bar.get_width() / 2, height),
                                 xytext=(0, 3),
                                 textcoords="offset points",
                                 ha='center', va='bottom', color=self.text_color, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()


class AvailableSlotsGraph(QWidget):
    """A custom interactive graph to show strictly max 50 available slots per section, decreasing dynamically."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SlotsGraphSection")

        self.card_bg = "#FFFFFF"
        self.border_color = "#D1E0ED"
        self.text_color = "#333333"
        self.bar_color_11 = "#4A90E2"  # Blue for Grade 11
        self.bar_color_12 = "#50E3C2"  # Teal for Grade 12

        self.current_strand = "STEM"
        self.setup_ui()
        self.load_and_draw_data()

    def setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        control_layout = QHBoxLayout()
        lbl = QLabel("Select Strand Network:")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        self.combo = QComboBox()
        self.combo.addItems(["STEM", "ABM", "HUMSS", "GAS", "TVL"])
        self.combo.setView(QListView())
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #9fb3c8;
                border-radius: 6px;
                color: #1f2933;
                font-size: 14px;
                min-width: 150px;
                padding: 7px 34px 7px 12px;
            }
            QComboBox:hover {
                border-color: #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #9fb3c8;
                color: #1f2933;
                selection-background-color: #d9ebff;
                selection-color: #102a43;
                outline: none;
            }
        """)
        self.combo.currentTextChanged.connect(self.on_strand_change)

        control_layout.addWidget(lbl)
        control_layout.addWidget(self.combo)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        self.card_frame = QFrame()
        self.card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.card_bg};
                border: 1px solid {self.border_color};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(self.card_frame)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(self.card_bg)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout.addWidget(self.canvas, 1)

        main_layout.addWidget(self.card_frame, 1)
        self.ax_bar = self.figure.add_subplot(111)

    def on_strand_change(self, strand):
        self.current_strand = strand
        self.load_and_draw_data()

    def fetch_data(self):
        labels = []
        available = []
        colors = []

        for slot in get_available_slots_by_strand(self.current_strand):
            grade = slot["grade"]
            schedule_label = slot.get("schedule_label", "")
            section_label = slot["section"]
            if schedule_label:
                section_label = f"{section_label}\n{schedule_label}"
            labels.append(f"Gr. {grade}\n{section_label}")
            available.append(slot["available"])
            colors.append(self.bar_color_11 if grade == "11" else self.bar_color_12)

        return labels, available, colors

    def load_and_draw_data(self):
        labels, available, colors = self.fetch_data()

        self.ax_bar.clear()
        self.ax_bar.set_facecolor(self.card_bg)

        if not labels:
            labels = ["No Data"]
            available = [0]
            colors = [self.bar_color_11]

        bars = self.ax_bar.bar(labels, available, color=colors, width=0.5)

        self.ax_bar.set_title(f'Real-Time Available Slots: {self.current_strand} (Max 50 / Section)',
                              color=self.text_color, pad=15, fontsize=12, fontweight='bold')
        self.ax_bar.tick_params(colors=self.text_color, labelsize=9)
        self.ax_bar.set_ylim(0, 55)

        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color(self.border_color)
        self.ax_bar.spines['bottom'].set_color(self.border_color)

        for bar in bars:
            height = bar.get_height()
            self.ax_bar.annotate(f'{int(height)} Slots',
                                 xy=(bar.get_x() + bar.get_width() / 2, height),
                                 xytext=(0, 3),
                                 textcoords="offset points",
                                 ha='center', va='bottom', color=self.text_color, fontweight='bold')

        self.figure.tight_layout()
        self.canvas.draw()
