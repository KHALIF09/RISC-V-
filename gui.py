import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from simulator import RISCVSim, PipelineSim

class PipelineWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect()
        stage_w = rect.width() // 5 - 12
        stage_h = rect.height() - 30
        x = 10
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        for i, name in enumerate(['IF','ID','EX','MEM','WB']):
            r = QtCore.QRect(x, 10, stage_w, stage_h)
            painter.setBrush(QtGui.QColor(240,240,240))
            painter.setPen(QtGui.QPen(QtGui.QColor(60,60,60), 2))
            painter.drawRoundedRect(r, 8, 8)
            painter.drawText(r.adjusted(4,4,-4,-4), QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter, name)
            x += stage_w + 8
        painter.end()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RISC-V Simulator (PyQt5) - Pipeline View')
        self.sim = RISCVSim()
        self.pipeline = PipelineSim(self.sim)
        self.init_ui()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_cycle)
        self.running = False

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)

        # Controls
        controls = QtWidgets.QHBoxLayout()
        btn_load = QtWidgets.QPushButton('Load HEX')
        btn_load.clicked.connect(self.load_file)
        controls.addWidget(btn_load)

        btn_step = QtWidgets.QPushButton('Step Core')
        btn_step.clicked.connect(self.step_core)
        controls.addWidget(btn_step)

        btn_cycle = QtWidgets.QPushButton('Cycle Pipeline')
        btn_cycle.clicked.connect(self.cycle_pipeline)
        controls.addWidget(btn_cycle)

        btn_run = QtWidgets.QPushButton('Run Pipeline')
        btn_run.setCheckable(True)
        btn_run.toggled.connect(self.toggle_run)
        controls.addWidget(btn_run)

        btn_reset = QtWidgets.QPushButton('Reset')
        btn_reset.clicked.connect(self.reset)
        controls.addWidget(btn_reset)

        controls.addWidget(QtWidgets.QLabel('Speed (ms)'))
        self.spin_speed = QtWidgets.QSpinBox(); self.spin_speed.setRange(10,2000); self.spin_speed.setValue(300)
        controls.addWidget(self.spin_speed)

        v.addLayout(controls)

        # Pipeline drawing + labels
        self.pipeline_widget = PipelineWidget()
        v.addWidget(self.pipeline_widget)

        # Below: stage details, registers, memory
        h = QtWidgets.QHBoxLayout()

        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel('Pipeline Stages (latest)'))
        self.stage_list = QtWidgets.QListWidget()
        left.addWidget(self.stage_list)
        h.addLayout(left, 1)

        mid = QtWidgets.QVBoxLayout()
        mid.addWidget(QtWidgets.QLabel('Registers'))
        self.reg_table = QtWidgets.QTableWidget(8,4)
        self.reg_table.setHorizontalHeaderLabels(['r0','r1','r2','r3'])
        self.reg_table.verticalHeader().setVisible(False)
        mid.addWidget(self.reg_table)
        h.addLayout(mid,1)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel('Memory (first 64 words)'))
        self.mem_view = QtWidgets.QTextEdit(); self.mem_view.setReadOnly(True)
        right.addWidget(self.mem_view)
        right.addWidget(QtWidgets.QLabel('Log'))
        self.log = QtWidgets.QTextEdit(); self.log.setReadOnly(True)
        right.addWidget(self.log)
        h.addLayout(right,2)

        v.addLayout(h)
        self.update_ui()

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open HEX file', '', 'HEX Files (*.hex);;All Files (*)')
        if not path: return
        try:
            words = []
            with open(path,'r') as f:
                for line in f:
                    line = line.split('#',1)[0].strip()
                    if not line: continue
                    for tok in line.split():
                        if tok.lower().startswith('0x'):
                            tok = tok[2:]
                        words.append(int(tok,16))
            self.sim.reset()
            self.pipeline.reset()
            self.sim.load_words(words, 0)
            self.log.append(f'Loaded {len(words)} words from {path}')
            self.update_ui()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def step_core(self):
        # execute a single instruction directly on core
        if self.sim.halted:
            self.log.append('Core halted')
            return
        self.sim.step()
        self.update_ui()

    def cycle_pipeline(self):
        if self.pipeline.halted or self.sim.halted:
            self.log.append('Pipeline/Core halted')
            return
        self.pipeline.cycle()
        self.log.append('Pipeline cycled')
        self.update_ui()

    def auto_cycle(self):
        if not self.running: return
        self.cycle_pipeline()
        if self.pipeline.halted:
            self.toggle_run(False)

    def toggle_run(self, running: bool):
        self.running = running
        if running:
            self.timer.start(self.spin_speed.value())
        else:
            self.timer.stop()

    def reset(self):
        self.sim.reset(); self.pipeline.reset(); self.log.append('Reset'); self.update_ui()

    def update_ui(self):
        # update pipeline stage list
        self.stage_list.clear()
        for name, instr_hex, pc in self.pipeline.get_stage_info():
            line = f"{name}: " + (instr_hex if instr_hex else "-") + (f" @ {pc}" if pc else "")
            self.stage_list.addItem(line)
        # update registers
        for row in range(8):
            for col in range(4):
                idx = row*4 + col
                item = QtWidgets.QTableWidgetItem(f'x{idx}: 0x{self.sim.regs[idx]:08X}')
                self.reg_table.setItem(row, col, item)
        # update memory view (first 256 bytes)
        lines = []
        for addr in range(0, 256, 4):
            w = self.sim.read_word(addr)
            lines.append(f'0x{addr:04X}: 0x{w:08X}')
        self.mem_view.setPlainText(''.join(lines))

        # update log with PC
        self.log.append(f'PC=0x{self.sim.pc:08X} halted={self.sim.halted}')
        # redraw pipeline widget
        self.pipeline_widget.update()
