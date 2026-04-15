from manim import *

class SplitScreenConcept(Scene):
    def construct(self):
        # --- 1. SETUP (Pure Black Canvas) ---
        self.camera.background_color = "#050505" # Very deep black/grey

        # --- 2. LEFT HEMISPHERE: The Code ---
        # We write a simple variable assignment and print statement
        code_snippet = Code(
            code_string='box = 5\nprint(box)',
            tab_width=4,
            background="rectangle",
            background_config={"stroke_width": 0, "fill_opacity": 0}, # Invisible background
            language="python",
            add_line_numbers=True,
            formatter_style="monokai"
        ).scale(2) # We can scale this up massively now!
        
        # Anchor the code to the absolute left middle of the screen
        code_snippet.to_edge(LEFT, buff=1.5)

        # --- 3. THE DIVIDER ---
        # A subtle vertical line separating Logic from Visualization
        divider = Line(UP*4, DOWN*4, color=DARK_GRAY)

        # --- 4. RIGHT HEMISPHERE: The Visual Metaphor ---
        # We literally build a 2D box for the variable
        var_box = Square(side_length=2, color="#58C4DD", stroke_width=4)
        var_label = Text("box", font_size=30, color=GRAY).next_to(var_box, UP)
        
        # The data that will go inside the box
        data_value = Text("5", font_size=60, color="#4AF626")
        
        # Group the right-side elements and anchor them to the right
        visual_group = VGroup(var_box, var_label)
        visual_group.to_edge(RIGHT, buff=2.5)
        
        # Position the data value dead-center inside the box
        data_value.move_to(var_box.get_center())

        # --- 5. THE ANIMATION SEQUENCE ---
        self.play(FadeIn(divider))
        
        # Step A: Write the code
        self.play(Write(code_snippet), run_time=2)
        self.wait(0.5)
        
        # Step B: Explain Line 1 (box = 5)
        # We highlight the first line using the array hack we learned
        highlight_1 = SurroundingRectangle(code_snippet[-1][0], color=YELLOW, fill_opacity=0.2, buff=0.1)
        self.play(Create(highlight_1), run_time=0.5)
        
        # Draw the literal box on the right
        self.play(Create(var_box), Write(var_label), run_time=1)
        
        # Make the number 5 pop into existence inside the box
        self.play(GrowFromCenter(data_value), run_time=0.5)
        self.wait(1)

        # Step C: Explain Line 2 (print(box))
        # Move the highlight from Line 1 down to Line 2
        highlight_2 = SurroundingRectangle(code_snippet[-1][1], color=YELLOW, fill_opacity=0.2, buff=0.1)
        self.play(Transform(highlight_1, highlight_2), run_time=0.5)
        
        # Emphasize the box pulsing to show it's being "accessed"
        self.play(Indicate(var_box, color="#4AF626", scale_factor=1.2))
        self.wait(1)