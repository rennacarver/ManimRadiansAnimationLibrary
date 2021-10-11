from manim import *

#   for scenes 'Circles0to6Rad', 'RadianExplanation101' and 'EndAnimation' in manim CE v0.11.0
#   navigate to /manim/mobject/geometry.py
#   comment out line 142 "self.reset_endpoints_based_on_top(tip, at_start)"

config.disable_caching = True

config.tex_template = TexTemplate()

segoe_template = TexTemplate(
    tex_compiler="xelatex",
    output_format=".xdv",
    preamble=r"""
    \usepackage[english]{babel}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{fontspec}
    \setmainfont{Segoe UI Light}
    \usepackage[defaultmathsizes]{mathastext}
    """)

ANIM_ORANGE = "#C55A11"
ANIM_BLACK = "#404040"
ANIM_YELLOW = "#FFC000"
ANIM_BLUE = "#41719C"
ANIM_GREEN = "#A9D18E"
ANIM_AQUA = "#42A996"
ANIM_PURPLE = "#CC0099"

TEXT_COLOR = "#463622"

def get_background():
    """Returns a gradient rectangle to be used as the background."""
    background = Rectangle(
            width=config["frame_width"],
            height=config["frame_width"],
            stroke_width=0,
            fill_color=color.color_gradient(["#D5D4C9","#DBD7CF"], 32), #astroparche_light
            #fill_color=color.color_gradient(["#ECECEC", "#F2F2F2"], 32), #whiteboard_modern
            fill_opacity=1, z_index=-1000)
    return background

class RadianCircle():
    """An updating circle, labels and objects."""
    @classmethod
    def get_circle_and_objs(
        self,
        radius: float = 1, 
        label_radius: int = 1,
        use_letters: bool = False,
        coords: np.array = ORIGIN,
        tracker: ValueTracker = ValueTracker(0),
        show_angle_label: bool = True,
        x_tracker: ValueTracker = None,
        radius_tracker: ValueTracker = None,
        simplified: bool = False,
        segment_color: str = ANIM_ORANGE,
        circle_stroke_width: float = 3
        ):
        """Returns a circle with extra objects.
        
        Parameters
        -----------
        radius : float
            The radius of the circle.
        label_radius : int
            The radius to be shown in a label.
        use_letters : bool
            Whether to use letters or not for the equations, radius & distance labels.
        coords : np.array
            The position of the circle.
        tracker : ValueTracker
            The ValueTracker to track the current angle.
        show_angle_label : bool
            Whether to show or not the equation above the circle that displays the angle.
        x_tracker : ValueTracker
            The ValueTracker to track the x coordinate and move everything accordingly.
        radius_tracker : ValueTracker
            The ValueTracker to track the circle's radius.
        simplified : bool
            If set to True, returns only the circle, fixed and rotating segment and center dot.
        segment_color : str
            The color of the segments forming the angle.
        circle_stroke_width : float
            The stroke width of the circle.

        Returns
        -----------
        VGroup
            A group of all the objects.
        """

        def get_distance():
            return str(round(label_radius * tracker.get_value(), 1))

        def get_angle_label():
            distance = float(get_distance())

            if use_letters and distance <= label_radius:
                theta = r"{{\theta}} \, = \, "
            else:
                theta = r"\theta\,=\,"

            if use_letters:
                if distance <= label_radius:
                    return MathTex(theta + r"{ {{s}} \over {{r}} }").set_color(TEXT_COLOR)

                tmp_frac = MathTex(theta + r"{", "6.28", r"r \over r}").set_color(TEXT_COLOR)

                text_rad =  DecimalNumber(tracker.get_value(), num_decimal_places=2).move_to(tmp_frac[1]).set_color(TEXT_COLOR)

                return VGroup(tmp_frac[0], text_rad, tmp_frac[2])

            tmp_frac = MathTex(theta, r"{", str(float(label_radius)), r"\over " + str(label_radius) + r"} \, = ")

            text_distance = DecimalNumber(distance, num_decimal_places=1).move_to(tmp_frac[2])

            text_rad =  DecimalNumber(tracker.get_value(), num_decimal_places=2).next_to(tmp_frac, buff=0.2)

            return VGroup(tmp_frac[:2], text_distance, tmp_frac[3], text_rad).set_color(TEXT_COLOR)

        def get_distance_label():
            label = None
            if use_letters:
                if float(get_distance()) <= label_radius:
                    label = MathTex("s")
                else:
                    label = VGroup(DecimalNumber(round(tracker.get_value(), 2), num_decimal_places=2),
                        MathTex("r")).arrange(buff=0.05)
                    label[-1].align_to(label[0], DOWN)
            else:
                dist = float(get_distance())
                label = DecimalNumber(dist, num_decimal_places=1)

            label.scale(0.5).set_color(ANIM_ORANGE)
            label.move_to(Arc(radius=radius_func()+0.3, angle=tracker.get_value(), arc_center=center()).point_from_proportion(0.5))

            return label if tracker.get_value() > 0.5 else VMobject()

        center = lambda: coords
        if x_tracker is not None:
            center = lambda: (x_tracker.get_value(), 0, 0)

        radius_func = (lambda: radius) if not radius_tracker else (lambda: radius_tracker.get_value())

        initial_angle = tracker.get_value()

        circle = Circle(radius=radius_func(), color=ANIM_BLACK, stroke_width=circle_stroke_width).move_to(center()).add_updater(
            lambda m: m.become(Circle(radius=radius_func(), color=ANIM_BLACK, stroke_width=circle_stroke_width)).move_to(center())
        )

        fixed_segment = Line(start=center(), end=circle.get_right(), color=segment_color).add_updater(
            lambda m: m.become(Line(start=center(), end=circle.get_right(), color=segment_color))
        )

        rotating_segment = Line(
            start=center(),
            end=(center()[0] + np.cos(initial_angle)*radius_func(), center()[1] + np.sin(initial_angle)*radius_func(), 0),
            color=segment_color).add_updater(
            lambda m: m.become(
                Line(
                    start=center(),
                    end=(center()[0] + np.cos(tracker.get_value())*radius_func(), center()[1] + np.sin(tracker.get_value())*radius_func(), 0),
                    color=segment_color))
        )

        center_dot = Dot(circle.get_center(), radius=DEFAULT_DOT_RADIUS/2, color=segment_color).add_updater(lambda m: m.move_to(center()))

        if simplified:
            return VGroup(circle, fixed_segment, rotating_segment, center_dot)

        theta = MathTex(r"\theta", color=ANIM_ORANGE).scale(0.5).move_to(circle.get_right())

        theta.add_updater(lambda m: m.move_to(
            Angle(
                fixed_segment, rotating_segment, radius=0.1 + 3 * SMALL_BUFF, other_angle=False
            ).point_from_proportion(0.5)
        )if tracker.get_value() != 0 else lambda m: m)

        theta.add_updater(lambda m: m.set_opacity(tracker.get_value()*2))

        dot = Dot(circle.get_right(), color=ANIM_ORANGE).add_updater(lambda m: m.move_to(circle.get_right()))

        arc_arrow = Arc(radius=radius_func(), angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=center()).add_updater(
            lambda m: m.become(Arc(radius=radius_func(), angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=center()).add_tip(tip_length=0.1)
                if tracker.get_value() > 0.1 else Arc(radius=radius_func(), angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=center()))
        )

        label_radius_tex = MathTex("r \ = \ " + str(label_radius) if not use_letters else "r", color=ANIM_ORANGE).scale(0.43).add_updater(
            lambda m, dt: m.next_to(fixed_segment, DOWN), call_updater=True
        )

        label_distance = get_distance_label().add_updater(lambda m: m.become(get_distance_label()))

        group = VGroup(circle, fixed_segment, rotating_segment, theta, dot, center_dot, arc_arrow, label_radius_tex, label_distance)

        if not show_angle_label:
            return group

        angle_label = get_angle_label().set_color(ANIM_BLACK).scale(0.6).next_to(circle, UP, buff=0.6).add_updater(lambda m: m.become(
            get_angle_label().set_color(ANIM_BLACK).scale(0.6).next_to(circle, UP, buff=0.6)
        ))

        group.add(angle_label)        

        return group

