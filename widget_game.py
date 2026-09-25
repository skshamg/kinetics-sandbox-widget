import sys
import math
import random
import pymunk

from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QApplication, QWidget


class Particle:
    def __init__(self, body, shape, color):
        self.body = body
        self.shape = shape
        self.color = color


class DesktopSandboxWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless, translucent, pinned desktop widget
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.width = 500
        self.height = 620
        self.resize(self.width, self.height)
        self.move(950, 100)

        # Physics space setup
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 900.0)
        self.space.damping = 0.98

        self.setup_boundaries()

        self.particles = []

        # Interaction flags
        self.is_aiming = False
        self.sling_start = None
        self.sling_current = None
        self.is_dragging_window = False
        self.drag_window_pos = QPoint()

        # Telemetry metrics
        self.total_kinetic_energy = 0.0

        # 60 FPS physics & render loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_tick)
        self.timer.start(16)

        # Spawn initial particles
        for _ in range(14):
            self.spawn_particle(
                random.randint(80, 420),
                random.randint(100, 260),
                radius=random.randint(10, 16)
            )

    def setup_boundaries(self):
        """Creates physical barrier walls around the widget perimeter."""
        thickness = 20
        w, h = self.width, self.height

        walls = [
            [(0, 0), (w, 0)],
            [(0, h), (w, h)],
            [(0, 0), (0, h)],
            [(w, 0), (w, h)]
        ]

        for p1, p2 in walls:
            seg = pymunk.Segment(self.space.static_body, p1, p2, thickness)
            seg.elasticity = 0.85
            seg.friction = 0.3
            self.space.add(seg)

    def spawn_particle(self, x, y, radius=12, velocity=(0, 0)):
        mass = radius * 0.4
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        body.velocity = velocity

        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.88
        shape.friction = 0.3
        self.space.add(body, shape)

        colors = [
            QColor(0, 240, 255, 230),  # Neon Cyan
            QColor(255, 42, 75, 230),   # Neon Red
            QColor(255, 170, 0, 230),   # Neon Amber
            QColor(16, 185, 129, 230)   # Neon Green
        ]
        self.particles.append(Particle(body, shape, random.choice(colors)))

    def game_tick(self):
        """Steps the physics simulation and updates telemetry."""
        dt = 1.0 / 60.0
        self.space.step(dt)

        ke = 0.0
        for p in self.particles:
            v = p.body.velocity.length
            ke += 0.5 * p.body.mass * (v ** 2)
        self.total_kinetic_energy = ke

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Dark chassis container
        bg_brush = QBrush(QColor(8, 12, 18, 225))
        border_pen = QPen(QColor(0, 240, 255, 70), 1.5)
        painter.setBrush(bg_brush)
        painter.setPen(border_pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 16, 16)

        # Header grab-bar accent line
        painter.setPen(QPen(QColor(0, 240, 255, 30), 1))
        painter.drawLine(10, 60, self.width - 10, 60)

        # 2. Render particles
        for p in self.particles:
            pos = p.body.position
            r = p.shape.radius
            painter.setBrush(QBrush(p.color))
            painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
            painter.drawEllipse(QPointF(pos.x, pos.y), r, r)

            angle = p.body.angle
            end_x = pos.x + math.cos(angle) * r
            end_y = pos.y + math.sin(angle) * r
            painter.setPen(QPen(QColor(0, 0, 0, 180), 1.5))
            painter.drawLine(QPointF(pos.x, pos.y), QPointF(end_x, end_y))

        # 3. Slingshot vector preview
        if self.is_aiming and self.sling_start and self.sling_current:
            painter.setPen(QPen(QColor(0, 240, 255, 240), 2, Qt.PenStyle.DashLine))
            painter.drawLine(self.sling_start, self.sling_current)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(255, 42, 75, 220), 1.5))
            painter.drawEllipse(self.sling_start, 14, 14)

        # 4. Header readouts
        painter.setPen(QColor(0, 240, 255, 240))
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.drawText(20, 28, "KINETICS LAB // 2D PHYSICS WIDGET")

        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor(148, 163, 184))
        g_status = "9.8G" if self.space.gravity.y > 0 else "ZERO-G"
        info = f"BODIES: {len(self.particles)} | KE: {int(self.total_kinetic_energy):,} J | GRAV: {g_status}"
        painter.drawText(20, 46, info)

        # Footer controls guide
        painter.setPen(QColor(100, 116, 139))
        controls = "[TOP] DRAG WINDOW | [ARENA] SLING | [G] GRAV | [C] CLEAR"
        painter.drawText(20, self.height - 18, controls)

    # --- MOUSE DRAG & SLINGSHOT CONTROLS ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            # If clicked in the top header bar (0-60px), drag the window
            if pos.y() <= 60:
                self.is_dragging_window = True
                self.is_aiming = False
                self.drag_window_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            else:
                # Clicked inside the sandbox area: slingshot
                self.is_dragging_window = False
                self.is_aiming = True
                self.sling_start = pos
                self.sling_current = pos
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging_window:
            self.move(event.globalPosition().toPoint() - self.drag_window_pos)
            event.accept()
        elif self.is_aiming:
            self.sling_current = event.position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging_window:
                self.is_dragging_window = False
            elif self.is_aiming:
                self.is_aiming = False
                dx = (self.sling_start.x() - event.position().x()) * 8
                dy = (self.sling_start.y() - event.position().y()) * 8
                
                self.spawn_particle(
                    self.sling_start.x(),
                    self.sling_start.y(),
                    radius=random.randint(12, 20),
                    velocity=(dx, dy)
                )
            event.accept()

    def keyPressEvent(self, event):
        # [G] Toggle Gravity / Zero-G
        if event.key() == Qt.Key.Key_G:
            if self.space.gravity.y != 0:
                self.space.gravity = (0.0, 0.0)
            else:
                self.space.gravity = (0.0, 900.0)

        # [C] Clear particles
        elif event.key() == Qt.Key.Key_C:
            for p in self.particles:
                self.space.remove(p.body, p.shape)
            self.particles.clear()

        # [ESC] Close cleanly
        elif event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = DesktopSandboxWidget()
    game.show()
    sys.exit(app.exec())