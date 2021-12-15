from setuptools import setup

setup(
    name="aoc-miyagi-2021",
    version="0.1",
    url="https://github.com/maxfischer2781/aoc2021_py",
    packages=["aoc2021"],
    entry_points={"adventofcode.user": ["miyagi = aoc2021:plugin"]},
)