class Compass():
    """A compass with two perpendicular double arrows and labels."""
    @classmethod
    def create_compass(self, labels=None, coords=ORIGIN, rotation=0):
        """Returns a compass.

        Parameters
        -----------
        labels : list
            A list of the labels to be used. They will be placed in the following order: UP, DOWN, LEFT, RIGHT
        coords : np.array 
            The position of the compass.
        rotation : float
            The angle to rotate the compass and labels.

        Returns
        -----------
        VGroup
            A group of the compass and labels.
        """
        arrows = VGroup(*[
            DoubleArrow(start=LEFT*1.3, end=RIGHT*1.35, tip_length=.2, color=ANIM_BLACK, stroke_width=6, z_index=-10).rotate(
                PI/2 if i else 0)
            for i in range(2)])
        arrows.move_to(coords)
        for a in arrows:
            for tip in a.get_tips():
                tip.z_index=-10

        if labels is None:
            return arrows.rotate(rotation)

        labels_text = VGroup()

        for text, coord in zip(labels, [UP, DOWN, LEFT, RIGHT]):
            label = Text(text, color=ANIM_BLACK, stroke_width=1).scale(0.5).next_to(arrows.get_edge_center(coord), coord)
            labels_text.add(label)

        compass = VGroup(arrows, labels_text).rotate(rotation)

        return compass

class Timer():
    """A timer with animating functionality."""
    @classmethod
    def create_timer(self, seconds=5):
        """Creates the timer.

        Parameters
        -----------
        seconds : int
            The amount of seconds of the timer.

        Returns
        -----------
        VGroup
            A group containing the circle and numbers.
        """
        numbers = [Text(str(i), color=TEXT_COLOR, font="Segoe UI Light").scale(0.4) for i in range(seconds+1)]
        numbers.reverse()
        circle = Circle(radius=max(numbers[0].height, numbers[0].width)*1.5, color=ANIM_ORANGE, stroke_width=2).to_corner(DL).rotate(PI/2)
        for i in numbers:
            i.move_to(circle.get_center())

        return VGroup(VGroup(*numbers), circle)

    @classmethod
    def animate(self, renderer, timer):
        """Animates the timer counting down. The timer should already be on screen before
        calling this method.

        Parameters
        -----------
        renderer : Scene
            The Scene where the timer will be animated.
        timer : Timer
            The timer to be animated.

        Returns
        -----------
        None
        """
        global time_passed
        time_passed = 0
        numbers = timer[0]
        circle = timer[1]

        def get_number(dt):
            global time_passed
            index = min(int(time_passed), len(numbers) - 1)
            time_passed += dt

            return numbers[index]

        numbers[0].add_updater(lambda m, dt: m.become(get_number(dt)))
        renderer.play(Uncreate(circle, rate_func=lambda t: 1-t), run_time=5)
        numbers[0].clear_updaters()
        numbers[0].become(numbers[-1])
        renderer.play(FadeOut(numbers[0]), run_time=0.5)

class TicksAndLabelsFromCircle():
    """A set of ticks/dashes and labels constructed around a circle."""
    @classmethod
    def create_ticks_and_labels(self, circle, label_angles, inner_labels, outer_labels, full_turn_labels, scale_factor=0.4):
        """Returns the ticks and labels from a passed circle.

        Parameters
        -----------
        circle : Circle
            The circle to place the ticks and labels around.
        label_angles : list
            A list of angles where a tick and labels should be placed.
        innner_labels : list
            A list of tex strings to make a label positioned inside the circle.
        outer_labels : list
            A list of tex strings to make a label positioned outside the circle.
        full_turn_labels : tuple
            The two labels (tex strings) that represent a full turn. The inner one should go first. For example: 360° or 2pi.
        scale_factor :  float
            The scale factor for the labels.

        Returns
        -----------
        tuple
            A tuple containing the ticks, inner labels and outer labels.
        """
        p = circle.get_center()
        r = circle.radius - 0.06
        
        ticks = VGroup()
        inner_labels_tex = VGroup()
        outer_labels_tex = VGroup()

        for i, (a, inner, outer) in enumerate(zip(label_angles, inner_labels, outer_labels)):
            tick = Line(stroke_width=2, color=ANIM_BLACK)
            tick.set_length(0.15).rotate(a)
            tick.move_to((p[0] + np.cos(a) * r, p[1] + np.sin(a) * r, 0))
            ticks.add(tick)

            inner_label = MathTex(inner, tex_template=segoe_template, color=TEXT_COLOR).scale(scale_factor)
            direction = DOWN*round(np.sin(a), 10)+LEFT*round(np.cos(a), 10)
            inner_label.next_to(tick.get_start(), direction, aligned_edge=direction, buff=0.23)
            inner_labels_tex.add(inner_label)

            outer_label = MathTex(outer, tex_template=segoe_template, color=TEXT_COLOR).scale(scale_factor)
            direction = UP*round(np.sin(a), 10)+RIGHT*round(np.cos(a), 10)
            outer_label.next_to(tick, direction, aligned_edge=ORIGIN, buff=0.1)
            outer_labels_tex.add(outer_label)
        
        inner_full_turn, outer_full_turn = [
            MathTex(i, tex_template=segoe_template, color=TEXT_COLOR).scale(scale_factor)
            for i in full_turn_labels
            ]

        inner_full_turn.next_to(inner_labels_tex[0], DOWN, buff=0.1).align_to(inner_labels_tex[0], RIGHT)
        outer_full_turn.next_to(outer_labels_tex[0], DOWN, buff=0.1).align_to(outer_labels_tex[0], LEFT)

        VGroup(inner_full_turn, inner_labels_tex[0]).next_to(ticks[0], LEFT, buff=0.15)
        VGroup(outer_full_turn, outer_labels_tex[0]).next_to(ticks[0], RIGHT, buff=0.15)

        inner_labels_tex.add(inner_full_turn)
        outer_labels_tex.add(outer_full_turn)

        return (ticks, inner_labels_tex, outer_labels_tex)

class GridCompass(Scene):
    def construct(self):
        buff = 1.7

        vertical_lines = VGroup(*[Line(UP*3.2, DOWN*3.2, color=ANIM_BLACK) for _ in range(4)]).arrange(buff=buff)
        horizontal_lines = VGroup(*[Line(LEFT*3.2, RIGHT*3.2, color=ANIM_BLACK) for _ in range(4)]).arrange(DOWN, buff=buff)

        grid = VGroup(vertical_lines, horizontal_lines)

        red_dot = Dot(point=(-buff*1.5, -buff*1.5, 0), radius=DEFAULT_DOT_RADIUS * 3, color=ANIM_ORANGE, z_index=1000)
        green_dot = Dot(point=(buff*1.5, buff*1.5, 0), radius=DEFAULT_DOT_RADIUS * 3, color=ANIM_AQUA, z_index=1000)

        fifth = Tex("5th", color=TEXT_COLOR).scale(0.5).next_to(red_dot, LEFT, buff=0.75).shift(UP*0.01)
        roosevelt = Tex("Roosevelt", color=TEXT_COLOR).scale(0.5).next_to(red_dot, DOWN, buff=0.6)#.shift(LEFT*0.1)

        eighth = Tex("8th", color=TEXT_COLOR).scale(0.5).next_to(green_dot, RIGHT, buff=0.6)#.shift(UP*0.2)
        columbus = Tex("Columbus", color=TEXT_COLOR).scale(0.5).next_to(green_dot, UP, buff=0.5).shift(UP*0.1)

        grid_objs = VGroup(grid, green_dot, red_dot, fifth, eighth, roosevelt, columbus)

        shift_factor = LEFT*2

        compass1 = Compass.create_compass(labels=["N", "S", "W", "E"], coords=RIGHT*4)

        vectors = VGroup()

        for i in range(6):
            k = int(i/2) if i != 1 else 3
            direction_h = [(buff*(k-1.5), buff*(k-1.5), 0), (buff*(k-0.5), buff*(k-1.5), 0)]
            direction_v = [(buff*(k-1.5), buff*(k-2.5), 0), (buff*(k-1.5), buff*(k-1.5), 0)]

            direction_to_use = direction_h if i % 2 == 0 else direction_v

            arrow = Arrow(*direction_to_use , tip_length=0.2, color=ANIM_ORANGE, z_index=100, buff=0).shift(shift_factor)
            vectors.add(arrow)

        vectors.sort()

        self.add(get_background())

        self.play(Create(grid), run_time=4)
        self.wait(0.5)
        self.play(Write(red_dot), run_time=0.5)
        self.wait(0.2)
        self.play(FadeIn(VGroup(fifth, roosevelt)))
        self.wait(0.3)
        self.play(Write(green_dot), run_time=0.5)
        self.wait(0.2)
        self.play(FadeIn(VGroup(eighth, columbus)))
        self.wait(0.5)
        self.play(
            Write(compass1),
            grid_objs.animate.shift(shift_factor)
            )
        self.wait(0.5)
        for i in vectors:
            self.play(GrowArrow(i), run_time=0.7)
            self.wait(0.2)
        self.wait(0.5)
        self.play(FadeOut(grid_objs, compass1, vectors))
        self.wait(0.5)

