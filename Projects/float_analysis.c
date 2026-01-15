#include <stdio.h>
#include <stdint.h>
#include <math.h>

int main(void) {
    uint64_t nan_count = 0, pos_inf = 0, neg_inf = 0;
    uint64_t pos_zero = 0, neg_zero = 0;
    uint64_t pos_subnormal = 0, neg_subnormal = 0;
    uint64_t pos_normal = 0, neg_normal = 0;

    for (uint64_t i = 0; i <= 0xFFFFFFFF; i++) {
        uint32_t bits = (uint32_t)i;
        union { uint32_t u; float f; } u = { .u = bits };
        float f = expf(u.f);

        union { float f; uint32_t u; } result = { .f = f };
        uint32_t rbits = result.u;

        uint32_t sign = (rbits >> 31) & 1;
        uint32_t exp = (rbits >> 23) & 0xFF;
        uint32_t mantissa = rbits & 0x7FFFFF;

        if (exp == 0xFF) {
            if (mantissa != 0) nan_count++;
            else if (sign) neg_inf++;
            else pos_inf++;
        } else if (exp == 0) {
            if (mantissa == 0) {
                if (sign) neg_zero++;
                else pos_zero++;
            } else {
                if (sign) neg_subnormal++;
                else pos_subnormal++;
            }
        } else {
            if (sign) neg_normal++;
            else pos_normal++;
        }
    }

    uint64_t total = 0x100000000ULL;

    printf("Category             Count          Percentage\n");
    printf("------------------------------------------------\n");
    printf("NaN                  %12lu   %3lu%%\n", nan_count, (nan_count * 100 + total/2) / total);
    printf("Positive Infinity    %12lu   %3lu%%\n", pos_inf, (pos_inf * 100 + total/2) / total);
    printf("Negative Infinity    %12lu   %3lu%%\n", neg_inf, (neg_inf * 100 + total/2) / total);
    printf("Positive Zero        %12lu   %3lu%%\n", pos_zero, (pos_zero * 100 + total/2) / total);
    printf("Negative Zero        %12lu   %3lu%%\n", neg_zero, (neg_zero * 100 + total/2) / total);
    printf("Positive Subnormal   %12lu   %3lu%%\n", pos_subnormal, (pos_subnormal * 100 + total/2) / total);
    printf("Negative Subnormal   %12lu   %3lu%%\n", neg_subnormal, (neg_subnormal * 100 + total/2) / total);
    printf("Positive Normal      %12lu   %3lu%%\n", pos_normal, (pos_normal * 100 + total/2) / total);
    printf("Negative Normal      %12lu   %3lu%%\n", neg_normal, (neg_normal * 100 + total/2) / total);
    printf("------------------------------------------------\n");
    printf("Total                %12lu\n", (unsigned long)total);

    return 0;
}
