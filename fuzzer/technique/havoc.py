# Copyright (C) 2017-2019 Sergej Schumilo, Cornelius Aschermann, Tim Blazytko
# Copyright (C) 2019-2020 Intel Corporation
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
AFL-style havoc and splicing stage 
"""

import glob

from common.config import FuzzerConfiguration
from fuzzer.technique.havoc_handler import *


def load_dict(file_name):
    f = open(file_name)
    dict_entries = []
    for line in f:
        if not line.startswith("#"):
            try:
                dict_entries.append((line.split("=\"")[1].split("\"\n")[0]).encode('latin1').decode('unicode-escape').encode('latin1'))
            except:
                pass
    f.close()
    return dict_entries


def init_havoc(config):
    global location_corpus
    if config.argument_values["dict"]:
        set_dict(load_dict(FuzzerConfiguration().argument_values["dict"]))
    # AFL havoc adds these at runtime as soon as available dicts are non-empty
    if config.argument_values["dict"] or config.argument_values["redqueen"]:
        append_handler(havoc_dict_insert)
        append_handler(havoc_dict_replace)

    location_corpus = config.argument_values['work_dir'] + "/corpus/"


def havoc_range(perf_score):
    max_iterations = int(2*perf_score)

    if max_iterations < AFL_HAVOC_MIN:
        max_iterations = AFL_HAVOC_MIN

    return max_iterations


def mutate_seq_havoc_array(data, func, max_iterations, pso=None, resize=False):
    if resize:
        data = data + data
    else:
        data = data
        
    for _ in range(max_iterations):
        stacking = rand.int(AFL_HAVOC_STACK_POW2)

        for _ in range(1 << (1 + stacking)):
            if pso:
                data = pso.select_and_run_handler(data)
            else:
                handler = rand.select(havoc_handler)
                data = handler(data)
                if len(data) >= KAFL_MAX_FILE:
                    data = data[:KAFL_MAX_FILE]
        
        recv = func(data, need_hits=True)
        if pso:
            pso.update(sum(recv))


def mutate_seq_splice_array(data, func, max_iterations, pso=None, resize=False):
    global location_corpus
    files = glob.glob(location_corpus + "/regular/payload_*")
    for _ in range(AFL_SPLICE_ROUNDS):
        spliced_data = havoc_splicing(data, files)
        mutate_seq_havoc_array(spliced_data,
                               func,
                               int(2*max_iterations/AFL_SPLICE_ROUNDS),
                               pso=pso,
                               resize=resize)