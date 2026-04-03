#include <cstring>
#include <iostream>

#include "rebucket.h"

static void expect_true(bool cond, const char* msg) {
    if (!cond) {
        std::cerr << "[FAIL] " << msg << "\n";
        std::exit(1);
    }
}

static void expect_streq(const char* a, const char* b, const char* msg) {
    if (!a || !b || std::strcmp(a, b) != 0) {
        std::cerr << "[FAIL] " << msg << ", got='" << (a ? a : "<null>") << "' expected='" << (b ? b : "<null>")
                  << "'\n";
        std::exit(1);
    }
}

int main() {
    rebucket_reset();
    expect_true(rebucket_bucket_count() == 0, "bucket count should start from 0");

    // First stack always creates a new bucket.
    const char* s1 = "{\"stack_id\":\"1\",\"stack_arr\":[\"a\",\"b\",\"c\",\"d\"]}";
    const char* r1 = single_pass_clustering(s1);
    expect_streq(r1, "1", "first clustering should return its stack_id");
    expect_true(rebucket_bucket_count() == 1, "bucket count should be 1 after first insert");

    // Identical frames should be clustered into existing bucket.
    const char* s2 = "{\"stack_id\":\"2\",\"stack_arr\":[\"a\",\"b\",\"c\",\"d\"]}";
    const char* r2 = single_pass_clustering(s2);
    expect_streq(r2, "1", "identical stacks should map to same bucket_id");
    expect_true(rebucket_bucket_count() == 1, "bucket count should remain 1 for identical stack");

    // Invalid json should not crash and should return empty string.
    const char* r3 = single_pass_clustering("{bad json");
    expect_streq(r3, "", "invalid json should return empty string");
    expect_true(rebucket_bucket_count() == 1, "bucket count should not change on invalid input");

    // Missing fields should return empty string.
    const char* r4 = single_pass_clustering("{}");
    expect_streq(r4, "", "missing fields should return empty string");

    std::cout << "[PASS] all tests\n";
    return 0;
}
