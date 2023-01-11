# Copyright 2017-2019 Sergej Schumilo, Cornelius Aschermann, Tim Blazytko
# Copyright 2019-2020 Intel Corporation
#
# SPDX-License-Identifier: AGPL-3.0-or-later

ACQUIRE = b'R'
RELEASE = b'D'

RELOAD = b'L'
ENABLE_SAMPLING = b'S'
DISABLE_SAMPLING = b'O'
COMMIT_FILTER = b'T'
FINALIZE = b'F'
CONNECT = b'Y'

ENABLE_RQI_MODE = b'A'
DISABLE_RQI_MODE = b'B'
ENABLE_TRACE_MODE = b'E'
DISABLE_TRACE_MODE = b'G'
ENABLE_PATCHES = b'P'
DISABLE_PATCHES = b'Q'
REDQUEEN_SET_LIGHT_INSTRUMENTATION = b'U'
REDQUEEN_SET_WHITELIST_INSTRUMENTATION = b'W'
REDQUEEN_SET_BLACKLIST = b'X'

CRASH = b'C'
KASAN = b'K'
INFO = b'I'
TIMEOUT = b't'

PRINTF = b'X'

PT_TRASHED = b'Z'
PT_TRASHED_CRASH = b'M'
PT_TRASHED_KASAN = b'N'

ABORT = b'H'

CMDS = {
    ACQUIRE: "ACQUIRE",
    RELEASE: "RELEASE",
    RELOAD: "RELOAD",

    ENABLE_SAMPLING: "ENABLE_SAMPLING",
    DISABLE_SAMPLING: "DISABLE_SAMPLING",
    COMMIT_FILTER: "COMMIT_FILTER",
    FINALIZE: "FINALIZE",
    CONNECT: "CONNECT",

    ENABLE_RQI_MODE: "ENABLE_RQI_MODE",
    DISABLE_RQI_MODE: "DISABLE_RQI_MODE",

    ENABLE_TRACE_MODE: "ENABLE_TRACE_MODE",
    DISABLE_TRACE_MODE: "DISABLE_TRACE_MODE",
    ENABLE_PATCHES: "ENABLE_PATCHES",
    DISABLE_PATCHES: "DISABLE_PATCHES",
    REDQUEEN_SET_LIGHT_INSTRUMENTATION: "REDQUEEN_SET_LIGHT_INSTRUMENTATION",
    REDQUEEN_SET_WHITELIST_INSTRUMENTATION: "REDQUEEN_SET_WHITELIST_INSTRUMENTATION",
    REDQUEEN_SET_BLACKLIST: "REDQUEEN_SET_BLACKLIST",

    CRASH: "CRASH",
    KASAN: "KASAN",
    INFO: "INFO",

    PRINTF: "PRINTF",

    PT_TRASHED: "PT_TRASHED",
    PT_TRASHED_CRASH: "PT_TRASHED_CRASH",
    PT_TRASHED_KASAN: "PT_TRASHED_KASAN",

    ABORT: "ABORT",
}
