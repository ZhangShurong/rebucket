#ifndef REBUCKET_H_
#define REBUCKET_H_

#include <cstddef>
#include <string>
#include <vector>

using namespace std;

/**
 * @brief A stack trace sample.
 */
struct Stack {
    string stack_id;
    vector<string> frames;
};

/**
 * @brief A cluster bucket.
 */
struct Bucket {
    string bucket_id;
    vector<Stack> stacks;
};

extern "C" {

/**
 * @brief Perform single-pass clustering on one stack json.
 *
 * Input json format (expected):
 *   {"stack_id":"...","stack_arr":["frame1","frame2", ...]}
 *
 * @return A pointer to a NUL-terminated string.
 *         The returned pointer is valid until the next call in the same thread.
 *         On invalid input, returns an empty string.
 */
const char* single_pass_clustering(const char* stack_json);

/**
 * @brief Reset internal global state (clear all buckets).
 */
void rebucket_reset();

/**
 * @brief Get current bucket count.
 */
size_t rebucket_bucket_count();

/**
 * @brief Deprecated. Kept for ABI compatibility. No-op.
 */
void free_buffer(const char* str_ptr);

}  // extern "C"

#endif  // REBUCKET_H_
