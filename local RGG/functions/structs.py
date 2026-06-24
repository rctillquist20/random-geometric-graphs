import heapq
import bisect
import numpy as np

def generate_rgg_with_grid(G, m, n):
    grid = {(r, c): [] for r in range(m) for c in range(n)}
    pos = {}

    for node in range(G.vcount()):
        coord = G.vs[node]["pos"]
        x, y = coord[0], coord[1]

        pos[node] = (x, y)

        col = min(int(x * n), n - 1)
        row = min(int(y * m), m - 1)
        grid[(row, col)].append(node)

    return grid

class UnitSquare:
  def __init__(self):
    self.vertical_cuts_x = [0.0,1.0]
    self.horizontal_cuts_y = [0.0,1.0]
    self.divisions = {}
    self.priority_queue = []
    self.add_new_division(0,0)

  def add_new_division(self,i,j):
    x0, x1 = self.vertical_cuts_x[i], self.vertical_cuts_x[i+1]
    y0, y1 = self.horizontal_cuts_y[j], self.horizontal_cuts_y[j+1]
    area = (x1 - x0) * (y1 - y0)
    self.divisions[(i,j)] = (area,(x0,x1,y0,y1))
    heapq.heappush(self.priority_queue,(-area,i,j))

  def pop_largest_division(self):
    while self.priority_queue:
      area,i,j = heapq.heappop(self.priority_queue)
      if (i,j) in self.divisions and -area == self.divisions[(i,j)][0]:
        return i,j
    return None

  def get_cut_direction(self,x0,x1,y0,y1):
    width = x1 - x0
    height = y1 - y0
    return 'vertical' if width>height else 'horizontal'

  def add(self):
    popped_division = self.pop_largest_division()
    if popped_division is None:
      return
    i,j = popped_division
    (x0,x1,y0,y1) = self.divisions[(i,j)][1]
    del self.divisions[(i,j)]
    direction = self.get_cut_direction(x0,x1,y0,y1)
    if direction=='vertical':
      cut_x = (x0+x1)/2
      bisect.insort(self.vertical_cuts_x,cut_x)
      new_x = self.vertical_cuts_x.index(cut_x)
      for temp_x in range(new_x-1,len(self.vertical_cuts_x)-1):
        for temp_y in range(len(self.horizontal_cuts_y)-1):
          if (temp_x,temp_y) in self.divisions:
              del self.divisions[(temp_x,temp_y)]
          self.add_new_division(temp_x,temp_y)
      return cut_x,False
    else:
      cut_y = (y0+y1)/2
      bisect.insort(self.horizontal_cuts_y,cut_y)
      new_y = self.horizontal_cuts_y.index(cut_y)
      for temp_y in range(new_y-1,len(self.horizontal_cuts_y)-1):
        for temp_x in range(len(self.vertical_cuts_x)-1):
          if (temp_x,temp_y) in self.divisions:
              del self.divisions[(temp_x,temp_y)]
          self.add_new_division(temp_x,temp_y)
      return cut_y, True
  def get_all_areas(self):
    areas = []
    for area_and_coordinates in self.divisions.values():
      area, (x0, x1, y0, y1) = area_and_coordinates
      areas.append(area)
    return areas

  def get_probability(self):
    result = 0
    areas = self.get_all_areas()
    for area in areas:
      result = result + (area**2)
    return 1-result

