from manim import *

class VariableBox(VGroup):
    """A standardized visual for a variable: A box with a label and a value inside."""
    def __init__(self, label, value, color="#58C4DD", **kwargs):
        super().__init__(**kwargs)
        self.box = RoundedRectangle(corner_radius=0.1, width=2, height=2, color=color, stroke_width=4)
        self.label = Text(label, font_size=24, color=GRAY).next_to(self.box, UP, buff=0.2)
        self.value_text = Text(str(value), font_size=48, color=WHITE).move_to(self.box.get_center())
        self.add(self.box, self.label, self.value_text)

    def update_value(self, new_value, scene):
        """Animates the value changing inside the box."""
        new_text = Text(str(new_value), font_size=48, color=WHITE).move_to(self.box.get_center())
        scene.play(Transform(self.value_text, new_text))

class DataList(VGroup):
    """A row of boxes representing an Array or List."""
    def __init__(self, values, color="#4AF626", **kwargs):
        super().__init__(**kwargs)
        self.boxes = VGroup(*[
            VariableBox(label=f"[{i}]", value=val, color=color) 
            for i, val in enumerate(values)
        ]).arrange(RIGHT, buff=0.2)
        self.add(self.boxes)

class LogicGate(VGroup):
    """A diamond shape used for If-Statements and decisions."""
    def __init__(self, condition, **kwargs):
        super().__init__(**kwargs)
        self.shape = Polygon([-1.5,0,0], [0,1,0], [1.5,0,0], [0,-1,0], color=YELLOW, stroke_width=4)
        self.text = Text(condition, font_size=20).move_to(self.shape.get_center())
        self.add(self.shape, self.text)