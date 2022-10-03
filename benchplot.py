# Copyright (C) 2022 José Enrique Vilca Campana
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
# usage: plot.py [-h] [--xLabel [XLABEL]] [--title [TITLE]]
#                [--series SERIES [SERIES ...]]
#                INPUT [INPUT ...]

# Plots benchmark CSV outputs.

# positional arguments:
#   INPUT                 input file name

# optional arguments:
#   -h, --help            show this help message and exit
#   --xLabel [XLABEL]     Label for the X axis
#   --title [TITLE]       Title of the plot
#   --series SERIES [SERIES ...]
#                         Series names to be shown on the plot
# ------------------------------------------------------------------------------
# Example call:
# python3 plot.py plot_test.json
# ------------------------------------------------------------------------------
import argparse
import json
import pathlib
import sys

import matplotlib.pyplot as plt


def set_parser_arguments():
    parser = argparse.ArgumentParser(
        description="Visualize google-benchmark json output",
        epilog="script designed by @marcusmors",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "input",
        metavar="<file>",
        type=str,
        nargs=1,
        help="path to file.json with benchmark data",
        # required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="<output>",
        default="output",
        type=str,
        nargs=1,
        help="Place the output into <file>.png",
        # required=True,
    )

    parser.add_argument(
        "-t",
        "--benchmark_type",
        type=str,
        nargs="?",
        choices=["simple", "central_tendency"],
        default="simple",
        help="Type of benchmark to plot {simple|central_tendency}",
    )

    parser.add_argument(
        "--x_label",
        dest="x_label",
        default="Data Size",
        type=str,
        nargs="?",
        help="Label for the X axis",
    )

    parser.add_argument(
        "--title",
        dest="title",
        default="Run Time",
        type=str,
        nargs="?",
        help="Title of the plot",
    )

    return parser


def new_plot_elem():
    obj: dict = {
        "name": "",
        "data_size": [],
        "real_time": [],
    }
    return obj


def get_mean_raw_benchmarks(raw_benchmarks):
    mean_raw_benchmarks: list = []
    for elem in raw_benchmarks:
        if "_mean" == elem["name"][-len("_mean") :]:
            mean_raw_benchmarks.append(elem)
    return mean_raw_benchmarks


def main():
    # Set input arguments
    parser = set_parser_arguments()
    args = parser.parse_args()

    # Read input json file
    parsed_benchmarks: list[dict] = []
    time_unit: str = ""
    with open(args.input[0]) as json_file:
        data = json.load(json_file)
        if args.benchmark_type == "simple":
            parsed_benchmarks = data["benchmarks"]
        else:
            if args.title == "Run Time":
                args.title = "Run Time Mean"

            raw_benchmarks = data["benchmarks"]
            time_unit = raw_benchmarks[0]["time_unit"]
            mean_raw_benchmarks = get_mean_raw_benchmarks(raw_benchmarks)
            for elem in mean_raw_benchmarks:
                [name, data_size] = elem["name"].split("/")
                elem["name"] = name[3:]
                # elem["name"] = name[3:] + "_mean"
                elem["data_size"] = data_size[: len("_mean") + 1]
                elem.pop("run_name")
                elem.pop("run_type")
                elem.pop("repetitions")
                elem.pop("aggregate_name")
                elem.pop("threads")
                elem.pop("iterations")
                elem.pop("cpu_time")
                elem.pop("time_unit")
                # print(elem["name"], "\t", elem["real_time"], "\t", elem["data_size"])
            parsed_benchmarks = mean_raw_benchmarks

    plot_list: list[dict] = []
    plot_elem: dict = new_plot_elem()

    # adding a disruptor guard
    parsed_benchmarks.append(plot_elem)

    plot_elem["name"] = parsed_benchmarks[0]["name"]
    plot_elem["data_size"].append(parsed_benchmarks[0]["data_size"])
    plot_elem["real_time"].append(parsed_benchmarks[0]["real_time"])
    for i in range(1, len(parsed_benchmarks)):  # [1:n)
        prev_elem = parsed_benchmarks[i - 1]
        elem = parsed_benchmarks[i]
        if prev_elem["name"] == elem["name"]:
            plot_elem["data_size"].append(elem["data_size"])
            plot_elem["real_time"].append(elem["real_time"])
        else:
            plot_list.append(plot_elem)
            plot_elem = new_plot_elem()
            plot_elem["name"] = elem["name"]
            plot_elem["data_size"].append(elem["data_size"])
            plot_elem["real_time"].append(elem["real_time"])

    # print("-------------- HERE COMES THE ELEMENTS --------------")
    # for elem in plot_list:
    #     print(f'name : {elem["name"]}')
    #     print(f'data_size : {elem["data_size"]}')
    #     print(f'real_time : {elem["real_time"]}')
    #     print("\n")

    # Draw the plot
    plt.figure(figsize=(15, 10))
    for elem in plot_list:
        plt.plot(
            elem["data_size"],
            elem["real_time"],
            label=elem["name"],
            # figsize=(15, 10),
            # legend=True,
            # fontsize=12,
            # rot=0,
        )
    plt.legend(fontsize=16, loc="upper left", frameon=False)
    plt.title(args.title)
    plt.xlabel(args.x_label, fontsize=16)
    plt.ylabel("time in " + time_unit, fontsize=16)
    # output_file: str = str(args.output)
    plt.savefig(str(args.output[0]), transparent=False, bbox_inches="tight")


if __name__ == "__main__":
    main()

# i found a similar project, try to improve this.
# https://github.com/lakshayg/google_benchmark_plot/blob/master/plot.py