class BigGridCompasses(Scene):
    def construct(self):
        buff = 0.5

        vertical_lines = VGroup(*[Line(UP*3.1, DOWN*3.1, color=ANIM_BLACK, stroke_width=2) for _ in range(16)]).arrange(buff=buff)
        horizontal_lines = VGroup(*[Line(LEFT*4, RIGHT*4, color=ANIM_BLACK, stroke_width=2) for _ in range(12)]).arrange(DOWN, buff=buff)

        grid = VGroup(vertical_lines, horizontal_lines)

        red_dot = Dot(point=(-buff*4.5, -buff*4.5, 0), radius=DEFAULT_DOT_RADIUS * 2, color=ANIM_ORANGE, z_index=1000)
        green_dot = Dot(point=(buff*6.5, buff*3.5, 0), radius=DEFAULT_DOT_RADIUS * 2, color=ANIM_AQUA, z_index=1000)

        panama = Tex("Panama", color=TEXT_COLOR).scale(0.5).next_to(red_dot, DOWN, buff=0.8)#.shift(LEFT*0.5)
        rotterdam = Tex("Rotterdam", color=TEXT_COLOR).scale(0.5).next_to(green_dot, UP, buff=1.5)#.shift(LEFT*0.5)

        grid_objs = VGroup(grid, green_dot, red_dot, panama, rotterdam)

        shift_factor = LEFT*2

        compass1 = Compass.create_compass(labels=["N", "S", "W", "E"], coords=RIGHT*4)
        compass2 = Compass.create_compass(labels=["NE", "SW", "NW", "SE"], coords=compass1[0])

        compasses = [Compass.create_compass(coords=compass1[0]) for _ in range(100)]

        vector = Arrow(start=red_dot.get_center(), end=(buff*5.5, buff*4.5, 0), tip_length=.2, color=ANIM_ORANGE,
            z_index=100, buff=0).shift(shift_factor)

        final_vector = Arrow(start=red_dot.get_center(), end=green_dot.get_corner(DL), tip_length=.2, color=ANIM_ORANGE,
            z_index=100, buff=0).shift(shift_factor)

        final_vector.get_tip().z_index = 100

        radius = 0.925

        circle = Circle(radius=compasses[-1].width/2, color=ANIM_BLACK, fill_opacity=1, z_index=-1).move_to(RIGHT*4)
        outer_circle = Circle(radius=radius, color=ANIM_BLACK, z_index=-1).move_to(RIGHT*4)

        tracker = ValueTracker(PI/4)

        radius += 0.025

        vec = Arrow(start=RIGHT*4, end=(4 + np.cos(tracker.get_value())*radius, np.sin(tracker.get_value())*radius, 0), color=ANIM_ORANGE, buff=0, z_index=1000,
            stroke_width=6, tip_length=0.2, max_stroke_width_to_length_ratio=6)

        vec.add_updater(lambda m: m.become(
            Arrow(start=outer_circle.get_center(), end=(outer_circle.get_x() + np.cos(tracker.get_value())*radius, np.sin(tracker.get_value())*radius, 0),
                color=ANIM_ORANGE, buff=0, z_index=1000, stroke_width=6, tip_length=0.2, max_stroke_width_to_length_ratio=6)))

        vec.suspend_updating()

        rectangle = Rectangle(height=buff*12.5, width=buff*16.5, color=ANIM_BLACK, fill_opacity=1, z_index=0).shift(shift_factor)

        grid_copy = grid.copy().shift(shift_factor)

        earth = Tex("Earth", color=TEXT_COLOR).scale(0.5).move_to(panama).shift(shift_factor).shift(0.2*DOWN)
        moon = Tex("Moon", color=TEXT_COLOR).scale(0.5).move_to(rotterdam).shift(shift_factor)

        copy_dots = [green_dot.copy().shift(UP*DEFAULT_DOT_RADIUS*3*i+LEFT*DEFAULT_DOT_RADIUS*3*i+shift_factor) for i in range(1, 3)]
        copy_dots = VGroup(*copy_dots)

        self.add(get_background())

        self.play(Create(vertical_lines), Create(horizontal_lines), run_time=3)
        self.wait(0.5)
        self.play(Create(red_dot), run_time=0.5)
        self.wait(0.2)
        self.play(Write(panama))
        self.wait(0.3)
        self.play(Create(green_dot), run_time=0.5)
        self.wait(0.2)
        self.play(Write(rotterdam))
        self.wait(0.5)
        self.play(Write(compass1), grid_objs.animate.shift(shift_factor))
        self.wait(0.5)
        self.add(compass2[0])
        self.play(
            Write(compass2[1]),
            compass2[0].animate.rotate(-PI/4),
            compass2[1].animate.rotate(-PI/4)
            )
        self.wait(0.5)
        self.play(GrowArrow(vector), GrowArrow(vec))
        self.wait(0.5)
        for j, c in enumerate(compasses[:2]):
            self.add(c.rotate(-PI/4))
            angle = PI/8
            angle *= -1 if j else 1
            self.play(c.animate.rotate(angle), run_time=0.5, rate_func=rate_functions.ease_in_out_sine)
        
        to_add = []
        for j, c in enumerate(compasses[2:7]):
            initial_angle = -PI/4 - (PI/8) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/16
            angle *= -1 if j else 1
            c.rotate(angle)
            to_add.append(c)
        self.play(FadeIn(*to_add))
        self.wait(0.1)

        to_add = []
        for j, c in enumerate(compasses[7:16]):
            initial_angle = -PI/4 - (PI/16) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/32
            angle *= -1 if j else 1
            c.rotate(angle)
            to_add.append(c)
        self.play(FadeIn(*to_add))
        self.wait(0.05)

        to_add = []

        for j, c in enumerate(compasses[16:33]):
            initial_angle = -PI/4 - (PI/32) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/64
            angle *= -1 if j else 1
            c.rotate(angle)
            to_add.append(c)

        self.play(FadeIn(*to_add), run_time=1.1)

        self.wait(0.2)
        self.play(FadeOut(compass1[1], compass2[1]), FadeIn(circle))
        self.remove(*compasses, compass1[0], compass2[0])
        self.play(TransformMatchingShapes(circle, outer_circle))
        self.wait(0.5)
        vec.resume_updating()
        self.wait(0.5)
        self.play(tracker.animate.set_value(36*DEGREES), ReplacementTransform(vector, final_vector))
        self.wait(0.5)

        self.play(
            grid.animate.scale(0.4),
            FadeTransform(grid_copy, rectangle),
            ReplacementTransform(panama, earth),
            ReplacementTransform(rotterdam, moon),
            run_time=2)
        self.wait(0.5)
        self.play(
            tracker.animate.set_value(43*DEGREES),
            final_vector.animate.rotate(7*DEGREES, about_point=final_vector.get_start())
            )
        self.wait(0.5)
        self.play(Create(copy_dots))
        self.wait(2.0)
        self.remove(grid, grid_copy)
        self.play(
            FadeOut(earth, moon, final_vector, copy_dots, red_dot, green_dot, rectangle),
            outer_circle.animate.center())
        vec.clear_updaters()
        self.play(FadeOut(vec))
        self.wait(0.5)

