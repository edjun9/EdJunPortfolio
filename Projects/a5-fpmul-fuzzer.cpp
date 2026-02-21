#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>

static float fpmul(float a, float b) {
  uint32_t ai, bi;
  memcpy(&ai, &a, 4);
  memcpy(&bi, &b, 4);

  uint32_t as = ai >> 31;
  uint32_t ae = (ai >> 23) & 0xFF;
  uint32_t am = ai & 0x7FFFFF;

  uint32_t bs = bi >> 31;
  uint32_t be = (bi >> 23) & 0xFF;
  uint32_t bm = bi & 0x7FFFFF;

  uint32_t afm = (1 << 23) | am;
  uint32_t bfm = (1 << 23) | bm;

  uint64_t fullm = static_cast<uint64_t>(afm) * bfm;
  uint32_t needs_shift = (fullm >> 47) & 1;
  uint64_t shiftm = needs_shift ? fullm : (fullm << 1);

  uint32_t guard = (shiftm >> 23) & 1;
  uint32_t sticky = (shiftm & 0x7FFFFF) ? 1 : 0;
  uint32_t lsb = (shiftm >> 24) & 1;
  uint32_t round_up = (guard & sticky) | (guard & ~sticky & lsb);

  uint32_t ym = ((shiftm >> 24) & 0x7FFFFF) + round_up;
  uint32_t fulle = ae + be - 127 + needs_shift;
  uint32_t ye = fulle & 0xFF;

  uint32_t ys = as ^ bs;

  uint32_t yi = (ys << 31) | (ye << 23) | (ym & 0x7FFFFF);

  float y;
  memcpy(&y, &yi, 4);
  return y;
}

static uint32_t to_bits(float value) {
  uint32_t bits = 0;
  memcpy(&bits, &value, 4);
  return bits;
}

static bool is_normal_bits(uint32_t bits) {
  uint32_t exp = (bits >> 23) & 0xFF;
  return exp > 0 && exp < 0xFF;
}

static float random_normal(std::mt19937_64 &rng) {
  std::uniform_int_distribution<uint32_t> sign_dist(0, 1);
  std::uniform_int_distribution<uint32_t> exp_dist(1, 254);
  std::uniform_int_distribution<uint32_t> mant_dist(0, 0x7FFFFF);

  uint32_t sign = sign_dist(rng);
  uint32_t exp = exp_dist(rng);
  uint32_t mantissa = mant_dist(rng);
  uint32_t bits = (sign << 31) | (exp << 23) | mantissa;
  float value;
  memcpy(&value, &bits, 4);
  return value;
}

int main() {
  std::random_device rd;
  std::mt19937_64 rng(rd());

  for (;;) {
    float a = random_normal(rng);
    float b = random_normal(rng);

    float expected = a * b;
    uint32_t expected_bits = to_bits(expected);
    if (!is_normal_bits(expected_bits)) {
      continue;
    }

    float actual = fpmul(a, b);
    if (to_bits(actual) != expected_bits) {
      std::printf("a=%a b=%a expected=%a actual=%a\n", a, b, expected, actual);
      return 0;
    }
  }
}
