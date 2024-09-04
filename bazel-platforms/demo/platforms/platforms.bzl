SUPPORTED_TARGET_TUPLES = [
    {"cpu": "x86_64", "os": "windows", "cpp_compiler": "mingw"},
    {"cpu": "x86_64", "os": "linux",   "cpp_compiler": "gcc"},
]

SUPPORTED_PLATFORMS = {
    "{os}_{cpu}_{cpp_compiler}".format(
        cpu=target_tuple["cpu"],
        os=target_tuple["os"],
        cpp_compiler=target_tuple["cpp_compiler"],
    ): {
        "constraint_values": [
            "@platforms//os:" + target_tuple["os"],
            "@platforms//cpu:" + target_tuple["cpu"],
            "@bazel_tools//tools/cpp:" + target_tuple["cpp_compiler"],
        ],
    }
    for target_tuple in SUPPORTED_TARGET_TUPLES
}