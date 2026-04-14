import os
import random

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QRect, QTimer
from PySide6.QtGui import QPixmap

from src.ui.intro.photo_sprite import PhotoSprite


class BackgroundLayer(QWidget):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)

        self.project_root = project_root
        self.setStyleSheet("background-color: black;")
        self.forbidden_rect = None

        images_dir = os.path.join(project_root, "assets", "data", "images")
        self.image_paths = [
            os.path.join(images_dir, f)
            for f in os.listdir(images_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        self.sprites = []
        self.active_paths = set()

        count = min(4, len(self.image_paths))
        initial_paths = random.sample(self.image_paths, k=count)

        for path in initial_paths:
            pix = QPixmap(path)
            sprite = PhotoSprite(pix, parent=self)
            sprite.current_path = path
            sprite.hide()
            sprite.fadedOut.connect(lambda s=sprite: self.replace_sprite_image(s))
            self.sprites.append(sprite)
            self.active_paths.add(path)

        for i, sprite in enumerate(self.sprites):
            delay = int((2000 + random.randint(-500, 500)) * i)
            QTimer.singleShot(delay, sprite.start_cycle)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.relayout_sprites()

    def relayout_sprites(self):
        w = self.width()
        h = self.height()

        if w <= 0 or h <= 0:
            return

        for sprite in self.sprites:
            pix = sprite.pixmap()
            if pix is None:
                continue

            pw = pix.width()
            ph = pix.height()

            x, y = self.random_position_avoiding(sprite, pw, ph, w, h)
            sprite.setGeometry(x, y, pw, ph)
            sprite.show()

    def random_position_avoiding(self, sprite, pw, ph, w, h):
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)

        min_x = margin_x
        max_x = max(margin_x, w - pw - margin_x)

        min_y = margin_y
        max_y = max(margin_y, h - ph - margin_y)
        avoid_pad = int(min(w, h) * 0.12)

        for _ in range(60):
            x = random.randint(min_x, max_x) if max_x >= min_x else margin_x
            y = random.randint(min_y, max_y) if max_y >= min_y else margin_y

            candidate = QRect(x, y, pw, ph)
            if self.forbidden_rect is not None and candidate.intersects(self.forbidden_rect):
                continue
            too_close = False
            for other in self.sprites:
                if other is sprite:
                    continue
                if not other.isVisible():
                    continue
                r = other.geometry()
                if not r.isValid():
                    continue

                expanded = r.adjusted(-avoid_pad, -avoid_pad, avoid_pad, avoid_pad)
                if expanded.intersects(candidate):
                    too_close = True
                    break

            if not too_close:
                return x, y

        return w // 2 - pw // 2, h // 2 - ph // 2

    def set_forbidden_rect(self, rect):
        self.forbidden_rect = rect
        self.relayout_sprites()

    def replace_sprite_image(self, sprite: PhotoSprite):
        old_path = getattr(sprite, "current_path", None)
        if old_path in self.active_paths:
            self.active_paths.remove(old_path)

        available = [p for p in self.image_paths if p not in self.active_paths]
        if not available:
            available = [p for p in self.image_paths if p != old_path]

        new_path = random.choice(available)
        new_pix = QPixmap(new_path)

        sprite.setPixmap(new_pix)
        sprite.current_path = new_path
        self.active_paths.add(new_path)

        w = self.width()
        h = self.height()
        pw = new_pix.width()
        ph = new_pix.height()

        x, y = self.random_position_avoiding(sprite, pw, ph, w, h)
        sprite.setGeometry(x, y, pw, ph)

        sprite.start_cycle()
