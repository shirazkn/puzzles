import manim as man
import numpy as np
from copy import deepcopy

"""
NOTE: UNFORTUNATELY THIS IS BROKEN FOR RECENT VERSIONS OF MANIM. NEED TO REPLACE SOME OF THESE METHODS WITH THEIR
NON-DEPRECATED VERSIONS IN MANIM-CE
SEE ./MEDIA FOR EXAMPLES OF WHAT ONCE WAS

A quick low-res animation can be rendered using: `python3 -m manim -pql game_of_life.py GridScene` from command line
Useful flags:
-s : Skip to last frame (Exports a png)
-p : Preview (Opens the video when done)
-l : Low-res rendering

File is saved in the working directory, in `./media/`
"""

CELL_SIZE = 2
LINE_WIDTH_MULTIPLE = 0.001  # Seems fairly well suited for 10x10 to 500x500

ANIMATION_SPEED = 0.07  # Lower is faster.
GRID_SIZE_VERTICAL = 30
GRID_SIZE_HORIZONTAL = 30
DIAGONAL_LINE = np.array([1, 1, 0])


class simul:
    def set_stage(self):
        '''For now it builds a 10 cell row.
        Change this for different starting
        structures.'''
        grid = np.zeros((GRID_SIZE_VERTICAL, GRID_SIZE_HORIZONTAL))
        a = []
        for i in range(10):
            a.append([15, 10 + i])
            grid[15][10 + i] = 1
        return (grid, a)

    def neighbours(self, element, grid):
        '''First argument takes the indices of the
        requested element ((vertical,horizontal)),
        second argument is the array the element
        resides in.'''
        x = element[0]
        y = element[1]
        order = (len(grid), len(grid[0]))
        _i = order[0]
        _j = order[1]
        howdy = []
        for i in range(3):
            a = x - 1 + i
            if a < 0 or a == _i:
                continue
            for j in range(3):
                b = y - 1 + j
                if b < 0 or b == _j or (b == y and a == x):
                    continue
                howdy.append(grid[a, b])
        return howdy

    # 0,0
    #
    #
    #
    #
    # _i, 0                         _i, _j

    def gstep(self, grid):
        '''Performs one step of the game of life
        on array. For use on arrays with binary
        elements only. Returns (output array,
        elements that were flipped in input array)'''
        grid_copy = deepcopy(grid)

        a = []
        for i in range(len(grid_copy)):
            for j in range(len(grid_copy[i])):

                chck = simul().neighbours([i, j], grid)
                _chck_ = chck.count(1)
                if (_chck_ == 2 or _chck_ == 3) and grid[i][j] == 1:
                    pass
                elif _chck_ == 3 and grid[i][j] == 0:
                    a.append([i, j])
                    grid_copy[i][j] = 1
                else:
                    if grid[i][j] == 1:
                        a.append([i, j])
                    grid_copy[i][j] = 0
        return (grid_copy, a)  # buffer is a final array, res is a list of coordinates of cells flipped


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

        # for i in range(5):
        # Example of how game of life animation works...
        # self.example_game()

        stage = simul().set_stage()   # stage = (grid, list of flips)
        for i in range(20):
            # is a new addition, step right up!
            self.anim_gol(stage[1])
            # import pdb; pdb.set_trace()
            stage = simul().gstep(stage[0])

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
            self.grid[i][j].shift(man.RIGHT * CELL_SIZE * j + man.UP * CELL_SIZE * i + 0.5 * CELL_SIZE * DIAGONAL_LINE)
            animation = man.ShowCreation(self.grid[i][j], run_time=ANIMATION_SPEED)

        return animation

    def set_grid_size(self, _m, _n):
        self.m = _m
        self.n = _n

    def resize_camera(self):
        """
        Keeps things within the frame (retaining aspect ratio)
        """
        self.camera.set_frame_center(np.array([self.n * CELL_SIZE * 0.5, self.m * CELL_SIZE * 0.5, 0.0]))
        self.camera.set_frame_height(self.m * CELL_SIZE + 2 * CELL_SIZE)
        self.camera.set_frame_width(self.n * CELL_SIZE + 2 * CELL_SIZE)
        self.camera.resize_frame_shape(fixed_dimension=(1.78 * self.m > self.n))
        self.camera.cairo_line_width_multiple = LINE_WIDTH_MULTIPLE

    def create_empty_grid(self):
        for i in range(self.m):
            self.grid.append([None for _ in range(self.n)])

        all_lines = man.VGroup()
        for i in range(self.m + 1):
            all_lines.add(
                man.Line([0, i * CELL_SIZE, 0], [self.n * CELL_SIZE, i * CELL_SIZE, 0], color=man.COLOR_MAP["WHITE"]))

        for i in range(self.n + 1):
            all_lines.add(
                man.Line([i * CELL_SIZE, 0, 0], [i * CELL_SIZE, self.m * CELL_SIZE, 0], color=man.COLOR_MAP["WHITE"]))

        self.add(all_lines)
        self.wait(ANIMATION_SPEED * 2)

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

    def anim_gol(self, lis_):
        animations = []
        for i in range(len(lis_)):
            animations.append(self.flip_cell(lis_[i][0], lis_[i][1]))
        self.play(*animations)