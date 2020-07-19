import manimlib.imports as man
import numpy as np

"""
A quick low-res animation can be rendered using: `manim animations.py GridScene -pl` from command line
Useful flags:
-s : Skip to last frame
-p : Preview (Opens the video when done)
-l : Low-res rendering
 
File is saved in the working directory, in `./media/`
(I think) `--media-dir` flag can be used for changing export directory.
"""

CELL_SIZE = 2  # Don't change this, something's not right. It works with 2.
LINE_WIDTH_MULTIPLE = 0.001  # Seems fairly well suited for 100x100

ANIMATION_SPEED = 0.2
GRID_SIZE_HORIZONTAL = 50
GRID_SIZE_VERTICAL = 50


class GridScene(man.Scene):
    def __init__(self, *args, **kwargs):
        self.m = None  # Vertical axis
        self.n = None  # Horizontal axis
        self.grid = []  # 2D list of cells (as VMObjects)
        self.grid_status = []  # Keeps track of whether a cell is on or off
        self.all_cells = None  # Group which contain all VMObjects
        super(GridScene, self).__init__(*args, **kwargs)

    def construct(self):
        """
        Is the 'main' function called by Manim first
        """
        self.set_grid_size(GRID_SIZE_HORIZONTAL, GRID_SIZE_VERTICAL)
        self.resize_camera()
        self.create_empty_grid()

        for i in range(5):
            # Example of how game of life animation works...
            self.example_game()

        # Fade out (Removed cus it takes too long)
        # self.play(man.FadeOut(self.all_cells))

    def flip_cell(self, i, j):
        """
        Flips a cell
        :param i, j: coordinates of cell, int
        :return: Transform object instance, to be fed into `play` function
        """
        new_opacity = 0 if self.grid_status[i][j] else 1
        new_cell = man.Rectangle(height=CELL_SIZE, width=CELL_SIZE)
        new_cell.set_fill(man.COLOR_MAP["RED_C"], opacity=new_opacity)
        new_cell.shift(man.RIGHT*CELL_SIZE*j + man.UP*CELL_SIZE*i)

        self.grid_status[i][j] = (self.grid_status[i][j] + 1) % 2
        return man.Transform(self.grid[i][j], new_cell, run_time=ANIMATION_SPEED)

    def set_grid_size(self, _m, _n):
        self.m = _m
        self.n = _n

    def resize_camera(self):
        """
        Keemps thimgs in d frame :-)
        """
        self.camera.set_frame_center(np.array([self.n * CELL_SIZE * 0.5 - 1, self.m * CELL_SIZE * 0.5 - 1, 0.0]))
        self.camera.set_frame_height(self.m * CELL_SIZE + CELL_SIZE)
        self.camera.set_frame_width(self.n * CELL_SIZE + CELL_SIZE)
        self.camera.resize_frame_shape(fixed_dimension=1)
        self.camera.cairo_line_width_multiple = LINE_WIDTH_MULTIPLE

    def create_empty_grid(self):
        self.all_cells = man.VGroup()

        for i in range(self.m):
            self.grid.append([])
            self.grid_status.append([])

            for j in range(self.n):
                self.grid[-1].append(man.Rectangle(height=CELL_SIZE, width=CELL_SIZE))
                self.grid[-1][-1].shift(man.RIGHT*CELL_SIZE*j + man.UP*CELL_SIZE*i)

                self.grid_status[-1].append(0)
                self.all_cells.add(self.grid[-1][-1])

        self.play(man.ShowCreation(self.all_cells))

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
        animations.append(self.flip_cell(2, 2))
        animations.append(self.flip_cell(2, 1))
        self.play(*animations)

        # The * unpacks the list as if they're separate arguments...
        # Same as self.play(animations[0], animations[1]...)
        # I believe they must be fed into the play function together in order for simultaneous animation


