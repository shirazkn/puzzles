import manimlib.imports as man
import numpy as np

"""
A quick low-res animation can be rendered using: `manim animations.py GridScene -pl` from command line
Useful flags:
-s : Skip to last frame (Exports a png)
-p : Preview (Opens the video when done)
-l : Low-res rendering
 
File is saved in the working directory, in `./media/`
(I think) `--media-dir` flag can be used for changing export directory.
"""

CELL_SIZE = 2
LINE_WIDTH_MULTIPLE = 0.001  # Seems fairly well suited for 10x10 to 500x500

ANIMATION_SPEED = 0.2  # Lower is faster.
GRID_SIZE_VERTICAL = 20
GRID_SIZE_HORIZONTAL = 20
DIAGONAL_LINE = np.array([1, 1, 0])


class GridScene(man.Scene):
    def __init__(self, *args, **kwargs):
        self.m = None  # Vertical length
        self.n = None  # Horizontal length
        self.grid = []  # 2D list of cells (as VMObjects)
        super(GridScene, self).__init__(*args, **kwargs)

    def construct(self):
        """
        Is the 'main' function called by Manim first
        """
        self.set_grid_size(GRID_SIZE_VERTICAL, GRID_SIZE_HORIZONTAL)
        self.resize_camera()
        self.create_empty_grid()

        for i in range(5):
            # Example of how game of life animation works...
            self.example_game()

    def flip_cell(self, i, j):
        """
        Flips a cell
        :param i, j: coordinates of cell, int
        :return: Transform object instance, to be fed into `play` function
        """
        if self.grid[i][j]:
            animation = man.FadeOut(self.grid[i][j], run_time=ANIMATION_SPEED)
            self.grid[i][j] = None

        else:
            self.grid[i][j] = man.Rectangle(height=CELL_SIZE, width=CELL_SIZE)
            self.grid[i][j].set_fill(man.COLOR_MAP["RED_C"], opacity=1.0)
            self.grid[i][j].shift(man.RIGHT*CELL_SIZE*j + man.UP*CELL_SIZE*i + 0.5*CELL_SIZE*DIAGONAL_LINE)
            animation = man.ShowCreation(self.grid[i][j], run_time=ANIMATION_SPEED)

        return animation

    def set_grid_size(self, _m, _n):
        self.m = _m
        self.n = _n

    def resize_camera(self):
        """
        Keeps things within the frame (retaining aspect ratio)
        """
        self.camera.set_frame_center(np.array([self.n*CELL_SIZE*0.5, self.m*CELL_SIZE*0.5, 0.0]))
        self.camera.set_frame_height(self.m * CELL_SIZE + 2*CELL_SIZE)
        self.camera.set_frame_width(self.n * CELL_SIZE + 2*CELL_SIZE)
        self.camera.resize_frame_shape(fixed_dimension=(1.78*self.m > self.n))
        self.camera.cairo_line_width_multiple = LINE_WIDTH_MULTIPLE

    def create_empty_grid(self):
        for i in range(self.m):
            self.grid.append([None for _ in range(self.n)])

        all_lines = man.VGroup()
        for i in range(self.m + 1):
            all_lines.add(man.Line([0, i*CELL_SIZE, 0], [self.n*CELL_SIZE, i*CELL_SIZE, 0], color=man.COLOR_MAP["WHITE"]))

        for i in range(self.n + 1):
            all_lines.add(man.Line([i*CELL_SIZE, 0, 0], [i*CELL_SIZE, self.m*CELL_SIZE, 0], color=man.COLOR_MAP["WHITE"]))

        self.add(all_lines)
        self.wait(ANIMATION_SPEED*2)

    def example_game(self):
        """
        An example of how the animation can be done
        """

        # First select which cells to flip
        animations = []
        animations.append(self.flip_cell(2, 2))
        animations.append(self.flip_cell(2, 3))

        # Then animate the flips for current time step
        self.play(*animations)

        # Similarly, in the next iteration
        animations = []
        animations.append(self.flip_cell(5, 6))
        animations.append(self.flip_cell(6, 7))
        self.play(*animations)

        # The * unpacks the list as if they're separate arguments...
        # Same as self.play(animations[0], animations[1]...)
        # I believe they must be fed into the play function together in order for simultaneous animation


