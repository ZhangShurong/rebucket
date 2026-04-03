#include "rebucket.h"
#include "rapidjson/document.h"
#include <cmath>
#include <algorithm>
#include <limits>
#include <mutex>
#include <string>
#include <vector>
#include <omp.h>
using namespace rapidjson;

/**
 * @brief Global buckets.
 *
 * NOTE: This state makes the library unsuitable for multi-request server usage.
 * We provide `rebucket_reset()` and a mutex to keep behavior deterministic.
 */
static std::vector<Bucket> buckets;
static std::mutex g_buckets_mu;

static bool json_to_stack(const char* json, Stack* out) {
    if (!out) {
        return false;
    }
    out->stack_id.clear();
    out->frames.clear();

    if (!json) {
        return false;
    }

    Document d;
    d.Parse(json);
    if (d.HasParseError() || !d.IsObject()) {
        return false;
    }

    if (!d.HasMember("stack_id") || !d["stack_id"].IsString()) {
        return false;
    }
    if (!d.HasMember("stack_arr") || !d["stack_arr"].IsArray()) {
        return false;
    }

    out->stack_id.assign(d["stack_id"].GetString(), d["stack_id"].GetStringLength());
    const auto& arr = d["stack_arr"].GetArray();
    out->frames.reserve(arr.Size());
    for (SizeType i = 0; i < arr.Size(); ++i) {
        if (!arr[i].IsString()) {
            return false;
        }
        out->frames.emplace_back(arr[i].GetString(), arr[i].GetStringLength());
    }
    return true;
}

static double get_dist(const Stack& stack1, const Stack& stack2)
{
    double c = 0.04;
    double o = 0.13;
    int stack_len1 = stack1.frames.size();
    int stack_len2 = stack2.frames.size();
    if(stack_len1 == 1 || stack_len2 == 1) {
        return 1.0;
    }
    // FIXME: Current implementation is O(n*m) DP and is sensitive to stack order.
    std::vector<std::vector<double> > M(stack_len1 + 1, std::vector<double>(stack_len2 + 1));

    for(int i = 1; i < stack_len1 + 1; ++i){
        for(int j = 1; j < stack_len2 + 1; ++j) {
            double x = 0;
            if(stack1.frames[i - 1] == stack2.frames[j - 1]){
                x = exp(-c*min(i-1, j-1)) * exp(-o*abs(i-j));
            }
            M[i][j] = max(max(M[i-1][j-1] + x, M[i-1][j]), M[i][j-1]);
        }
    }
    double sig = 0;
    for (int i = 0; i < min(stack_len1, stack_len2); ++i){
        sig += exp(-c * i);
    }
    double sim = M[stack_len1][stack_len2] / sig;
    return 1.0 - sim;

}

const char* single_pass_clustering(const char* stack_json)
{
    // Returned pointer must remain valid after the function returns.
    static thread_local std::string ret;
    ret.clear();

    Stack stack;
    if (!json_to_stack(stack_json, &stack)) {
        return ret.c_str();
    }
    if (stack.stack_id.empty()) {
        return ret.c_str();
    }

    // Serialize access to global state.
    std::lock_guard<std::mutex> lock(g_buckets_mu);

    double min_dist = std::numeric_limits<double>::infinity();
    int min_index = -1;

    // Safe parallel min search.
    const int n = static_cast<int>(buckets.size());
    #pragma omp parallel
    {
        double local_min = std::numeric_limits<double>::infinity();
        int local_idx = -1;
        #pragma omp for nowait
        for (int i = 0; i < n; ++i) {
            if (buckets[i].stacks.empty()) {
                continue;
            }
            const double dist = get_dist(stack, buckets[i].stacks[0]);
            if (dist < local_min) {
                local_min = dist;
                local_idx = i;
            }
        }
        #pragma omp critical
        {
            if (local_min < min_dist) {
                min_dist = local_min;
                min_index = local_idx;
            }
        }
    }

    std::string bucket_id = stack.stack_id;

    const double kThreshold = 0.06;
    if (min_index >= 0 && min_dist < kThreshold) {
        buckets[min_index].stacks.push_back(stack);
        bucket_id = buckets[min_index].bucket_id;
    } else {
        Bucket bucket;
        bucket.bucket_id = stack.stack_id;
        bucket.stacks.push_back(stack);
        buckets.push_back(bucket);
    }

    ret = bucket_id;
    return ret.c_str();
}
void free_buffer(const char* str_ptr)
{
    // Deprecated: `single_pass_clustering()` returns an internal buffer.
    // Keep this symbol for backward compatibility.
    (void)str_ptr;
}

void rebucket_reset() {
    std::lock_guard<std::mutex> lock(g_buckets_mu);
    buckets.clear();
}

size_t rebucket_bucket_count() {
    std::lock_guard<std::mutex> lock(g_buckets_mu);
    return buckets.size();
}