class DashedCircles(ZoomedScene):
    def __init__(self, **kwargs):
            ZoomedScene.__init__(
                self,
                zoom_factor=0.3,
                zoomed_display_height=2,
                zoomed_display_width=3,
                image_frame_stroke_width=20,
                zoomed_camera_config={
                    "default_frame_stroke_width": 3,
                    },
                **kwargs
            )

    def construct(self):
        config.disable_caching = True
        def show_dashes_and_labels(angle, dt):
            if dt == 0:
                return
            angle_int = int(angle)
            angles_to_show = [i % 360 for i in range(self.last_dashed_angle + 1, angle_int + 1)]
            label_to_show = np.intersect1d(angles_to_show, angles_w_labels)
            if label_to_show.size > 0:
                label_to_show = angles_w_labels.index(label_to_show[0])
                labels[label_to_show].add_updater(lambda m, dt: m.set_opacity(m.get_fill_opacity() + dt *2))
                labels[label_to_show].set_opacity(0)
                self.add(labels[label_to_show])
                
            self.last_dashed_angle = angle_int
            
            if angles_to_show:
                for i in angles_to_show:
                    self.add(dashes[i])

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame
        zoomed_display_frame = zoomed_display.display_frame

        radius_tracker = ValueTracker(0.925)
        angle_tracker = ValueTracker(40)

        end_radius = 2.4
        
        self.last_dashed_angle = int(angle_tracker.get_value()) - 1
        angles_w_labels = [0, 90, 180, 270]

        circle = Circle(radius=radius_tracker.get_value(), color=ANIM_BLACK).add_updater(
            lambda m: m.become(Circle(radius=radius_tracker.get_value(), color=ANIM_BLACK))
        )

        tmp_circ = Circle(radius=1.5)

        dashes = self.get_dashes(Circle(radius=end_radius))
        labels = self.get_labels(Circle(radius=end_radius))

        small_dashes = self.get_dashes(tmp_circ)
        small_labels = self.get_labels(tmp_circ, labels=["0°, 360°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"])

        labels1 = self.get_labels(Circle(radius=end_radius), labels=["0, 100", "25", "50", "75"])
        labels2 = self.get_labels(Circle(radius=end_radius), labels=["0, 400", "100", "200", "300"])

        timer = Timer.create_timer()

        zd_rect = BackgroundRectangle(zoomed_display, fill_opacity=0, buff=MED_SMALL_BUFF)
        self.add_foreground_mobject(zd_rect)

        unfold_camera = UpdateFromFunc(zd_rect, lambda rect: rect.replace(zoomed_display))

        dasher = VMobject().add_updater(lambda m, dt: show_dashes_and_labels(angle_tracker.get_value(), dt), call_updater=True)
        dasher.suspend_updating()

        circle_r = Circle(radius=1.5, color=ANIM_BLACK).shift(RIGHT*4.5+DOWN*0.8)
        labels_r = self.get_labels(tmp_circ, labels=["0, 100", "12.5", "25", "37.5", "50", "52.5", "75", "87.5"])
        dashes_r = self.get_dashes(circle_r)
        vec_r = self.get_arrow(circle_r, angle_tracker)
        angle_label_r = VMobject().add_updater(lambda m, dt: m.become(self.get_angle_label(vec_r, angle_tracker.get_value(), 100,
            False, 2, 1.3, m=m)), call_updater=True)

        group_r = VGroup(circle_r, labels_r, vec_r, angle_label_r, dashes_r)

        circle_l = Circle(radius=1.5, color=ANIM_BLACK).shift(LEFT*4.5+DOWN*0.8)
        labels_l = self.get_labels(tmp_circ, labels=["0, 400", "50", "100", "150", "200", "250", "300", "350"])
        dashes_l = self.get_dashes(circle_l)
        vec_l = self.get_arrow(circle_l, angle_tracker)
        angle_label_l = VMobject().add_updater(lambda m, dt: m.become(self.get_angle_label(vec_l, angle_tracker.get_value(), 400,
            False, 2, 1.3, m=m)), call_updater=True)

        group_l = VGroup(circle_l, labels_l, vec_l, angle_label_l, dashes_l)

        ##########################
        
        self.add(get_background())

        self.add(circle, dasher)
        self.wait(0.5)
        self.play(radius_tracker.animate.set_value(end_radius), run_time=2)
        vec = self.get_arrow(circle, angle_tracker=angle_tracker, radius_tracker=radius_tracker)
        angle_label = self.get_angle_label(vec, angle_tracker.get_value(), 360).add_updater(lambda m: m.become(
            self.get_angle_label(vec, angle_tracker.get_value(), 360)
        ))
        vec.update()
        vec.suspend_updating()
        vec.resume_updating()
        circle.update()
        angle_label.update()
        self.wait(0.5)
        vec.suspend_updating()
        self.play(GrowArrow(vec))
        vec.resume_updating()
        self.wait(0.5)
        self.play(FadeIn(timer[0][0], timer[1]), run_time=2)
        self.wait(0.3)
        Timer.animate(self, timer)
        self.wait(0.5)
        angle_label.suspend_updating()
        angle_label_copy = angle_label.copy().clear_updaters()
        self.play(Write(angle_label_copy))
        self.wait()
        self.play(FadeOut(angle_label_copy))
        self.wait(0.5)

        dasher.resume_updating()
        self.play(angle_tracker.animate().set_value(0), run_time=5.3)
        self.wait(0.5)
        angle_label.resume_updating()
        angle_label.update()
        angle_label.suspend_updating()
        self.play(FadeIn(angle_label))
        angle_label.resume_updating()
        self.wait(0.7)
        self.play(angle_tracker.animate().set_value(400), run_time=5.3)
        self.wait(0.5)
        dasher.clear_updaters()
        self.play(angle_tracker.animate.set_value(360), run_time=2)
        angle_tracker.set_value(0)
        self.wait(0.5)
        self.play(angle_tracker.animate().set_value(-40), run_time=2)
        self.wait(0.5)
        self.play(angle_tracker.animate().set_value(0), run_time=2)
        self.wait(0.5)
        self.play(angle_tracker.animate().set_value(40), run_time=2.5)
        self.wait(0.5)
        for i in labels:
            i.suspend_updating()
        dasher.clear_updaters()
        angle_label.clear_updaters()
        self.wait(0.5)

        # angle_tracker.set_value(40)
        angle_label.add_updater(lambda m: m.become(
            self.get_angle_label(vec, angle_tracker.get_value(), 360, decimal_places=2, scaling=1.3, m=m)))
        
        # Move zooming frame to the angle_label
        frame.move_to(angle_label) 

        self.play(Create(frame))
        self.activate_zooming()
        self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera)
        self.wait(0.5)
        self.play(angle_tracker.animate(rate_func=linear).set_value(39), run_time=2)
        self.play(angle_tracker.animate(rate_func=linear).set_value(40), run_time=2)
        self.wait(0.5)
        self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera, rate_func=lambda t: smooth(1 - t))
        self.play(Uncreate(zoomed_display_frame), FadeOut(frame))
        self.wait(0.5)

        objs_w_updaters = [vec_l, vec_r, angle_label_l, angle_label_r]

        for i in objs_w_updaters:
            i.suspend_updating()

        tmp_label = labels.copy()
        tmp_ang_label = angle_label.copy()

        tmp_ang_r = Text("11.11", font="Segoe UI Light", color=ANIM_ORANGE, stroke_width=1).scale(0.3).move_to(angle_label)
        tmp_ang_l = Text("44.44", font="Segoe UI Light", color=ANIM_ORANGE, stroke_width=1).scale(0.3).move_to(angle_label)
        for i in [tmp_ang_l, tmp_ang_r, *objs_w_updaters]:
            i.resume_updating()
            i.update()
            i.suspend_updating()
            i.update()

        self.play(ReplacementTransform(labels, labels1), ReplacementTransform(angle_label, tmp_ang_r), run_time=1.5)
        self.wait(0.5)
        self.play(ReplacementTransform(labels1, labels2), ReplacementTransform(tmp_ang_r, tmp_ang_l), run_time=1.5)
        self.wait(0.5)
        self.play(ReplacementTransform(labels2, tmp_label), ReplacementTransform(tmp_ang_l, tmp_ang_label), run_time=1.5)
        self.wait(0.5)

        tmp_ang_label.clear_updaters()
        tmp_ang_label.add_updater(lambda m, dt: m.become(self.get_angle_label(vec, angle_tracker.get_value(), 360, m=m)),
            call_updater=True)

        labels_r.shift(RIGHT*4.5+DOWN*0.8)
        labels_l.shift(LEFT*4.5+DOWN*0.8)
        labels.clear_updaters()
        small_labels.clear_updaters()

        for i in [tmp_ang_l, tmp_ang_r, *objs_w_updaters]:
            i.update()
            i.resume_updating()
            i.update()
            i.suspend_updating()
            i.update()

        self.play(FadeIn(group_r, group_l), radius_tracker.animate.set_value(1.5), TransformMatchingShapes(dashes, small_dashes),
            ReplacementTransform(tmp_label, small_labels), run_time=2)
        self.play(VGroup(
            circle.clear_updaters(),
            small_dashes,
            small_labels
            ).animate.shift(UP*1.2),
            run_time=1.2
            )
        self.wait(0.5)

        for i in objs_w_updaters:
            i.resume_updating()

        self.play(angle_tracker.animate.set_value(400), run_time=4)
        self.wait(0.5)

        self.play(angle_tracker.animate.set_value(360), run_time=2)
        angle_label.clear_updaters()
        angle_label_l.clear_updaters()
        angle_label_r.clear_updaters()
        tmp_ang_label.clear_updaters()
        # self.play(FadeOut(angle_label_l, angle_label_r, tmp_ang_label), run_time=0.8)
        self.wait(0.5)
        
        #############

    def get_arrow(self, circle, angle_tracker=None, radius_tracker=None):
        r = radius_tracker.get_value if radius_tracker else lambda: circle.radius

        angle = angle_tracker.get_value() * DEGREES if angle_tracker else 0
        p = circle.get_center

        a = angle_tracker.get_value

        arrow = Arrow(
            start=p(),
            end=(p()[0] + np.cos(angle)*r(), p()[1] + np.sin(angle)*r(), 0),
            color=ANIM_ORANGE,
            tip_length=0.2,
            buff=0)

        arrow.add_updater(lambda m: m.become(
            Arrow(
            start=p(),
            end=(p()[0] + np.cos(a()*DEGREES)*r(), p()[1] + np.sin(a()*DEGREES)*r(), 0),
            color=ANIM_ORANGE,
            tip_length=0.2,
            buff=0))
            )

        return arrow

    def get_dashes(self, circle, offset1=0.05, offset2=0.06):
        p = circle.get_center()
        r = circle.radius
        r -= offset1
        
        dashes = VGroup()

        thick_angles = [0, 90, 180, 270]
        middle_angles = range(0, 360, 10)

        for i in range(0, 360):
            a = i * DEGREES
            thick = int(i in thick_angles)
            middle = int(i in middle_angles)

            if thick:
                r -= offset2
            
            elif middle:
                r -= offset2 / 2

            dash = Line(stroke_width=1 + max(thick*1.5, middle/2), color=ANIM_BLACK, z_index=-10)
            dash.set_length(0.07 + max(0.18*thick, 0.1*middle)).rotate(a)
            dash.move_to((p[0] + np.cos(a) * r, p[1] + np.sin(a) * r, 0))
            dashes.add(dash)

            r = circle.radius - offset1

        return dashes

    def get_labels(self, circle, labels=["0°, 360°", "90°", "180°", "270°"]):
        labels_text = VGroup()
        dirs = [RIGHT, UP, LEFT, DOWN] if len(labels) == 4 else [RIGHT, UR, UP, UL, LEFT, DL, DOWN, DR]
        for n, (i, d) in enumerate(zip(labels, dirs)):
            negative_buff = len(labels) != 4 and n % 2 != 0
            labels_text.add(
                Text(i, font="Segoe UI Light", color=TEXT_COLOR, stroke_width=1).scale(0.34).next_to(circle.get_edge_center(d), d, buff=-0.35 if negative_buff else 0.22)
                )

        return labels_text

    def get_angle_label(self, arrow, angle, max_angle, is_degree=True, decimal_places=0, scaling=1.29, m=None):
        angle_cut = angle % 360
        custom_angle = round(angle_cut * max_angle / 360, decimal_places if decimal_places else None)
        if angle < 0:
            custom_angle = round(angle, decimal_places if decimal_places else None)
        if custom_angle == 0:
            return VMobject()
        string = str(custom_angle)
        if is_degree:
            string += "°"
        pos = arrow.copy().scale(scaling).get_end()
        label = Text(string, font="Segoe UI Light", color=ANIM_ORANGE, stroke_width=1).scale(0.32)
        return label.move_to(pos)

