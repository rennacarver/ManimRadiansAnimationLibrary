from re import M
from manim import *

#   for scene 'Circles0to6Rad' in manim CE v0.8.0
#   navigate to /manim/mobject/geometry.py
#   comment out line 140 "self.reset_endpoints_based_on_top(tip, at_start)"

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
    background = Rectangle(
            width=config["frame_width"],
            height=config["frame_width"],
            stroke_width=0,
            fill_color=color.color_gradient(["#D5D4C9","#DBD7CF"], 32),
            fill_opacity=1, z_index=-1000)
    return background

class Compass():
    @classmethod
    def create_compass(self, labels=None, coords=ORIGIN, rotation=0):
        arrows = VGroup(*[DoubleArrow(start=LEFT*1.2, end=RIGHT*1.2, tip_length=.2, color=ANIM_BLACK, stroke_width=6, z_index=-10).rotate(PI/2 if i else 0) for i in range(2)])
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
    @classmethod
    def create_timer(self, seconds=5):
        numbers = [Text(str(i), color=TEXT_COLOR, font="Segoe UI Light").scale(0.4) for i in range(seconds+1)]
        numbers.reverse()
        circle = Circle(radius=max(numbers[0].height, numbers[0].width)*1.5, color=ANIM_ORANGE, stroke_width=2).to_corner(DL).rotate(PI/2)
        for i in numbers:
            i.move_to(circle.get_center())

        return VGroup(VGroup(*numbers), circle)

    @classmethod
    def animate(self, renderer, timer):
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

