"""Offline unit test suite for :mod:`aoc_common.aoc_commons`.

Purpose & Value:
    Provides deterministic regression coverage for the shared AoC helper library—spanning
    path resolution, AoC input downloading, Rich logging setup, 2D/3D geometry, grid
    manipulation, sparse point rendering, and algorithmic utilities—without touching live
    network services or personal secrets.

Mechanics & Isolation:
    Uses ``unittest.TestCase``, temporary directories, and ``unittest.mock`` patches over
    ``urllib.request.urlopen`` and environment variables so every HTTP, ``.env``, and
    filesystem scenario executes cleanly offline with no ``AOC_SESSION_COOKIE`` required.
"""

import copy
import heapq
import importlib
import logging
import os
import unittest
from os import path
from shutil import rmtree
from unittest.mock import MagicMock, patch

from rich.logging import RichHandler

import aoc_common
import aoc_common.aoc_commons as ac

# Set logging level of aoc_commons
logger = logging.getLogger("aoc_common.aoc_commons")
logger.setLevel(logging.INFO)


class TestTypes(unittest.TestCase):
    """Unit tests for reusable helpers and geometric types in ``aoc_commons``."""

    def setUp(self):
        """Read locations, clear the input folder, and set up some test data."""
        self.locations = ac.get_locations(__file__)
        self.clear_input_folder()

        self.points = set()
        self.a_point = ac.Point(5, 5)
        self.b_point = ac.Point(1, 2)
        self.c_point = ac.Point(6, 7)
        self.d_point = ac.Point(4, 3)
        self.e_point = ac.Point(3, 6)
        self.y_invert_point = ac.Point(0, -1)

        self.points.add(self.a_point)
        self.points.add(self.b_point)
        self.points.add(self.c_point)
        self.points.add(self.d_point)
        self.points.add(self.e_point)

        self.a_point_neighbours = self.a_point.neighbours()

    def tearDown(self) -> None:
        self.clear_input_folder()
        return super().tearDown()

    def clear_input_folder(self):
        if self.locations.input_dir.exists():
            print(f"Deleting {self.locations.input_dir}")
            rmtree(self.locations.input_dir)

    def test_write_puzzle_input_file(self):
        """Verify offline AoC input retrieval, User-Agent header, and file caching."""
        # Missing session cookie raises ValueError without making HTTP calls
        with (
            patch("aoc_common.aoc_commons.os.getenv", return_value=None),
            patch("aoc_common.aoc_commons.requests.get") as mock_get,
            self.assertRaises(ValueError),
        ):
            ac.write_puzzle_input_file(2026, 1, self.locations)
        mock_get.assert_not_called()

        # Non-200 HTTP response raises ValueError and sends required AoC User-Agent header
        not_found_response = MagicMock(
            status_code=404,
            reason="Not Found",
            content=b"Puzzle inputs differ by user.",
        )
        with (
            patch("aoc_common.aoc_commons.os.getenv", return_value="test_cookie_123456"),
            patch("aoc_common.aoc_commons.requests.get", return_value=not_found_response) as mock_get,
            self.assertRaises(ValueError),
        ):
            ac.write_puzzle_input_file(2010, 1, self.locations)
        self.assertEqual(mock_get.call_args.kwargs["headers"]["User-Agent"], ac.AOC_USER_AGENT)

        # HTTP 200 writes retrieved data to input_file and returns it
        ok_response = MagicMock(status_code=200, text="(((())))\n")
        with (
            patch("aoc_common.aoc_commons.os.getenv", return_value="test_cookie_123456"),
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response) as mock_get,
        ):
            retrieved = ac.write_puzzle_input_file(2015, 1, self.locations)
        self.assertEqual(retrieved, "(((())))\n")
        self.assertEqual(self.locations.input_file.read_text(encoding="utf-8"), "(((())))\n")
        self.assertEqual(mock_get.call_args.kwargs["headers"]["User-Agent"], ac.AOC_USER_AGENT)

        # Non-empty existing input.txt skips HTTP download and returns filename
        with patch("aoc_common.aoc_commons.requests.get") as mock_get:
            cached = ac.write_puzzle_input_file(2015, 1, self.locations)
        mock_get.assert_not_called()
        self.assertEqual(cached, path.basename(self.locations.input_file))

        # A 0-byte placeholder input.txt does not block downloading real puzzle input
        self.locations.input_file.write_text("", encoding="utf-8")
        with (
            patch("aoc_common.aoc_commons.os.getenv", return_value="test_cookie_123456"),
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response) as mock_get,
        ):
            refreshed = ac.write_puzzle_input_file(2015, 1, self.locations)
        mock_get.assert_called_once()
        self.assertEqual(refreshed, "(((())))\n")

    def test_is_git_crypt_locked_and_write_puzzle_input_overwrites_locked_blob(self):
        """Verify 10-byte git-crypt header detection and locked-blob overwrite behaviour."""
        self.locations.input_dir.mkdir(parents=True, exist_ok=True)
        locked_file = self.locations.input_file
        plain_file = self.locations.input_dir / "plain.txt"
        empty_file = self.locations.input_dir / "empty.txt"
        missing_file = self.locations.input_dir / "missing.txt"

        locked_file.write_bytes(b"\x00GITCRYPT\x00\xde\xad\xbe\xef")
        plain_file.write_text("123\n", encoding="utf-8")
        empty_file.write_text("", encoding="utf-8")

        self.assertTrue(ac.is_git_crypt_locked(locked_file))
        self.assertFalse(ac.is_git_crypt_locked(plain_file))
        self.assertFalse(ac.is_git_crypt_locked(empty_file))
        self.assertFalse(ac.is_git_crypt_locked(missing_file))

        # Locked file with no session cookie raises an actionable git-crypt error without touching HTTP
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("aoc_common.aoc_commons.load_dotenv", return_value=False),
            patch("aoc_common.aoc_commons.requests.get") as mock_get,
            self.assertRaises(ValueError) as exc_ctx,
        ):
            ac.write_puzzle_input_file(2026, 2, self.locations)
        mock_get.assert_not_called()
        self.assertIn("git-crypt", str(exc_ctx.exception))
        self.assertIn("AOC_SESSION_COOKIE", str(exc_ctx.exception))

        # Locked file with valid AOC_SESSION_COOKIE downloads and overwrites the locked blob
        ok_response = MagicMock(status_code=200, text="fresh-input\n")
        with (
            patch.dict(os.environ, {"AOC_SESSION_COOKIE": "test_cookie_123456"}, clear=True),
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response) as mock_get,
        ):
            refreshed = ac.write_puzzle_input_file(2026, 2, self.locations)
        mock_get.assert_called_once()
        self.assertEqual(refreshed, "fresh-input\n")
        self.assertEqual(locked_file.read_text(encoding="utf-8"), "fresh-input\n")
        self.assertFalse(ac.is_git_crypt_locked(locked_file))

    def test_package_reexports_and_lazy_dotenv(self):
        """Verify package-level re-exports and lazy .env loading without import-time side effects."""
        expected_symbols = (
            "AOC_USER_AGENT",
            "Grid",
            "Locations",
            "Point",
            "Point3D",
            "VectorDicts",
            "Vectors",
            "binary_search",
            "bounding_box",
            "cls",
            "get_factors",
            "get_locations",
            "is_git_crypt_locked",
            "lower_bound",
            "merge_intervals",
            "render_points",
            "setup_file_logging",
            "setup_logging",
            "timer",
            "to_base_n",
            "top_and_tail",
            "upper_bound",
            "validate",
            "write_puzzle_input_file",
        )
        for symbol in expected_symbols:
            self.assertTrue(hasattr(aoc_common, symbol), f"aoc_common should re-export {symbol}")
            self.assertIs(getattr(aoc_common, symbol), getattr(ac, symbol))

        # Importing or reloading aoc_commons must not invoke load_dotenv eagerly
        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            importlib.reload(ac)
        mock_load_dotenv.assert_not_called()
        importlib.reload(ac)
        importlib.reload(aoc_common)

        # When AOC_SESSION_COOKIE is already present, load_dotenv is not called
        ok_response = MagicMock(status_code=200, text="input\n")
        with (
            patch.dict(os.environ, {"AOC_SESSION_COOKIE": "already_set_cookie"}, clear=True),
            patch("aoc_common.aoc_commons.load_dotenv") as mock_load_dotenv,
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response),
        ):
            result = ac.write_puzzle_input_file(2026, 2, self.locations)
        mock_load_dotenv.assert_not_called()
        self.assertEqual(result, "input\n")

        # Remove cached file so the next call attempts retrieval again
        self.locations.input_file.unlink()

        def populate_cookie(*_args: object, **_kwargs: object) -> bool:
            os.environ["AOC_SESSION_COOKIE"] = "lazy_cookie_123456"
            return True

        # When AOC_SESSION_COOKIE is missing, load_dotenv is invoked lazily
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("aoc_common.aoc_commons.load_dotenv", side_effect=populate_cookie) as mock_load_dotenv,
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response),
        ):
            lazy_result = ac.write_puzzle_input_file(2026, 2, self.locations)
        mock_load_dotenv.assert_called_once()
        self.assertEqual(lazy_result, "input\n")

    def test_vectors(self):
        """Test our Vector Enums"""
        self.assertEqual(ac.Vectors.N.value, (0, 1))
        self.assertEqual(ac.Vectors.NW.value, (-1, 1))
        self.assertEqual(ac.Vectors.S.value, (0, -1))
        self.assertEqual(ac.Vectors.E.value, (1, 0))
        self.assertEqual(ac.Vectors.N.y_inverted, (0, -1))
        self.assertEqual(ac.Vectors.SW.value, (-1, -1))
        self.assertEqual(ac.Vectors.N.to_point(), ac.Point(0, 1))
        self.assertEqual(ac.Vectors.N.to_point(y_down=True), ac.Point(0, -1))

    def test_vector_dicts(self):
        """Test our vector dicts using arrow keys"""
        self.assertEqual(ac.VectorDicts.ARROWS[">"], (1, 0))
        self.assertEqual(ac.VectorDicts.ARROWS["v"], (0, -1))
        self.assertEqual(ac.VectorDicts.DIRS["L"], (-1, 0))
        self.assertEqual(ac.VectorDicts.DIRS["U"], (0, 1))
        self.assertEqual(ac.VectorDicts.NINE_BOX["tr"], (1, 1))
        self.assertEqual(ac.VectorDicts.NINE_BOX["bl"], (-1, -1))
        self.assertEqual(ac.VectorDicts.ARROWS_Y_DOWN, {"^": (0, -1), ">": (1, 0), "v": (0, 1), "<": (-1, 0)})
        self.assertEqual(ac.VectorDicts.DIRS_Y_DOWN, {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)})

    def test_point_arithmetic(self):
        """Test we can add, subtract and multiply points"""
        self.assertEqual(self.a_point + self.b_point, self.c_point, "Asserting Point addition")
        self.assertEqual(self.a_point - self.b_point, self.d_point, "Asserting Point subtraction")
        self.assertEqual(self.b_point * ac.Point(3, 3), self.e_point, "Asserting multiplication")
        self.assertEqual(self.b_point * 3, ac.Point(3, 6))
        self.assertEqual(3 * self.b_point, ac.Point(3, 6))
        self.assertEqual(self.b_point * -2, ac.Point(-2, -4))
        with self.assertRaises(TypeError):
            _ = self.b_point * True

    def test_point_ordering_and_specific_neighbours(self):
        """Verify Point ordering for sorting/heaps and Iterable support in get_specific_neighbours."""
        self.assertLess(ac.Point(1, 5), ac.Point(2, 0))
        self.assertLess(ac.Point(1, 2), ac.Point(1, 5))
        self.assertEqual(
            sorted([ac.Point(2, 0), ac.Point(1, 5), ac.Point(1, 2)]),
            [ac.Point(1, 2), ac.Point(1, 5), ac.Point(2, 0)],
        )

        heap: list[tuple[int, ac.Point]] = []
        heapq.heappush(heap, (1, ac.Point(2, 0)))
        heapq.heappush(heap, (1, ac.Point(1, 2)))
        self.assertEqual(heapq.heappop(heap), (1, ac.Point(1, 2)))

        origin = ac.Point(0, 0)
        from_tuple = origin.get_specific_neighbours((ac.Vectors.N, ac.Vectors.E))
        from_gen = origin.get_specific_neighbours(v for v in (ac.Vectors.N, ac.Vectors.E))
        self.assertEqual(from_tuple, [ac.Point(0, 1), ac.Point(1, 0)])
        self.assertEqual(from_gen, [ac.Point(0, 1), ac.Point(1, 0)])

    def test_point3d(self):
        """Verify Point3D arithmetic, ordering, distances, and 6/26-neighbour generation."""
        p1 = ac.Point3D(1, 2, 3)
        p2 = ac.Point3D(4, -1, 2)

        self.assertEqual(p1 + p2, ac.Point3D(5, 1, 5))
        self.assertEqual(p1 - p2, ac.Point3D(-3, 3, 1))
        self.assertEqual(p1 * ac.Point3D(2, 3, 4), ac.Point3D(2, 6, 12))
        self.assertEqual(p1 * 3, ac.Point3D(3, 6, 9))
        self.assertEqual(3 * p1, ac.Point3D(3, 6, 9))
        with self.assertRaises(TypeError):
            _ = p1 * True

        self.assertLess(ac.Point3D(0, 9, 9), p1)
        self.assertLess(p1, ac.Point3D(1, 2, 4))
        self.assertEqual(repr(p1), "P3D(1,2,3)")

        self.assertEqual(ac.Point3D.manhattan_distance(ac.Point3D(-1, 2, -3)), 6)
        self.assertEqual(p1.manhattan_distance_from(p2), 7)

        orthog = p1.neighbours(include_diagonals=False)
        self.assertEqual(len(orthog), 6)
        self.assertNotIn(p1, orthog)

        all_26 = p1.neighbours(include_diagonals=True)
        self.assertEqual(len(all_26), 26)
        self.assertNotIn(p1, all_26)

        self.assertEqual(len(p1.neighbours(include_diagonals=False, include_self=True)), 7)
        self.assertIn(p1, p1.neighbours(include_diagonals=False, include_self=True))
        self.assertEqual(len(p1.neighbours(include_diagonals=True, include_self=True)), 27)
        self.assertEqual(list(p1.yield_neighbours(include_diagonals=False)), orthog)

    def test_bounding_box_and_render_points(self):
        """Verify bounding_box calculation and sparse point-cloud rendering."""
        pts = [ac.Point(2, -1), ac.Point(-3, 4), ac.Point(0, 0)]
        self.assertEqual(ac.bounding_box(pts), (ac.Point(-3, -1), ac.Point(2, 4)))
        with self.assertRaises(ValueError):
            ac.bounding_box([])

        sparse_set = {ac.Point(0, 0), ac.Point(2, 1)}
        self.assertEqual(ac.render_points(sparse_set, y_down=True), "#..\n..#")
        self.assertEqual(ac.render_points(sparse_set, y_down=False), "..#\n#..")

        sparse_map = {ac.Point(0, 0): "S", ac.Point(1, 1): "E"}
        self.assertEqual(ac.render_points(sparse_map, y_down=True), "S.\n.E")
        self.assertEqual(ac.render_points(sparse_map, y_down=False), ".E\nS.")

        self.assertEqual(ac.render_points(set()), "")
        self.assertEqual(ac.render_points({}), "")

    def test_manhattan_distance(self):
        """Test Manhattan distance between points, i.e. the sum of the two vectors"""
        self.assertEqual(ac.Point.manhattan_distance(self.e_point), 3 + 6)
        self.assertEqual(self.c_point.manhattan_distance_from(self.b_point), abs(self.a_point.x) + abs(self.a_point.y))

    def test_point_containers(self):
        """Test a points neighbours and orthogonal neighbours"""

        all_neighbours_count = 8  # point has 8 neighbours
        orthog_neighbours_count = 4  # point has 4 orthogonal neighbours

        self.assertEqual(len(self.a_point_neighbours), all_neighbours_count, f"Expect {all_neighbours_count} from all neighbours")

        a_point_orthog_neighbours = self.a_point.neighbours(include_diagonals=False)
        self.assertEqual(
            len(a_point_orthog_neighbours), orthog_neighbours_count, f"Expect {orthog_neighbours_count} orthogonal neighbours"
        )
        self.assertNotIn(self.a_point, self.a_point.neighbours(), "Check neighbours does not include self")
        self.assertIn(self.a_point, self.a_point.neighbours(include_self=True), "Check neighbours includes self")
        self.assertEqual(
            len(self.a_point.neighbours(include_self=True)),
            all_neighbours_count + 1,
            f"All neighbours with self should be {all_neighbours_count + 1}",
        )

    def test_point_neighbour_generator(self):
        """Test we can use a generator to return neighbours"""
        gen = self.a_point.yield_neighbours()

        for _ in range(len(self.a_point_neighbours)):
            self.assertIn(next(gen), self.a_point_neighbours, "Generated item is a valid neighbour")

        with self.assertRaises(StopIteration):  # no more items to generate
            next(gen)

    def test_grid(self):
        """Test our Grid class.
        Test height and width, valid locations within the grid, values at a location.
        Test we can retrieve a row and a column, as str.
        """
        input_grid = ["5483143223", "2745854711", "5264556173", "6141336146", "6357385478", "4167524645", "2176841721"]

        input_array_data = [[int(posn) for posn in row] for row in input_grid]
        grid = ac.Grid(input_array_data)
        self.assertEqual(grid.height, len(input_grid))
        self.assertEqual(grid.width, len(input_grid[0]))
        self.assertTrue(grid.valid_location(ac.Point(1, 1)))
        self.assertFalse(grid.valid_location(ac.Point(11, 8)))
        self.assertEqual(grid.value_at_point(ac.Point(1, 1)), 7)
        self.assertEqual(grid.rows_as_str()[0], "5483143223")
        self.assertEqual(grid.cols_as_str()[0], "5256642")

        transposed = grid.transpose()
        self.assertEqual(transposed.rows_as_str()[0], "5256642")

        flipped = grid.flip_vertical()
        self.assertEqual(flipped.rows_as_str()[0], "3223413845")

        flipped = grid.flip_horizontal()
        self.assertEqual(flipped.rows_as_str()[0], "2176841721")

        rotated = grid.rotate_90()
        self.assertEqual(rotated.rows_as_str()[0], "2466525")

        rotated = grid.rotate_90(ccw=True)
        self.assertEqual(rotated.rows_as_str()[0], "3136851")

        # Transposed and rotated grids retain mutable list rows
        transposed.set_value_at_point(ac.Point(0, 0), 9)
        self.assertEqual(transposed.value_at_point(ac.Point(0, 0)), 9)
        rotated.set_value_at_point(ac.Point(0, 0), 8)
        self.assertEqual(rotated.value_at_point(ac.Point(0, 0)), 8)

    def test_grid_ergonomics_and_edge_cases(self):
        """Verify Grid non-mutation, str rows, cols, find_points_with_value, neighbours_of, and edge cases."""
        source = [[1, 2], [2, 3]]
        grid = ac.Grid(source)
        grid.set_value_at_point(ac.Point(0, 0), 99)
        self.assertEqual(source, [[1, 2], [2, 3]])
        self.assertEqual(grid.value_at_point(ac.Point(0, 0)), 99)

        str_grid = ac.Grid(["12", "34"])
        str_grid.set_value_at_point(ac.Point(1, 0), "9")
        self.assertEqual(str_grid.rows_as_str(), ["19", "34"])

        lookup_grid = ac.Grid([[1, 2], [2, 3]])
        self.assertEqual(lookup_grid.cols, [[1, 2], [2, 3]])
        self.assertEqual(set(lookup_grid.find_points_with_value(2)), {ac.Point(1, 0), ac.Point(0, 1)})
        lookup_grid.set_value_at_point(ac.Point(0, 0), 2)
        self.assertEqual(
            set(lookup_grid.find_points_with_value(2)),
            {ac.Point(0, 0), ac.Point(1, 0), ac.Point(0, 1)},
        )

        self.assertEqual(
            set(lookup_grid.neighbours_of(ac.Point(0, 0), include_diagonals=False)),
            {ac.Point(1, 0), ac.Point(0, 1)},
        )
        self.assertEqual(
            set(lookup_grid.neighbours_of(ac.Point(0, 0), include_diagonals=True)),
            {ac.Point(1, 0), ac.Point(0, 1), ac.Point(1, 1)},
        )
        self.assertEqual(
            set(lookup_grid.neighbours_of(ac.Point(0, 0), include_diagonals=False, include_self=True)),
            {ac.Point(0, 0), ac.Point(1, 0), ac.Point(0, 1)},
        )

        empty_grid = ac.Grid([])
        self.assertEqual(empty_grid.width, 0)
        self.assertEqual(empty_grid.height, 0)
        self.assertEqual(empty_grid.all_points(), [])
        self.assertEqual(empty_grid.cols, [])
        self.assertEqual(empty_grid.rows_as_str(), [])
        self.assertEqual(empty_grid.cols_as_str(), [])
        self.assertEqual(empty_grid.transpose().width, 0)

        with self.assertRaises(ValueError):
            ac.Grid([[1, 2], [3]])

    def test_binary_search(self):
        """Test a binary search,
        i.e. where we start with a midpoint, evaluate the result of a function,
        and see if it gives us the result we want."""
        self.assertEqual(ac.binary_search(225, 0, 20, lambda x: x**2, reverse_search=True), None)
        self.assertEqual(ac.binary_search(225, 0, 20, lambda x: x**2), 15)

        calls = 0

        def guarded_square(x: int) -> int:
            nonlocal calls
            calls += 1
            if calls > 100:
                raise AssertionError("binary_search exceeded iteration bound (infinite loop)")
            return x**2

        self.assertIsNone(ac.binary_search(226, 0, 20, guarded_square))
        self.assertLessEqual(calls, 20)
        self.assertEqual(ac.binary_search(0, 0, 20, lambda x: x**2), 0)
        self.assertEqual(ac.binary_search(400, 0, 20, lambda x: x**2), 20)
        self.assertEqual(ac.binary_search(70, 0, 50, lambda x: 100 - 2 * x, reverse_search=True), 15)

        rev_calls = 0

        def guarded_desc(x: int) -> int:
            nonlocal rev_calls
            rev_calls += 1
            if rev_calls > 100:
                raise AssertionError("binary_search exceeded iteration bound (infinite loop)")
            return 100 - 2 * x

        self.assertIsNone(ac.binary_search(71, 0, 50, guarded_desc, reverse_search=True))
        self.assertLessEqual(rev_calls, 20)
        self.assertIsNone(ac.binary_search(0, 5, 2, lambda x: x))

    def test_lower_and_upper_bound(self):
        """Verify monotonic predicate bisection helpers."""
        self.assertEqual(ac.lower_bound(0, 20, lambda x: x**2 >= 200), 15)
        self.assertIsNone(ac.lower_bound(0, 10, lambda x: x > 100))
        self.assertEqual(ac.lower_bound(0, 10, lambda x: x >= 0), 0)
        self.assertIsNone(ac.lower_bound(5, 2, lambda x: x >= 0))

        self.assertEqual(ac.upper_bound(0, 20, lambda x: x**2 <= 200), 14)
        self.assertIsNone(ac.upper_bound(0, 10, lambda x: x < 0))
        self.assertEqual(ac.upper_bound(0, 10, lambda x: x <= 100), 10)
        self.assertIsNone(ac.upper_bound(5, 2, lambda x: x <= 10))

    def test_merge_intervals(self):
        """Test our ability to take a set of intervals and merge them."""
        pairs = [
            [1, 5],  # Non-overlapping pair
            [3, 7],  # Overlapping pair
            [8, 12],  # Non-overlapping pair
            [10, 15],  # Overlapping pair
            [18, 20],  # Non-overlapping pair
        ]

        expected = [[1, 7], [8, 15], [18, 20]]

        self.assertEqual(ac.merge_intervals(pairs), expected)
        self.assertEqual(ac.merge_intervals([]), [])

        unsorted_original = [[8, 12], [1, 5], [3, 7]]
        snapshot = copy.deepcopy(unsorted_original)
        self.assertEqual(ac.merge_intervals(unsorted_original), [[1, 7], [8, 12]])
        self.assertEqual(unsorted_original, snapshot)

        mixed_intervals = [(1, 5), range(3, 8), range(10, 10), (10, 12)]
        self.assertEqual(ac.merge_intervals(mixed_intervals), [[1, 7], [10, 12]])

        adjacent = [[1, 5], [6, 8], [10, 12]]
        self.assertEqual(ac.merge_intervals(adjacent), [[1, 5], [6, 8], [10, 12]])
        self.assertEqual(ac.merge_intervals(adjacent, merge_adjacent=True), [[1, 8], [10, 12]])

        with self.assertRaises(ValueError):
            ac.merge_intervals([[5, 2]])
        with self.assertRaises(ValueError):
            ac.merge_intervals([range(0, 10, 2)])
        with self.assertRaises(ValueError):
            ac.merge_intervals([[1, 2, 3]])

    def test_get_factors(self):
        """Test that we can retrieve all factors of a number"""
        expected = {1, 2, 4, 8}  # factors of 8
        self.assertEqual(ac.get_factors(8), expected)
        self.assertEqual(ac.get_factors(1), {1})
        with self.assertRaises(ValueError):
            ac.get_factors(0)
        with self.assertRaises(ValueError):
            ac.get_factors(-4)

    def test_to_base_n(self):
        """Test our ability to obtain the str representation of a number converted to any base"""
        self.assertEqual(ac.to_base_n(10, 2), "1010")
        self.assertEqual(ac.to_base_n(38, 5), "123")
        self.assertEqual(ac.to_base_n(24, 12), "20")
        self.assertEqual(ac.to_base_n(0, 12), "0")
        self.assertEqual(ac.to_base_n(57, 10), "57")
        self.assertEqual(ac.to_base_n(255, 16), "ff")
        self.assertEqual(ac.to_base_n(35, 36), "z")
        self.assertEqual(ac.to_base_n(-10, 2), "-1010")
        self.assertEqual(ac.to_base_n(-255, 16), "-ff")

        for invalid_base in (1, 0, -2, 37):
            with self.assertRaises(ValueError):
                ac.to_base_n(10, invalid_base)

        for base in (2, 8, 10, 12, 16, 36):
            for num in (-999, -1, 0, 1, 42, 999):
                self.assertEqual(int(ac.to_base_n(num, base), base), num)

    def test_top_and_tail(self):
        """Verify line summarisation, line numbering options, empty lists, and non-sequences."""
        short_lines = [f"line {i}" for i in range(1, 11)]
        expected_short = "\n".join(f"{i:>2}: line {i}" for i in range(1, 11))
        self.assertEqual(ac.top_and_tail(short_lines), expected_short)

        long_lines = [f"line {i}" for i in range(1, 13)]
        expected_long = "\n".join(
            [
                " 1: line 1",
                " 2: line 2",
                " 3: line 3",
                " 4: line 4",
                " 5: line 5",
                "...",
                " 8: line 8",
                " 9: line 9",
                "10: line 10",
                "11: line 11",
                "12: line 12",
            ]
        )
        self.assertEqual(ac.top_and_tail(long_lines), expected_long)

        eight_lines = [f"item {i}" for i in range(1, 9)]
        expected_custom_block = "\n".join(
            [
                "1: item 1",
                "2: item 2",
                "...",
                "7: item 7",
                "8: item 8",
            ]
        )
        self.assertEqual(ac.top_and_tail(eight_lines, block_size=2), expected_custom_block)

        expected_no_nums = "\n".join(["item 1", "item 2", "...", "item 7", "item 8"])
        self.assertEqual(
            ac.top_and_tail(eight_lines, block_size=2, include_line_numbers=False),
            expected_no_nums,
        )

        expected_zero_indexed = "\n".join(
            [
                "0: item 1",
                "1: item 2",
                "...",
                "6: item 7",
                "7: item 8",
            ]
        )
        self.assertEqual(
            ac.top_and_tail(eight_lines, block_size=2, zero_indexed=True),
            expected_zero_indexed,
        )

        self.assertEqual(ac.top_and_tail([]), "")
        self.assertEqual(ac.top_and_tail("raw text"), "raw text")

    def test_setup_logging_force_reconfigures_root(self):
        """Verify setup_logging replaces existing root handlers and updates level."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        original_level = root_logger.level
        dummy_handler = logging.NullHandler()

        try:
            root_logger.handlers = [dummy_handler]
            root_logger.setLevel(logging.WARNING)

            ac.setup_logging(level=logging.DEBUG)

            self.assertEqual(root_logger.level, logging.DEBUG)
            self.assertTrue(any(isinstance(h, RichHandler) for h in root_logger.handlers))
            self.assertNotIn(dummy_handler, root_logger.handlers)
        finally:
            root_logger.handlers = original_handlers
            root_logger.setLevel(original_level)

    def test_write_puzzle_input_strips_cookie_quotes_and_hints_on_400(self):
        """Strip quotes/whitespace from AOC_SESSION_COOKIE and hint when AoC returns HTTP 400."""
        if self.locations.input_file.exists():
            self.locations.input_file.unlink()

        ok_response = MagicMock(status_code=200, text="input\n")
        with (
            patch.dict(os.environ, {"AOC_SESSION_COOKIE": ' "quoted_cookie_123456"\n'}, clear=True),
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_response) as mock_get,
        ):
            ac.write_puzzle_input_file(2018, 7, self.locations)
        self.assertEqual(mock_get.call_args.kwargs["cookies"], {"session": "quoted_cookie_123456"})

        self.locations.input_file.unlink()
        expired_response = MagicMock(
            status_code=400,
            reason="Bad Request",
            content=b"Puzzle inputs differ by user.  Please log in to get your puzzle input.",
        )
        with (
            patch.dict(os.environ, {"AOC_SESSION_COOKIE": "expired_cookie_123456"}, clear=True),
            patch("aoc_common.aoc_commons.requests.get", return_value=expired_response),
            self.assertRaises(ValueError) as ctx,
        ):
            ac.write_puzzle_input_file(2018, 7, self.locations)
        self.assertIn("Hint: Your AOC_SESSION_COOKIE may have expired", str(ctx.exception))

    def test_parse_puzzle_html_part1_part2_and_samples(self):
        """Parse AoC puzzle HTML articles, Markdown formatting, and ranked sample candidates."""
        html = (
            "<html><body>"
            '<header><div class="user">Darren</div></header>'
            "<main>"
            '<article class="day-desc">'
            "<h2>--- Day 1: Secret Entrance ---</h2>"
            "<p>Intro with <code>inline</code> &amp; <em>bold</em>.</p>"
            "<p>For example:</p>"
            "<pre><code><em>L68</em>\nL30 &lt; R48\n</code></pre>"
            "<pre><code>tiny</code></pre>"
            "</article>"
            '<article class="day-desc">'
            '<h2 id="part2">--- Part Two ---</h2>'
            "<p>Second part question: <em>what is the password?</em></p>"
            "</article>"
            "</main>"
            "</body></html>"
        )
        page = ac.parse_puzzle_html(html, year=2025, day=1)

        self.assertEqual(page.title, "Secret Entrance")
        self.assertTrue(page.authenticated)
        self.assertIn("`inline`", page.part1_markdown)
        self.assertIn("**bold**", page.part1_markdown)
        self.assertIsNotNone(page.part2_markdown)
        assert page.part2_markdown is not None
        self.assertIn("**what is the password?**", page.part2_markdown)
        self.assertEqual(len(page.samples), 2)
        self.assertEqual(page.samples[0].text, "L68\nL30 < R48")
        self.assertGreater(page.samples[0].score, page.samples[1].score)

    def test_parse_puzzle_html_nested_code_em_and_li_pre(self):
        """Suppress bold markers inside inline code and flush list text before nested <pre> blocks."""
        html = (
            "<main>"
            '<article class="day-desc">'
            "<h2>--- Day 7: Some Assembly ---</h2>"
            "<p>Answer is <code><em>CABDFE</em></code>, "
            "policy <code>1-3 a: <em>a</em>bcde</code>, "
            "or <em><code>142</code></em>.</p>"
            "<ul>"
            "<li>For example:<pre><code>Step C\nStep A\n</code></pre></li>"
            "</ul>"
            "</article>"
            "</main>"
        )
        page = ac.parse_puzzle_html(html, year=2018, day=7)

        self.assertIn("Answer is `CABDFE`", page.part1_markdown)
        self.assertIn("policy `1-3 a: abcde`", page.part1_markdown)
        self.assertIn("or **`142`**.", page.part1_markdown)
        self.assertNotIn("**CABDFE**", page.part1_markdown)
        self.assertNotIn("**a**", page.part1_markdown)

        li_pos = page.part1_markdown.index("- For example:")
        pre_pos = page.part1_markdown.index("```\nStep C\nStep A\n```")
        self.assertLess(li_pos, pre_pos)

        self.assertEqual(len(page.samples), 1)
        self.assertEqual(page.samples[0].context, "For example:")
        self.assertGreaterEqual(page.samples[0].score, 70)

    def test_fetch_puzzle_page_optional_cookie_and_http_error(self):
        """Allow anonymous page fetches when AOC_SESSION_COOKIE is absent and fail loudly on HTTP errors."""
        ok_html = (
            '<main><article class="day-desc"><h2>--- Day 1: Secret Entrance ---</h2>'
            "<p>For example:</p><pre><code>L68\n</code></pre></article></main>"
        )
        ok_resp = MagicMock(status_code=200, text=ok_html)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("aoc_common.aoc_commons.load_dotenv"),
            patch("aoc_common.aoc_commons.requests.get", return_value=ok_resp) as mock_get,
        ):
            page = ac.fetch_puzzle_page(2025, 1)

        self.assertEqual(page.title, "Secret Entrance")
        self.assertFalse(page.authenticated)
        self.assertIsNone(mock_get.call_args.kwargs["cookies"])
        self.assertEqual(mock_get.call_args.kwargs["headers"], {"User-Agent": ac.AOC_USER_AGENT})

        err_resp = MagicMock(status_code=404, reason="Not Found", content=b"404 Not Found")
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("aoc_common.aoc_commons.load_dotenv"),
            patch("aoc_common.aoc_commons.requests.get", return_value=err_resp),
            self.assertRaises(ValueError) as ctx,
        ):
            ac.fetch_puzzle_page(2025, 1)
        self.assertIn("Unable to retrieve puzzle description", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)  # if we want to include function names and docstring headers
    # unittest.main()