class RadianWarning(Scene):
    def construct(self):

        scale_factor = 0.4
        warning = Text("Warning:", font="Segoe UI Light", color="#FF0000").scale(scale_factor)
        rads = Text("Radians Are Counter-Intuitive", font="Segoe UI Light", color="#FF0000").scale(scale_factor)

        group = VGroup(warning, rads).arrange(DOWN, buff=0.1).center()
        
        self.add(get_background())
        self.play(GrowFromCenter(group))
        self.wait(0.5)
        self.play(FadeOut(group))
        self.play(FadeIn(group))
        self.play(FadeOut(group))
        #self.play(ShrinkToCenter(group))
        #self.wait(2)

class RadianExplanation101(Scene):
    def construct(self):
        
        angle_tracker_1 = ValueTracker(0)
        angle_tracker_2 = ValueTracker(1)

        x_tracker = ValueTracker(0)
        x_tracker_2 = ValueTracker(1.5)

        rad_tracker = ValueTracker(1)

        circle_1 = RadianCircle.get_circle_and_objs(1, 5, False, ORIGIN, angle_tracker_1, False, x_tracker)

        circle_2 = RadianCircle.get_circle_and_objs(1, 10, False, RIGHT*1.5, angle_tracker_2, False, x_tracker_2, radius_tracker=rad_tracker)

        circles = VGroup(circle_1, circle_2)

        timer = Timer.create_timer()

        arcs_1, labels_1 = self.get_radian_arcs(1, (-3, 0, 0))
        arcs_2, labels_2 = self.get_radian_arcs(2, (2.5, 0, 0), scale_factor=1.2)

        change_color = ANIM_AQUA

        arcs_1_copy = arcs_1.copy().set_color(change_color)
        arcs_2_copy = arcs_2.copy().set_color(change_color)

        arcs_1_copy.z_index = 1000
        arcs_2_copy.z_index = 1000

        equation = MathTex(r"C\,=\,2\pi r\,=\, \pi d", color=TEXT_COLOR).scale(0.9).to_edge(DOWN, buff=0.8)

        self.add(get_background())

        circle, fixed_segment, rotating_segment, theta, dot, center_dot, arc_arrow, label_radius_tex, label_distance = circle_1

        circle.suspend_updating()

        self.play(FadeIn(circle))
        circle.resume_updating()
        self.wait(0.5)

        dot.suspend_updating()
        arc_arrow.suspend_updating()

        self.play(FadeIn(dot, arc_arrow), run_time=0.7)
        arc_arrow.resume_updating()
        self.play(angle_tracker_1.animate.set_value(1), run_time=4)
        self.wait(0.5)

        for i in [rotating_segment, fixed_segment, center_dot, theta]:
            i.update()
            i.set_opacity(0)
            self.add(i)
            i.suspend_updating()
        circle_2[0].suspend_updating()

        self.play(VGroup(center_dot, fixed_segment, theta, rotating_segment).animate.set_opacity(1))

        for i in circle_1[:-2]:
            i.resume_updating()

        self.wait(0.5)
        self.play(x_tracker.animate.set_value(-2), FadeIn(circle_2[0]))
        self.wait(0.5)
        self.play(rad_tracker.animate.set_value(2))
        self.wait(0.5)
        
        for i in [label_distance, label_radius_tex, circle_2[1:]]:
            i.update()
            i.set_opacity(0)
            self.add(i)
            i.suspend_updating()

        self.play(VGroup(label_radius_tex, label_distance, *circle_2[1:6], *circle_2[7:]).animate.set_opacity(1),
            circle_2[6].animate.set_stroke(opacity=1))

        for i in [label_distance, label_radius_tex, *circle_2[1:]]:
            i.resume_updating()

        self.wait()
        self.play(angle_tracker_1.animate.set_value(4), angle_tracker_2.animate.set_value(2), run_time=2.5)
        self.wait()
        self.play(angle_tracker_1.animate.set_value(1), angle_tracker_2.animate.set_value(1), run_time=1.5)
        # This is to increase render speed
        circles.update()
        circles.suspend_updating()
        self.wait()
        rad_title = Text('1 radian', font='Segoe UI Light').scale(0.8).shift(3 * DOWN).set_color(TEXT_COLOR)
        self.play(FadeIn(rad_title))
        self.wait(2)

        for i in range(2, 4):
            # This is to increase render speed
            circles.resume_updating()

            self.play(angle_tracker_1.animate.set_value(i), angle_tracker_2.animate.set_value(i), FadeOut(rad_title))
            rad_title = Text(str(i) + ' radians', font='Segoe UI Light').scale(0.8).shift(3 * DOWN).set_color(TEXT_COLOR)
            
            # This is to increase render speed
            circles.update()
            circles.suspend_updating()

            self.play(FadeIn(rad_title))
            self.wait(2)

        # This is to increase render speed
        circles.resume_updating()

        circles.update()
        label_distance.suspend_updating()
        circle_2[-1].suspend_updating()

        self.play(
            VGroup(label_distance, circle_2[-1]).animate(run_time=0.5).set_opacity(0),
            angle_tracker_1.animate.set_value(6.28),
            angle_tracker_2.animate.set_value(6.28),
            FadeOut(rad_title),
            run_time=2.5)
        
        self.remove(label_distance, circle_2[-1])
        
        circles.update()
        circles.suspend_updating()

        self.play(FadeIn(timer[0][0], timer[1]))
        self.wait(0.5)
        Timer.animate(self, timer)
        self.wait()

        circles.resume_updating()

        self.play(Write(equation), run_time=2)
        self.wait()
        self.play(
            x_tracker.animate.set_value(-3),
            x_tracker_2.animate.set_value(2.5),
            run_time=1.5
            )

        circles.update()
        circles.suspend_updating()

        self.wait(0.5)
        w1 = arcs_1.width
        w2 = arcs_2.width
        arcs_1.scale_to_fit_width(2)
        arcs_2.scale_to_fit_width(4)
        self.add(arcs_1, arcs_2)
        self.play(
            arcs_1.animate.scale_to_fit_width(w1),
            arcs_2.animate.scale_to_fit_width(w2),
            FadeOut(arc_arrow, circle_2[6], theta, circle_2[3], label_radius_tex, circle_2[-2], run_time=0.5),
            run_time=2
            )
        self.add(arc_arrow, circle_2[6], theta, circle_2[3])
        angle_tracker_1.set_value(0)
        angle_tracker_2.set_value(0)
        circles.update()
        self.play(FadeIn(labels_1, labels_2))
        self.wait()
        
        for j, i in enumerate([*range(1, 7), 6.28]):
            circles.resume_updating()
            self.play(
                angle_tracker_1.animate.set_value(i),
                angle_tracker_2.animate.set_value(i), 
                Create(arcs_1_copy[j]),
                Create(arcs_2_copy[j]),
                labels_1[j].animate.set_color(change_color),
                labels_2[j].animate.set_color(change_color),
                run_time=1.5
                )
            circles.update()
            circles.suspend_updating()
            self.wait()

    def get_radian_arcs(self, radius, center, scale_factor=1.4):
        def get_points(ang1, ang2):
            return [
                (x + np.cos(ang1) * radius, y + np.sin(ang1) * radius, 0),
                (x + np.cos(ang2-0.1) * radius, y + np.sin(ang2-0.1) * radius, 0)
            ]

        radius *= scale_factor

        x, y = center[:2]

        arcs = VGroup(*[ArcBetweenPoints(*get_points(i, i+1), angle=0.9, color=ANIM_ORANGE) for i in range(6)])
        arcs.add(ArcBetweenPoints(*get_points(6, 6.28), angle=0.18, color=ANIM_ORANGE))

        labels = VGroup(
            *[
                Text(str(i), font="Segoe UI Light", color=ANIM_ORANGE).scale(0.25).move_to(arcs[i-1].copy()
                    .scale(5/radius).point_from_proportion(0.5))
                for i in range(1, 7)
            ]
        )

        labels.add(Text(".28", font="Segoe UI Light", color=ANIM_ORANGE).scale(0.25).move_to(arcs[-1].copy()
                    .scale(50/radius).point_from_proportion(0.5)))

        return VGroup(arcs, labels)