class UnitSquareNew:
    """
    Heuristic point generator for the grid-based metric dimension algorithm.

    The two fitted curves (defined in the canonical frame centered at (cx, cy))
    are:
        curve1: y = -0.028964*(x-cx)^2 + 0.985804*(x-cx) + 0.630070 + cy
        curve2: y =  0.021721*(x-cx)^2 + 0.981117*(x-cx) - 0.626609 + cy

    point_generator yields ideal probe points in the order dictated by the
    pattern in pattern.pdf:
      1. Center of curve1 (x=cx), then center of curve2 (x=cx).
      2. Expand symmetrically left/right in steps of d, yielding
         (x+d, curve1), (x+d, curve2), (x-d, curve1), (x-d, curve2), ...
      A point is only yielded if it falls inside the grid cell's bounding
      square [cx-r, cx+r] x [cy-r, cy+r].  The generator stops once a full
      expansion step produces no in-bounds points on either curve in either
      direction.

    Yields: (x, y) tuples (curve_id dropped; callers only need coordinates).
    """

    @staticmethod
    def _curve1_y(x, cx, cy):
        dx = x - cx
        return -0.028964 * dx**2 + 0.985804 * dx + 0.630070 + cy

    @staticmethod
    def _curve2_y(x, cx, cy):
        dx = x - cx
        return  0.021721 * dx**2 + 0.981117 * dx - 0.626609 + cy

    @staticmethod
    def _in_square(x, y, cx, cy, r):
        """True iff (x, y) is inside the axis-aligned cell square of half-side r."""
        return (cx - r) <= x <= (cx + r) and (cy - r) <= y <= (cy + r)

    def point_generator(self, cx, cy, r, d):
        """
        Generator of ideal probe points for the cell centred at (cx, cy).

        Parameters
        ----------
        cx, cy : float  -- cell centre in RGG [0,1]^2 space
        r      : float  -- RGG radius (half-side of the grid cell)
        d      : float  -- step size along x between successive probe points
        """
        # --- Step 0: centre points (x = cx) ---
        y1_center = self._curve1_y(cx, cx, cy)
        if self._in_square(cx, y1_center, cx, cy, r):
            yield (cx, y1_center)

        y2_center = self._curve2_y(cx, cx, cy)
        if self._in_square(cx, y2_center, cx, cy, r):
            yield (cx, y2_center)

        # --- Steps 1, 2, 3, ...: expand symmetrically ---
        step = 1
        while True:
            any_yielded = False

            for sign in [1, -1]:
                x = cx + sign * step * d

                y1 = self._curve1_y(x, cx, cy)
                if self._in_square(x, y1, cx, cy, r):
                    yield (x, y1)
                    any_yielded = True

                y2 = self._curve2_y(x, cx, cy)
                if self._in_square(x, y2, cx, cy, r):
                    yield (x, y2)
                    any_yielded = True

            if not any_yielded:
                return

            step += 1

class UnitCircle:
    def __init__(self,center_x,center_y,r):
        self.us = UnitSquare()
        self.centers = []
        self.center_x=center_x
        self.center_y = center_y
        self.r = r
    def add(self):
        coordinate, is_horizontal = self.us.add()
        return self.modifyCenters(coordinate, is_horizontal)

    def modifyCenters(self, coordinate, is_horizontal):
        if not is_horizontal:
            new_x = 0
            if(coordinate>0.5):
              new_x = self.center_x + ((1-coordinate)*2*self.r)
            else:
              new_x = self.center_x + (coordinate*2*self.r)
            self.centers.append((new_x , self.center_y))
            return (new_x, self.center_y)
        else:
            new_y = 0
            if(coordinate>0.5):
                new_y = self.center_y + ((1-coordinate)*2*self.r)
            else:
                new_y = self.center_y + (coordinate*2*self.r)
            self.centers.append((self.center_x, new_y))
            return (self.center_x, new_y)
    def getProbability(self):
        base_circle = Point(self.center_x,self.center_y).buffer(1)
        cut_circles = [Point(x,y).buffer(1) for (x,y) in self.centers]
        regions = [base_circle]
        for cut_circle in cut_circles:
          new_regions = []
          for region in regions:
            inter = region.intersection(cut_circle)
            if not inter.is_empty:
              new_regions.append(inter)
            diff = region.difference(cut_circle)
            if not diff.is_empty:
              new_regions.append(diff)
          regions = new_regions
        total_area = base_circle.area
        area_fractions = [region.area/total_area for region in regions]
        p_same_region = sum(area**2 for area in area_fractions)
        return 1-p_same_region
    def getCenters(self):
      return self.centers