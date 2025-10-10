
import numpy as np

from tools import lines, chemistry


class McCabeThieleLogic:

    DEFAULTS = {
        'xf': 0.68,
        'xd': 0.93,
        'xb': 0.04,
        'alpha': 1.85,
        'R': 3.0,
        'B': 10.0,
        'q': 0.99,
    }
    DEFAULT_MAX_EQ_ARRAY_SIZE = 127
    DEPENDENT_VARS = ['R', 'B', 'q', 'xf', 'xd', 'xb']
    DEFAULT_DEPENDENT_VAR = 'q'

    def __init__(self, xf=None, xd=None, xb=None, alpha=None, r=None, b=None, q=None, *, max_eq_array_size=None):
        self.variables = {}
        init_args = locals()

        for var_name, default_value in self.DEFAULTS.items():
            value = init_args.get(var_name)
            self.variables[var_name] = value if value is not None else default_value

        self._dependent_variable = self.DEFAULT_DEPENDENT_VAR

        self.max_eq_array_size = max_eq_array_size if max_eq_array_size is not None else self.DEFAULT_MAX_EQ_ARRAY_SIZE
        self.n_eq_points = 0
        self.eq_points = np.zeros(( 2 *self.max_eq_array_size, 1), dtype=float)

        self.rectifying_coef = 0.0, 0.0
        self.stripping_coef = 0.0, 0.0
        self.q_line_coef = 0.0, 0.0
        self.q_point = 0.0, 0.0

        self.xs = np.arange(0, 1, 0.01, dtype=float)
        self.vle_curve = np.zeros_like(self.xs)

        self._variable_calculators_dict = {
            'xf': self._calculate_xf,
            'xd': self._calculate_xd,
            'xb': self._calculate_xb,
            'R': self._calculate_r,
            'B': self._calculate_b,
            'q': self._calculate_q,
        }

    @property
    def dependent_variable(self):
        return self._dependent_variable

    @dependent_variable.setter
    def dependent_variable(self, new_value):
        if new_value not in self.DEPENDENT_VARS:
            raise ValueError(f"Invalid dependent variable '{new_value}'. ")
        self._dependent_variable = new_value


    def calc_rectifying_line_coef(self):
        r = self.variables['R']
        a = r / (r + 1)
        if 'xd' == self._dependent_variable:
            b = lines.intersect_from_slope_and_point(a, *self.q_point)
        else:
            xd = self.variables['xd']
            b = xd / (r + 1)
        self.rectifying_coef = a, b

    def calc_stripping_line_coef(self):
        b = self.variables['B']
        slope = (b + 1) / b
        if 'xb' == self._dependent_variable:
            intercept = lines.intersect_from_slope_and_point(slope, *self.q_point)
        else:
            xb = self.variables['xb']
            intercept = -xb / b
        self.stripping_coef = slope, intercept

    def calc_q_line_coef(self):
        q = self.variables['q']
        if 1 == q:
            slope = float('inf')
        else:
            slope = q / (q - 1)

        if 'xf' == self.dependent_variable:
            intercept = lines.intersect_from_slope_and_point(slope, *self.q_point)
        else:
            xf = self.variables['xf']
            if 1 == q:
                intercept = xf
            else:
                intercept = -xf / (q - 1)
        self.q_line_coef = slope, intercept

    def calc_known_operating_lines(self):
        match self._dependent_variable:
            case 'q' | 'xf':
                self.calc_rectifying_line_coef()
                self.calc_stripping_line_coef()
            case 'R' | 'xd':
                self.calc_stripping_line_coef()
                self.calc_q_line_coef()
            case 'B' | 'xb':
                self.calc_rectifying_line_coef()
                self.calc_q_line_coef()

    def calculate_q_point(self):
        xf = self.variables['xf']
        q = self.variables['q']
        match self._dependent_variable:
            case 'q' | 'xf':
                ans = lines.intersect(*self.rectifying_coef, *self.stripping_coef)
            case 'R' | 'xd':
                if q == 1:
                    ans = xf, lines.get_y(xf, *self.stripping_coef)
                else:
                    ans = lines.intersect(*self.stripping_coef, *self.q_line_coef)
            case 'B' | 'xb':
                if q == 1:
                    ans = xf, lines.get_y(xf, *self.rectifying_coef)
                else:
                    ans = lines.intersect(*self.rectifying_coef, *self.q_line_coef)
            case _:
                raise ValueError("Impossible to get here")
        self.q_point = ans

    def _calculate_q(self):
        xf = self.variables['xf']
        a, _ = lines.through_points(*self.q_point, xf, xf)
        if a is None or float('inf') == a:
            ans = 1
        elif a == 1:
            ans = float('inf')
        elif 0 == a:
            ans = 0
        else:
            ans = a/ (a - 1)
        self.variables['q'] = ans

    def _calculate_r(self):
        xd = self.variables['xd']
        a, _ = lines.through_points(*self.q_point, xd, xd)
        # I don't think this will ever happen, but doesn't hurt to keep it in.
        if a == 1:
            self.variables['R'] = float('inf')
        else:
            self.variables['R'] = a / (1 - a)

    def _calculate_b(self):
        xb = self.variables['xb']
        a, _ = lines.through_points(*self.q_point, xb, xb)
        # Same as earlier.
        if a == 1:
            self.variables['B'] = float('inf')
        else:
            self.variables['B'] = 1 / (a - 1)

    def _calculate_x(self, var, coef):
        a, b = coef
        if 1 == a:
            raise ValueError("This should be physically impossible.")
        self.variables[var] = b / (1 - a)

    def _calculate_xb(self):
        self._calculate_x('xb', self.stripping_coef)

    def _calculate_xf(self):
        self._calculate_x('xf', self.q_line_coef)

    def _calculate_xd(self):
        self._calculate_x('xd', self.rectifying_coef)

    def calculate_dependent_var(self):
        self._variable_calculators_dict[self._dependent_variable]()

    def calc_found_operating_line(self):
        match self._dependent_variable:
            case 'q' | 'xf':
                self.calc_q_line_coef()
            case 'R' | 'xd':
                self.calc_rectifying_line_coef()
            case 'B' | 'xb':
                self.calc_stripping_line_coef()

    def make_equilibrium_points(self):
        """
        TODO: The constant reshaping of this array isn't necessary anymore,
        But it will be a lot of work to refactor, for very little benefit.
        """
        n_eq_points = 0
        eqs = self.eq_points
        eqs.shape = (2 * self.max_eq_array_size, 1)
        eqs.fill(0.0)
        xb = self.variables['xb']
        xd = self.variables['xd']
        alpha = self.variables['alpha']
        n = 3
        eqs[:n] = xb

        while eqs[n - 1] < xd and n < 2 * self.max_eq_array_size - 5:
            new = chemistry.vapor_liquid_equilibrium(eqs[n - 1], alpha)

            strip = (new - self.stripping_coef[1]) / self.stripping_coef[0]
            rect = (new - self.rectifying_coef[1]) / self.rectifying_coef[0]

            eqs[n] = new
            eqs[n + 1] = max(strip, rect)
            eqs[n + 2] = eqs[n]
            eqs[n + 3] = eqs[n + 1]
            n += 4
            n_eq_points += 1

        self.eq_points.shape = (self.max_eq_array_size, 2)
        self.n_eq_points = n_eq_points

    def make_all_lines(self):
        self.calc_known_operating_lines()
        self.calculate_q_point()
        # The order of the next 2 steps depend on what is calculated
        if self.dependent_variable in ('R', 'B', 'q'):
            self.calculate_dependent_var()
            self.calc_found_operating_line()
        else:
            self.calc_found_operating_line()
            self.calculate_dependent_var()
        self.vle_curve = chemistry.vapor_liquid_equilibrium(self.xs, self.variables['alpha'])
        self.make_equilibrium_points()


def main():
    return


if __name__ == "__main__":
    main()