class RadianDegreeConversion(Scene):
    def construct(self):
        
        tmp = PolarPlane()

        radian_values = range(0, 361, 45)[1:]

        radian_labels = [tmp.get_radian_label(i/360).get_tex_string() for i in radian_values]
        
        outer_labels_str = [r"0\,rad"]

        for label, value in zip(radian_labels, radian_values):
            outer_labels_str.append(label + r"\,=\," + str(round(np.deg2rad(value), 4)) + r"\,rad")

        circle = Circle(2, color=ANIM_BLACK)
        circle2 = Circle(circle.copy().scale(0.7).width/2, color=ANIM_BLACK).shift(RIGHT*2.5)

        d_ticks, d_inner_labels, d_outer_labels = TicksAndLabelsFromCircle.create_ticks_and_labels(
            circle=circle,
            label_angles=[i*DEGREES for i in range(0, 360, 45)],
            inner_labels=[str(i) + "°" for i in range(0, 360, 45)],
            outer_labels=outer_labels_str[:-1],
            full_turn_labels=("360°", outer_labels_str[-1])
        )

        outer_labels_deg_str = [str(round(np.rad2deg(i), 4)) + "°" for i in range(7)]
        outer_labels_deg_str[0] = "0°"
        outer_labels_deg_str.append("360°")

        r_ticks, r_inner_labels, r_outer_labels = TicksAndLabelsFromCircle.create_ticks_and_labels(
            circle=circle2,
            label_angles=range(7),
            inner_labels=[str(i) + r"\,rad" for i in range(7)],
            outer_labels=outer_labels_deg_str[:-1],
            full_turn_labels=(r"6.2832\,rad", outer_labels_deg_str[-1]),
            scale_factor=0.4*0.7
        )

        timer_1 = Timer.create_timer()
        timer_2 = Timer.create_timer()

        self.add(get_background())
        self.play(Create(circle), run_time=1.5)
        self.wait(0.5)
        for t, l in zip(d_ticks, d_inner_labels):
            self.play(Write(VGroup(t, l)), run_time=0.7)
            self.wait(0.7)
        self.play(Write(d_inner_labels[-1]), run_time=0.7)
        self.wait()
        self.play(Write(d_outer_labels[0]), run_time=1.5)
        self.wait()
        self.play(FadeIn(timer_1[0][0], timer_1[1]))
        self.wait(0.5)
        Timer.animate(self, timer_1)
        self.wait(0.5)
        for l in d_outer_labels[1:]:
            self.play(FadeIn(l), run_time=0.7)
            self.wait(0.4)
        self.wait()
        self.play(VGroup(circle, d_ticks, d_inner_labels, d_outer_labels).animate.scale(0.7).shift(LEFT*2.5),
            Create(circle2, run_time=1.5))
        self.wait()
        for t, l in zip(r_ticks, r_inner_labels):
            self.play(Write(VGroup(t, l)), run_time=0.7)
            self.wait(0.7)
        self.play(Write(r_inner_labels[-1]), run_time=0.7)
        self.wait()
        self.play(Write(VGroup(r_outer_labels[0], r_outer_labels[-1])), run_time=1.5)
        self.wait()
        self.play(FadeIn(timer_2[0][0], timer_2[1]))
        self.wait(0.5)
        Timer.animate(self, timer_2)
        self.wait(0.5)
        for l in r_outer_labels[1:-1]:
            self.play(FadeIn(l), run_time=0.7)
            self.wait(0.4)
        self.wait(2)
        self.play(FadeOut(VGroup(circle, d_ticks, d_inner_labels, d_outer_labels,
                                 circle2,r_ticks, r_inner_labels, r_outer_labels)))
        self.wait(2)

