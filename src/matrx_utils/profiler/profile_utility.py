import cProfile
import pstats
import io
import os
from contextlib import ContextDecorator
import datetime
from matrx_utils.conf import settings

class MatrxProfiler(ContextDecorator):
    def __init__(
        self,
        filename=None,
        sort_by="cumulative",
        limit=20,
        save_output=False,
        verbose=False,
        include_exclusions=False,
    ):
        """
        A utility class for profiling code blocks or functions.

        Parameters:
        - filename: Filename to save the profile stats (if save_output is True).
        - sort_by: Metric to sort by ('cumulative' or 'tottime').
        - limit: Limit the number of lines in the output.
        - save_output: Whether to save the profiling output to a file.
        - verbose: Whether to print detailed profiling information.
        - include_exclusions: Whether to include or exclude functions from the exclusion list.
        """
        self.profiler = cProfile.Profile()
        self.filename = filename
        self.sort_by = sort_by
        self.limit = limit
        self.save_output = save_output
        self.verbose = verbose
        self.include_exclusions = include_exclusions
        self.output_dir = settings.TEMP_DIR / "code_standards" / "profiler" / "outputs"
        self.exclusion_list = ["vcprint", "fancy_prints", "logging", "re", "encoder"]

    def __enter__(self):
        self.profiler.enable()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.profiler.disable()
        self._print_stats()
        if self.save_output:
            self._save_stats()

    def _print_stats(self):
        stats = pstats.Stats(self.profiler).sort_stats(self.sort_by)
        if not self.include_exclusions:
            stats = self._apply_exclusions(stats)
        print("\n---- Profiling Summary ----\n")
        stats.print_stats(self.limit)

    def _save_stats(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not self.filename:
            self.filename = os.path.join(
                self.output_dir,
                f"profile_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
        stats = pstats.Stats(self.profiler, stream=io.StringIO()).sort_stats(self.sort_by)
        if not self.include_exclusions:
            stats = self._apply_exclusions(stats)
        buffer = io.StringIO()
        stats.stream = buffer
        stats.print_stats(self.limit)
        content = buffer.getvalue()
        if self.verbose and not self.include_exclusions:
            exclusions_note = "Excluded: " + ", ".join(self.exclusion_list) + "\n"
            exclusions_note += "To include above, use 'include_exclusions=True'\n\n"
            content = exclusions_note + content
        with open(self.filename, "w") as f:
            f.write(content)
        print(f"Profiler output saved to: {self.filename}")
        print("\n ---- End Profiling Summary ----\n")

    def _apply_exclusions(self, stats):
        """
        Apply exclusions to the stats object based on the exclusion list.
        This removes entries in the profiler output that match the exclusion criteria.
        """
        # Create a new Stats object for filtered stats
        filtered_stats = pstats.Stats()
        filtered_stats.stream = stats.stream

        # Filter functions based on the exclusion list
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            filename, lineno, func_name = func
            if not any(exclude in filename or exclude in func_name for exclude in self.exclusion_list):
                filtered_stats.stats[func] = (cc, nc, tt, ct, callers)

        filtered_stats.files = stats.files
        return filtered_stats


# Example usage:
if __name__ == "__main__":
    my_variable = "Use This Pattern for Profiling Code Blocks"
    from matrx_utils import vcprint, clear_terminal
    clear_terminal()

    with MatrxProfiler(
        sort_by="tottime",
        limit=30,
        save_output=True,
        verbose=True,
        include_exclusions=True,
    ) as profiler:
        try:
            vcprint("This is where your code goes...")
            vcprint(my_variable)
            vcprint("using normal print to avoid importing anything else into this script for profiling")

        except Exception as e:
            print(f"An error occurred: {e}")