class DashedCircles(Scene):
    #config.disable_caching = True
    def construct(self):
        def show_dashes_and_labels(angle):
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

        radius_tracker = ValueTracker(0.925)
        angle_tracker = ValueTracker(40)

        end_radius = 1.5
        
        self.last_dashed_angle = int(angle_tracker.get_value()) - 1
        angles_w_labels = [0, 90, 180, 270]

        circle = Circle(radius=radius_tracker.get_value(), color=ANIM_BLACK).add_updater(
            lambda m: m.become(Circle(radius=radius_tracker.get_value(), color=ANIM_BLACK))
        )

        tmp_circ = Circle(radius=end_radius)

        dashes = self.get_dashes(tmp_circ)
        labels = self.get_labels(tmp_circ)

        labels1 = self.get_labels(tmp_circ, labels=["0, 100", "25", "50", "75"])
        labels2 = self.get_labels(tmp_circ, labels=["0, 400", "100", "200", "300"])

        vec = self.get_arrow(tmp_circ, angle_tracker=angle_tracker, radius_tracker=radius_tracker)
        timer = Timer.create_timer()

        angle_label = self.get_angle_label(vec, angle_tracker.get_value(), 360).add_updater(lambda m: m.become(
            self.get_angle_label(vec, angle_tracker.get_value(), 360)
        ))

        dasher = VMobject().add_updater(lambda m: show_dashes_and_labels(angle_tracker.get_value()))
        dasher.suspend_updating()

        circle_r = Circle(radius=end_radius, color=ANIM_BLACK).shift(RIGHT*4.5)
        labels_r = labels1.copy()
        dashes_r = self.get_dashes(circle_r)
        vec_r = self.get_arrow(circle_r, angle_tracker)
        angle_label_r = VMobject().add_updater(lambda m, dt: m.become(self.get_angle_label(vec_r, angle_tracker.get_value(), 100, False, 2, 1.3)), call_updater=True)

        group_r = VGroup(circle_r, labels_r, vec_r, angle_label_r, dashes_r)

        circle_l = Circle(radius=end_radius, color=ANIM_BLACK).shift(LEFT*4.5)
        labels_l = labels2.copy()
        dashes_l = self.get_dashes(circle_l)
        vec_l = self.get_arrow(circle_l, angle_tracker)
        angle_label_l = VMobject().add_updater(lambda m, dt: m.become(self.get_angle_label(vec_l, angle_tracker.get_value(), 400, False, 2, 1.3)), call_updater=True)

        group_l = VGroup(circle_l, labels_l, vec_l, angle_label_l, dashes_l)

        ##########################
        
        self.add(get_background())

        # radius_tracker.set_value(1.5)
        # vec.update()
        # circle.update()
        # angle_label.update()
        # self.add(circle, dashes, labels, angle_label, vec)
        # angle_label.clear_updaters()

        self.add(circle, dasher)
        self.wait(0.5)
        self.play(radius_tracker.animate.set_value(1.5), run_time=2)
        vec.update()
        circle.update()
        angle_label.update()
        self.wait(0.5)
        vec.suspend_updating()
        self.play(GrowArrow(vec))
        vec.resume_updating()
        self.wait(0.5)
        self.play(FadeIn(timer[0][0], timer[1]), run_time=0.8)
        self.wait(0.3)
        Timer.animate(self, timer)
        self.wait(0.5)
        angle_label.suspend_updating()
        self.play(Write(angle_label))
        angle_label.resume_updating()
        self.wait(0.5)

        dasher.resume_updating()
        self.play(angle_tracker.animate().set_value(400), run_time=5)
        for i in labels:
            i.suspend_updating()
        dasher.suspend_updating()
        angle_label.clear_updaters()
        self.wait(0.5)

        angle_tracker.set_value(40)
        angle_label.add_updater(lambda m: m.become(
            self.get_angle_label(vec, angle_tracker.get_value(), 360, decimal_places=2, scaling=1.3)))
        self.play(angle_tracker.animate(rate_func=linear).set_value(39), run_time=2)
        self.play(angle_tracker.animate(rate_func=linear).set_value(40), run_time=2)
        self.wait(0.5)

        objs_w_updaters = [vec_l, vec_r, angle_label_l, angle_label_r]

        for i in objs_w_updaters:
            i.suspend_updating()

        tmp_label = labels.copy()
        tmp_ang_label = angle_label.copy()

        tmp_ang_r = angle_label_r.copy().shift(LEFT*4.5)
        tmp_ang_l = angle_label_l.copy().shift(RIGHT*4.5)

        self.play(ReplacementTransform(labels, labels1), ReplacementTransform(angle_label, tmp_ang_r), run_time=1.5)
        self.wait(0.5)
        self.play(ReplacementTransform(labels1, labels2), ReplacementTransform(tmp_ang_r, tmp_ang_l), run_time=1.5)
        self.wait(0.5)
        self.play(ReplacementTransform(labels2, tmp_label), ReplacementTransform(tmp_ang_l, tmp_ang_label), run_time=1.5)
        self.wait(0.5)

        tmp_label = VMobject().add_updater(lambda m, dt: m.become(self.get_angle_label(vec_l, angle_tracker.get_value(), 360)), call_updater=True)

        labels_r.shift(RIGHT*4.5)
        labels_l.shift(LEFT*4.5)

        self.play(FadeIn(group_r, group_l), run_time=2)
        self.wait(0.5)

        for i in objs_w_updaters:
            i.resume_updating()

        self.play(angle_tracker.animate.set_value(100), run_time=2)
        self.wait(0.5)
        
    def get_arrow(self, circle, angle_tracker=None, radius_tracker=None):
        global radius, r
        if radius_tracker:
            r = radius_tracker.get_value
            radius = r()
        else:
            radius = circle.radius
            r = lambda: radius

        angle = angle_tracker.get_value() * DEGREES if angle_tracker else 0
        p = circle.get_center()

        a = angle_tracker.get_value

        arrow = Arrow(
            start=p,
            end=(p[0] + np.cos(angle)*radius, p[1] + np.sin(angle)*radius, 0),
            color=ANIM_ORANGE,
            tip_length=0.2,
            buff=0)

        arrow.add_updater(lambda m: m.become(
            Arrow(
            start=p,
            end=(p[0] + np.cos(a()*DEGREES)*r(), p[1] + np.sin(a()*DEGREES)*r(), 0),
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
        for i, d in zip(labels, [RIGHT, UP, LEFT, DOWN]):
            labels_text.add(Text(i, font="Segoe UI Light", color=TEXT_COLOR, stroke_width=1).scale(0.2).next_to(circle.get_edge_center(d), d, buff=0.3))

        return labels_text

    def get_angle_label(self, arrow, angle, max_angle, is_degree=True, decimal_places=0, scaling=1.2):
        angle = angle % max_angle
        custom_angle = round(angle * max_angle / 360, decimal_places if decimal_places else None)
        string = str(custom_angle)
        if is_degree:
            string += "°"
        pos = arrow.copy().scale(scaling).get_end()
        label = Text(string, font="Segoe UI Light", color=ANIM_ORANGE, stroke_width=1).scale(0.2)
        return label.move_to(pos)

class BigGridCompasses(Scene):
    def construct(self):
        buff = 0.5

        vertical_lines = VGroup(*[Line(UP*3.1, DOWN*3.1, color=ANIM_BLACK, stroke_width=2) for _ in range(16)]).arrange(buff=buff)
        horizontal_lines = VGroup(*[Line(LEFT*4, RIGHT*4, color=ANIM_BLACK, stroke_width=2) for _ in range(12)]).arrange(DOWN, buff=buff)

        grid = VGroup(vertical_lines, horizontal_lines)

        red_dot = Dot(point=(-buff*4.5, -buff*4.5, 0), radius=DEFAULT_DOT_RADIUS * 2, color=ANIM_ORANGE, z_index=1000)
        green_dot = Dot(point=(buff*6.5, buff*3.5, 0), radius=DEFAULT_DOT_RADIUS * 2, color=ANIM_AQUA, z_index=1000)

        panama = Tex("Panama", color=TEXT_COLOR).scale(0.5).next_to(red_dot, DOWN, buff=0.8).shift(LEFT*0.5)
        rotterdam = Tex("Rotterdam", color=TEXT_COLOR).scale(0.5).next_to(green_dot, UP, buff=1.5).shift(LEFT*0.5)

        grid_objs = VGroup(grid, green_dot, red_dot, panama, rotterdam)

        shift_factor = LEFT*2

        compass1 = Compass.create_compass(labels=["N", "S", "W", "E"], coords=RIGHT*4)
        compass2 = Compass.create_compass(labels=["NE", "SW", "NW", "SE"], coords=compass1[0])

        compasses = [Compass.create_compass(coords=compass1[0]) for _ in range(34)]

        vector = Arrow(start=red_dot.get_center(), end=(buff*5.5, buff*4.5, 0), tip_length=.2, color=ANIM_ORANGE,
            z_index=100, buff=0).shift(shift_factor)

        final_vector = Arrow(start=red_dot.get_center(), end=green_dot.get_corner(DL), tip_length=.2, color=ANIM_ORANGE,
            z_index=100, buff=0).shift(shift_factor)

        final_vector.get_tip().z_index = 100

        radius = 0.925

        circle = Circle(radius=radius, color=ANIM_BLACK, fill_opacity=1, z_index=-1).move_to(RIGHT*4)
        outer_circle = Circle(radius=radius, color=ANIM_BLACK, z_index=-1).move_to(RIGHT*4)

        tracker = ValueTracker(PI/4)

        radius += 0.025

        vec = Arrow(start=RIGHT*4, end=(4 + np.cos(tracker.get_value())*radius, np.sin(tracker.get_value())*radius, 0), color=ANIM_ORANGE, buff=0, z_index=1000,
            stroke_width=6, tip_length=0.2, max_stroke_width_to_length_ratio=6)

        vec.add_updater(lambda m: m.become(
            Arrow(start=outer_circle.get_center(), end=(outer_circle.get_x() + np.cos(tracker.get_value())*radius, np.sin(tracker.get_value())*radius, 0), color=ANIM_ORANGE, buff=0,
            z_index=1000, stroke_width=6, tip_length=0.2, max_stroke_width_to_length_ratio=6)))

        vec.suspend_updating()

        rectangle = Rectangle(height=buff*12.5, width=buff*16.5, color=ANIM_BLACK, fill_opacity=1, z_index=0).shift(shift_factor)

        grid_copy = grid.copy().shift(shift_factor)

        earth = Tex("Earth", color=TEXT_COLOR).scale(0.5).move_to(panama).shift(shift_factor)
        moon = Tex("Moon", color=TEXT_COLOR).scale(0.5).move_to(rotterdam).shift(shift_factor)

        copy_dots = [green_dot.copy().shift(UP*DEFAULT_DOT_RADIUS*3*i+LEFT*DEFAULT_DOT_RADIUS*3*i+shift_factor) for i in range(1, 3)]
        copy_dots = VGroup(*copy_dots)

        #self.add(grid, red_dot, green_dot, panama, rotterdam)

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
            self.play(c.animate.rotate(angle), run_time=0.5)
            self.wait(0.3)

        for j, c in enumerate(compasses[2:7]):
            initial_angle = -PI/4 - (PI/8) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/16
            angle *= -1 if j else 1
            self.play(c.animate.rotate(angle), run_time=0.25)
            self.wait(0.12)

        for j, c in enumerate(compasses[7:16]):
            initial_angle = -PI/4 - (PI/16) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/32
            angle *= -1 if j else 1
            self.play(c.animate.rotate(angle), run_time=0.1)
            self.wait(0.05)

        for j, c in enumerate(compasses[16:]):
            initial_angle = -PI/4 - (PI/32) * (j+1)
            self.add(c.rotate(initial_angle))

            angle = PI/64
            angle *= -1 if j else 1
            self.play(c.animate.rotate(angle), run_time=0.02)
            self.wait(0.01)

        self.wait(0.2)
        self.play(FadeOut(compass1[1], compass2[1]), FadeIn(circle))
        self.remove(*compasses, compass1[0], compass2[0])
        self.play(TransformMatchingShapes(circle, outer_circle))
        self.wait(0.5)
        vec.resume_updating()
        self.wait(0.5)
        self.play(tracker.animate.set_value(PI/4))
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
        self.play(tracker.animate.set_value(43*DEGREES), final_vector.animate.rotate(7*DEGREES, about_point=final_vector.get_start()))
        self.wait(0.5)
        self.play(Create(copy_dots))
        self.wait(0.5)
        self.remove(grid, grid_copy)
        self.play(FadeOut(earth, moon, final_vector, copy_dots, red_dot, green_dot, rectangle),
            outer_circle.animate.center())
        vec.clear_updaters()
        self.play(FadeOut(vec))
        self.wait(0.5)

class GridCompass(Scene):
    def construct(self):
        buff = 1.7

        vertical_lines = VGroup(*[Line(UP*3.2, DOWN*3.2, color=ANIM_BLACK) for _ in range(4)]).arrange(buff=buff)
        horizontal_lines = VGroup(*[Line(LEFT*3.2, RIGHT*3.2, color=ANIM_BLACK) for _ in range(4)]).arrange(DOWN, buff=buff)

        grid = VGroup(vertical_lines, horizontal_lines)

        red_dot = Dot(point=(-buff*1.5, -buff*1.5, 0), radius=DEFAULT_DOT_RADIUS * 3, color=ANIM_ORANGE, z_index=1000)
        green_dot = Dot(point=(buff*1.5, buff*1.5, 0), radius=DEFAULT_DOT_RADIUS * 3, color=ANIM_AQUA, z_index=1000)

        fifth = Tex("5th", color=TEXT_COLOR).scale(0.5).next_to(red_dot, LEFT, buff=1).shift(UP*0.2)
        roosevelt = Tex("Roosevelt", color=TEXT_COLOR).scale(0.5).next_to(red_dot, DOWN, buff=0.45).shift(LEFT*0.7)

        eighth = Tex("8th", color=TEXT_COLOR).scale(0.5).next_to(green_dot, RIGHT, buff=0.6).shift(UP*0.2)
        columbus = Tex("Columbus", color=TEXT_COLOR).scale(0.5).next_to(green_dot, UP, buff=0.5).shift(LEFT*0.7)

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

        # self.add(compass1)
        # self.add(grid_objs.shift(shift_factor))
        self.play(Create(grid), run_time=4)
        self.wait(0.5)
        self.play(Create(red_dot), run_time=0.5)
        self.wait(0.2)
        self.play(Write(VGroup(fifth, roosevelt)))
        self.wait(0.3)
        self.play(Create(green_dot), run_time=0.5)
        self.wait(0.2)
        self.play(Write(VGroup(eighth, columbus)))
        self.wait(0.5)
        self.play(Write(compass1), grid_objs.animate.shift(shift_factor))
        self.wait(0.5)
        for i in vectors:
            self.play(GrowArrow(i), run_time=0.7)
            self.wait(0.2)
        self.wait(0.5)
        self.play(FadeOut(grid_objs, compass1, vectors))
        self.wait(0.5)

class Circles0to6Rad(Scene):

    def construct(self):

        tracker =  ValueTracker(0)

        circle1 = self.get_circle_and_objs(8/4, 10, False, ORIGIN, tracker)
        circle2 = self.get_circle_and_objs(4.1/4, 5, False, (-4.5, 0, 0), tracker)
        circle3 = self.get_circle_and_objs(4.1/4, 5, True, (4.5, 0, 0), tracker)

        label_rad = Tex("radian", color=TEXT_COLOR)

        rad = Integer(1, color=TEXT_COLOR).next_to(label_rad, LEFT, 0.15).align_to(label_rad, DOWN)

        group = VGroup(rad, label_rad).set_color(TEXT_COLOR).next_to(circle1[0], DOWN).add_updater(lambda m: m.become(
            VGroup(rad, label_rad).arrange(buff=0.2).set_color(TEXT_COLOR).next_to(circle1[0], DOWN)
        ))

        self.add(get_background())

        #updates bottom title to plural or singular form depending on value
        radtitle_value = 0

        self.add(circle1, circle2, circle3)
        rad_title = Text(str(radtitle_value) + ' radians', font='Segoe UI Light').scale(0.8).shift(
            3 * DOWN).set_color(
            ANIM_BLACK)
        self.play(FadeIn(rad_title))
        self.wait(2)
        radtitle_value += 1

        for i in range(1, 7):
            if i == 1:
                self.play(tracker.animate.set_value(i), FadeOut(rad_title))
                rad_title = Text(str(radtitle_value) + ' radian', font='Segoe UI Light').scale(0.8).shift(
                    3 * DOWN).set_color(
                    ANIM_BLACK)
                self.play(FadeIn(rad_title))
            elif i > 1:
                self.play(tracker.animate.set_value(i), FadeOut(rad_title))
                rad_title = Text(str(radtitle_value) + ' radians', font='Segoe UI Light').scale(0.8).shift(
                    3 * DOWN).set_color(
                    ANIM_BLACK)
                self.play(FadeIn(rad_title))
            self.wait(2)
            radtitle_value += 1

        self.play(tracker.animate.set_value(6.28), FadeOut(rad_title))
        rad_title = Text('6.28 radians (2π)', font='Segoe UI Light').scale(0.8).shift(
            3 * DOWN).set_color(
            ANIM_BLACK)
        self.play(FadeIn(rad_title))
        self.wait(2)


    def get_circle_and_objs(self, radius: float, label_radius: int, use_letters: bool, coords: np.array, tracker: ValueTracker):
        """Returns the circle, labels & curved arrow"""

        def get_distance():
            return str(round(label_radius * tracker.get_value(), 1))

        def get_angle_label():
            theta = r"\theta \, = \, "

            distance = float(get_distance())

            if use_letters:
                if distance <= label_radius:
                    return MathTex(theta + r"\frac{s}{r}").set_color(TEXT_COLOR)

                tmp_frac = MathTex(theta + r"{", "6.28", r"r \over r}").set_color(TEXT_COLOR)

                text_rad =  DecimalNumber(tracker.get_value(), num_decimal_places=2).move_to(tmp_frac[1]).set_color(TEXT_COLOR)

                return VGroup(tmp_frac[0], text_rad, tmp_frac[2])

            tmp_frac = MathTex(theta, r"{", str(float(label_radius)), r"\over " + str(label_radius) + r"} \, = ")

            text_distance = DecimalNumber(distance, num_decimal_places=1).move_to(tmp_frac[2])

            text_rad =  DecimalNumber(tracker.get_value(), num_decimal_places=2).next_to(tmp_frac, buff=0.2)

            # rad = Tex("rad", color=TEXT_COLOR).next_to(text_rad, buff=0.2)
            rad = Tex("", color=TEXT_COLOR).next_to(text_rad, buff=0.2)

            return VGroup(tmp_frac[:2], text_distance, tmp_frac[3], text_rad, rad).set_color(TEXT_COLOR)

        def get_distance_label():
            label = None
            if use_letters:
                if float(get_distance()) <= label_radius:
                    label = MathTex("s")
                else:
                    label = VGroup(DecimalNumber(round(tracker.get_value(), 2), num_decimal_places=2),
                        Tex("r")).arrange(buff=0.15)
            else:
                dist = float(get_distance())
                label = DecimalNumber(dist, num_decimal_places=1)

            label.scale(0.5).set_color(ANIM_ORANGE)
            label.move_to(Arc(radius=radius+0.3, angle=tracker.get_value(), arc_center=coords).point_from_proportion(0.5))

            return label

        initial_angle = tracker.get_value()

        circle = Circle(radius=radius, color=ANIM_BLACK, stroke_width=3).move_to(coords)

        fixed_segment = Line(start=coords, end=circle.get_right(), color=ANIM_ORANGE)

        rotating_segment = Line(start=coords, end=(coords[0] + np.cos(initial_angle)*radius, coords[1] + np.sin(initial_angle)*radius, 0), color=ANIM_ORANGE).add_updater(
            lambda m: m.become(Line(start=coords, end=(coords[0] + np.cos(tracker.get_value())*radius, coords[1] + np.sin(tracker.get_value())*radius, 0), color=ANIM_ORANGE))
        )

        theta = MathTex(r"\theta", color=ANIM_ORANGE).scale(0.5).move_to(
            circle.get_right()
        )

        theta.add_updater(lambda m: m.move_to(
            Angle(
                fixed_segment, rotating_segment, radius=0.1 + 3 * SMALL_BUFF, other_angle=False
            ).point_from_proportion(0.5)
        ).set_opacity(1) if tracker.get_value() > 0.5 else lambda m: m.set_opacity(0))

        dot = Dot(circle.get_right(), color=ANIM_ORANGE)

        arc_arrow = Arc(radius=radius, angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=coords).add_updater(
            lambda m: m.become(Arc(radius=radius, angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=coords).add_tip(tip_length=0.1)
                if tracker.get_value() > 0.1 else Arc(radius=radius, angle=tracker.get_value(), color=ANIM_ORANGE, arc_center=coords))
        )

        label_rad = MathTex("r \ = \ " + str(label_radius) if not use_letters else "r", color=ANIM_ORANGE).scale(0.5).next_to(fixed_segment, DOWN)

        label_distance = get_distance_label().add_updater(lambda m: m.become(get_distance_label()))

        angle_label = get_angle_label().set_color(ANIM_BLACK).scale(0.6).next_to(circle, UP, buff=0.6).add_updater(lambda m: m.become(
            get_angle_label().set_color(ANIM_BLACK).scale(0.6).next_to(circle, UP, buff=0.6)
        ))

        group = VGroup(circle, fixed_segment, rotating_segment, theta, dot, arc_arrow, label_rad, label_distance, angle_label)

        return group