class RadianCalculation(Scene):
    def construct(self):
        
        angle_tracker = ValueTracker(PI/2)

        circles = [
            RadianCircle.get_circle_and_objs(1, coords=(i, 0, 0), tracker=angle_tracker, simplified=True, segment_color=ANIM_BLACK,
            circle_stroke_width=5)
            for i in range(-3, 4, 3)
            ]

        labels = [[r"90°"], [r"1/4"], [r"?", r"\,radians"]]
        
        labels_text_1 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(circles[j], DOWN, buff=0.7)
        for j, i in enumerate(labels)]

        equation = MathTex(r"{90°", r"\over 360°}", r"=", r"\frac{1}{4}", r"=", r"{?", r"\over 2\pi}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)

        eq1_1 = MathTex(r"{90°", r"\over 360°}", r"2\pi", r"=", r"\frac{1}{4}", r"2\pi", r"=", r"\,?", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)

        eq1_2 = MathTex(r"\frac{\pi}{2}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).move_to(eq1_1[4])

        equation2 = MathTex(r"{25°", r"\over 360°}", r"=", r"\frac{25}{360}", r"=", r"{\,?", r"\over 2\pi}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)

        eq2_0 = MathTex(r"{25°", r"\over 360°}", r"2\pi", r"=", r"\frac{25}{360}", r"2\pi", r"=", r"\,?", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)

        eq2_1 = MathTex(r"\frac{5}{72}", tex_template=segoe_template, color=TEXT_COLOR, stroke_width=0.5).scale(0.6).move_to(eq2_0[4])

        eq2_2 = MathTex(r"\frac{10\pi}{72}", tex_template=segoe_template, color=TEXT_COLOR, stroke_width=0.5).scale(0.6).move_to(eq2_1)

        eq2_3 = MathTex(r"\frac{5\pi}{36}", tex_template=segoe_template, color=TEXT_COLOR, stroke_width=0.5).scale(0.6).move_to(eq2_2)

        equation3 = MathTex(r"{?°", r"\over 360°}", r"=", r"\frac{2}{2\pi}", r"=", r"{2\, rad", r"\over 2\pi\,rad}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)
        
        eq3_1 = MathTex(r"?°", r"=", r"\frac{1}{\pi}", r"360°", r"=", r"{2\, rad", r"\over 2\pi\,rad}", r"360°", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).to_edge(UP, buff=1)

        eq3_2 = MathTex(r"\frac{1\, rad}{\pi\,rad}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.6).move_to(eq3_1[5:7])

        labels = [[r"25°"], [r"25/360"], [r"?", r"\,radians"]]
        
        labels_text_2 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(circles[j], DOWN, buff=0.7)
        for j, i in enumerate(labels)]

        labels = [[r"?°"], [r"2/2\pi"], [r"2\,radians"]]
        
        labels_text_3 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(circles[j], DOWN, buff=0.7)
        for j, i in enumerate(labels)]

        self.add(get_background())

        self.add(*circles, *labels_text_1)
        self.play(
            ReplacementTransform(labels_text_1[0].copy(), equation[0]),
            ReplacementTransform(labels_text_1[1].copy(), equation[3]),
            ReplacementTransform(labels_text_1[2][0].copy(), equation[5]),
            FadeIn(equation[1:3], equation[4], equation[6]),
            run_time=1.5
            )
        self.wait()
        self.play(
            TransformMatchingShapes(equation[:2], eq1_1[:2]),

            TransformMatchingShapes(equation[6].copy(), eq1_1[2], path_arc=0.5, fade_transform_mismatches=True),
            TransformMatchingShapes(equation[6], eq1_1[5], path_arc=0.5, fade_transform_mismatches=True),

            TransformMatchingShapes(equation[2], eq1_1[3]),
            TransformMatchingShapes(equation[3], eq1_1[4]),
            TransformMatchingShapes(equation[4], eq1_1[6]),
            TransformMatchingShapes(equation[5], eq1_1[7]),
            run_time=2
        )
        self.wait()
        self.play(
            ReplacementTransform(eq1_1[4:6], eq1_2),
            eq1_1[6:].animate.next_to(eq1_2, buff=0.1)
            )
        self.wait(2)
        equation1 = VGroup(eq1_1[:4], eq1_2, eq1_1[6:])
        self.play(FadeOut(equation1))
        self.play(
            angle_tracker.animate.set_value(25*DEGREES),
            ReplacementTransform(labels_text_1[0], labels_text_2[0]),
            ReplacementTransform(labels_text_1[1], labels_text_2[1]),
            run_time=1.7
            )
        self.wait()
        self.play(
            ReplacementTransform(labels_text_2[0].copy(), equation2[0]),
            ReplacementTransform(labels_text_2[1].copy(), equation2[3]),
            ReplacementTransform(labels_text_2[2][0].copy(), equation2[5]),
            FadeIn(equation2[1:3], equation2[4], equation2[6]),
            run_time=1.5
            )
        self.wait()
        self.play(
            TransformMatchingShapes(equation2[:2], eq2_0[:2]),

            TransformMatchingShapes(equation2[6].copy(), eq2_0[2], path_arc=0.5, fade_transform_mismatches=True),
            TransformMatchingShapes(equation2[6], eq2_0[5], path_arc=0.5, fade_transform_mismatches=True),

            TransformMatchingShapes(equation2[2], eq2_0[3]),
            TransformMatchingShapes(equation2[3], eq2_0[4]),
            TransformMatchingShapes(equation2[4], eq2_0[6]),
            TransformMatchingShapes(equation2[5], eq2_0[7]),
            run_time=2
        )
        self.wait()
        self.play(
            ReplacementTransform(eq2_0[4], eq2_1),
            eq2_0[:4].animate.next_to(eq2_1, LEFT, buff=0.1),
            eq2_0[5:].animate.next_to(eq2_1, buff=0.1),
        )
        self.wait()
        self.play(
            ReplacementTransform(VGroup(eq2_0[5], eq2_1), eq2_2),
            eq2_0[:4].animate.next_to(eq2_2, LEFT, buff=0.1),
            eq2_0[6:].animate.next_to(eq2_2, buff=0.1),
            run_time=1.2
        )
        self.wait()
        self.play(
            ReplacementTransform(eq2_2, eq2_3),
            eq2_0[:4].animate.next_to(eq2_3, LEFT, buff=0.1),
            eq2_0[6:].animate.next_to(eq2_3, buff=0.1),
            run_time=1.2
        )
        self.wait()
        equation2 = VGroup(eq2_0[:4], eq2_3, eq2_0[6:])
        self.wait(2)
        self.play(FadeOut(equation2))
        self.play(
            angle_tracker.animate.set_value(2),
            *[ReplacementTransform(i, j) for i, j in zip(labels_text_2[:2], labels_text_3[:2])],
            ReplacementTransform(labels_text_1[2], labels_text_3[2]),
            run_time=1.8
            )
        self.wait()
        self.play(
            ReplacementTransform(labels_text_3[0].copy(), equation3[0]),
            ReplacementTransform(labels_text_3[1].copy(), equation3[3]),
            ReplacementTransform(labels_text_3[2][0].copy(), equation3[5]),
            FadeIn(equation3[1:3], equation3[4], equation3[6]),
            run_time=1.5
            )
        self.wait()
        self.play(
            TransformMatchingShapes(equation3[0], eq3_1[0]),

            TransformMatchingShapes(equation3[1].copy(), eq3_1[3], path_arc=0.5, fade_transform_mismatches=True),
            TransformMatchingShapes(equation3[1], eq3_1[7], path_arc=0.5, fade_transform_mismatches=True),

            TransformMatchingShapes(equation3[2], eq3_1[1]),
            TransformMatchingShapes(equation3[3], eq3_1[2]),
            TransformMatchingShapes(equation3[4], eq3_1[4]),
            TransformMatchingShapes(equation3[5], eq3_1[5]),
            TransformMatchingShapes(equation3[6], eq3_1[6]),
            run_time=2
        )
        self.wait()
        self.play(
            TransformMatchingShapes(eq3_1[5:7], eq3_2),
            eq3_1[:5].animate.next_to(eq3_2, LEFT, buff=0.1),
            )
        self.wait()
        equation3 = VGroup(eq3_1[:5], eq3_2, eq3_1[7:])
        for i in circles:
            i.clear_updaters()
        self.play(FadeOut(equation3, *circles, *labels_text_3))
        self.wait()

class Circles0to6Rad(Scene):

    def construct(self):

        tracker =  ValueTracker(0)

        circle1 = RadianCircle.get_circle_and_objs(8/4, 10, False, ORIGIN, tracker)
        circle2 = RadianCircle.get_circle_and_objs(4.1/4, 5, False, (-4.5, 0, 0), tracker)
        circle3 = RadianCircle.get_circle_and_objs(4.1/4, 5, True, (4.5, 0, 0), tracker)

        circles = VGroup(circle1, circle2, circle3)

        self.add(get_background())

        self.add(circle1, circle2, circle3)
        circles.update()
        circles.suspend_updating()

        self.wait()

        self.play(Indicate(circle3[-1][0], color=ANIM_ORANGE, scale_factor=1.5), run_time=1.5)
        self.wait(0.3)
        self.play(Indicate(circle3[-1][2], color=ANIM_ORANGE, scale_factor=1.5), run_time=1.5)
        self.wait(0.3)
        self.play(Indicate(circle3[-1][4], color=ANIM_ORANGE, scale_factor=1.5), run_time=1.5)
        self.wait(0.3)
        self.wait()

        circles.resume_updating()

        self.play(tracker.animate.set_value(1), run_time=1.5)

        # This is to increase render speed
        circles.update()
        circles.suspend_updating()

        self.wait()
        rad_title = Text('1 radian', font='Segoe UI Light').scale(0.8).shift(3 * DOWN).set_color(TEXT_COLOR)
        self.play(FadeIn(rad_title))
        self.wait(2)
        self.should_update_mobjects()

        for i in range(2, 7):
            # This is to increase render speed
            circles.resume_updating()

            self.play(tracker.animate.set_value(i), FadeOut(rad_title), run_time=1.5)
            rad_title = Text(str(i) + ' radians', font='Segoe UI Light').scale(0.8).shift(3 * DOWN).set_color(TEXT_COLOR)
            
            # This is to increase render speed
            circles.update()
            circles.suspend_updating()

            self.play(FadeIn(rad_title))
            self.wait(2)

        circles.resume_updating()
        self.play(tracker.animate.set_value(6.28), FadeOut(rad_title))
        rad_title = Text('6.28 radians', font='Segoe UI Light').scale(0.8).shift(
            3 * DOWN).set_color(
            ANIM_BLACK)
        circles.update()
        circles.suspend_updating()
        self.play(FadeIn(rad_title))
        self.wait(2)

class EndAnimation(Scene):
    def construct(self):

        tmp = PolarPlane()

        tracker =  ValueTracker(6.28)

        circle1 = RadianCircle.get_circle_and_objs(8/4, 10, False, ORIGIN, tracker)
        circle2 = RadianCircle.get_circle_and_objs(4.1/4, 5, False, (-4.5, 0, 0), tracker)
        circle3 = RadianCircle.get_circle_and_objs(4.1/4, 5, True, (4.5, 0, 0), tracker)

        circles = VGroup(circle1, circle2, circle3)

        rad_title = Text('6.28 radians', font='Segoe UI Light').scale(0.8).shift(
            3 * DOWN).set_color(
            ANIM_BLACK)

        rad_title_2 = Text('1 radian', font='Segoe UI Light').scale(0.8).shift(
        3 * DOWN).set_color(
        ANIM_BLACK)

        radian_values = [i for i in range(0, 361, 15) if (((i-1)*15) % 30) != 0 or i in [45, 135, 225, 315]]

        radian_labels = [tmp.get_radian_label(i/360).get_tex_string() for i in radian_values[1:]]
        
        outer_labels_str = [r"0\,rad"]

        for label, value in zip(radian_labels, radian_values[1:]):
            outer_labels_str.append(label + r"\,=\," + str(round(np.deg2rad(value), 4)) + r"\,rad")

        circle = Circle(2, color=ANIM_BLACK)
        circle_r = circle.copy()
        d_labels = VGroup(*TicksAndLabelsFromCircle.create_ticks_and_labels(
            circle=circle,
            label_angles=[i*DEGREES for i in radian_values[:-1]],
            inner_labels=[str(i) + "°" for i in radian_values[:-1]],
            outer_labels=outer_labels_str[:-1],
            full_turn_labels=("360°", outer_labels_str[-1])
        ))

        outer_labels_deg_str = [str(round(np.rad2deg(i), 4)) + "°" for i in range(7)]
        outer_labels_deg_str[0] = "0°"
        outer_labels_deg_str.append("360°")

        r_labels = VGroup(*TicksAndLabelsFromCircle.create_ticks_and_labels(
            circle=circle_r,
            label_angles=range(7),
            inner_labels=[str(i) + r"\,rad" for i in range(7)],
            outer_labels=outer_labels_deg_str[:-1],
            full_turn_labels=(r"6.2832\,rad", outer_labels_deg_str[-1]),
            scale_factor=0.4
        ))

        a1 = ValueTracker(PI/2)
        a2 = ValueTracker(25*DEGREES)
        a3 = ValueTracker(2)

        group_circles = VGroup()

        for j, a in enumerate([a1, a2, a3]):
            circles_ = VGroup(*[
                RadianCircle.get_circle_and_objs(0.6, coords=(i, (1-j)*2.3, 0), tracker=a, simplified=True, segment_color=ANIM_BLACK,
                circle_stroke_width=5)
                for i in [-1.5, 0.5, 2.5]
                ])
            group_circles.add(circles_)

        group_circles.clear_updaters()

        group_circles.shift(RIGHT*0.3)

        labels = [[r"90°"], [r"1/4"], [r"?", r"\,radians"]]
        
        labels_text_1 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(group_circles[0][j], DOWN, buff=0.3)
        for j, i in enumerate(labels)]

        equation = MathTex(r"{90°", r"\over 360°}", r"=", r"\frac{1}{4}", r"=", r"{?", r"\over 2\pi}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.45).next_to(group_circles[0], buff=0.7)

        equation2 = MathTex(r"{25°", r"\over 360°}", r"=", r"\frac{5}{72}", r"=", r"{?", r"\over 2\pi}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.45).next_to(group_circles[1], buff=0.7)

        equation3 = MathTex(r"{?°", r"\over 360°}", r"=", r"\frac{1}{\pi}", r"=", r"{2\, rad", r"\over 2\pi\,rad}", tex_template=segoe_template,
            color=TEXT_COLOR, stroke_width=0.5).scale(0.45).next_to(group_circles[2], buff=0.7)

        labels = [[r"25°"], [r"25/360"], [r"?", r"\,radians"]]
        
        labels_text_2 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(group_circles[1][j], DOWN, buff=0.3)
        for j, i in enumerate(labels)]

        labels = [[r"?°"], [r"2/2\pi"], [r"2\,radians"]]
        
        labels_text_3 = [MathTex(*i, tex_template=segoe_template, color=TEXT_COLOR).scale(0.5).next_to(group_circles[2][j], DOWN, buff=0.3)
        for j, i in enumerate(labels)]

        self.add(get_background())
        
        self.add(circles, rad_title)
        self.play(
            tracker.animate.set_value(1),
            ReplacementTransform(rad_title, rad_title_2),
            run_time=2
            )
        circles.clear_updaters()
        self.wait()
        self.play(VGroup(circles, rad_title_2).animate.scale(0.3).to_corner(UL).to_edge(LEFT, buff=(config.frame_width/2 - equation3.get_right()[0])))
        self.wait()
        self.play(FadeIn(circle, d_labels))
        self.wait()
        self.play(VGroup(circle, d_labels).animate.scale(0.5).to_edge(LEFT, buff=(config.frame_width/2 - equation3.get_right()[0])).shift(UP*0.2))
        self.wait()
        self.play(FadeIn(circle_r, r_labels))
        self.wait()
        self.play(VGroup(circle_r, r_labels).animate.scale(0.5).to_corner(DL).to_edge(LEFT, buff=(config.frame_width/2 - equation3.get_right()[0])).set_x(circle.get_x()))
        self.wait()
        for c, l, e in zip(group_circles, [labels_text_1, labels_text_2, labels_text_3], [equation, equation2, equation3]):
            self.play(FadeIn(c, *l))
            self.wait()
            self.play(FadeIn(e))
            self.wait()
