// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstddef>
#include <cstdint>
#include <span>

namespace Core::Bloodborne::Chalice {
// A map identifies a floor template, never a generated dungeon. No native pointers on wire.
struct Key {
    std::uint64_t channel = 0;
    std::uint64_t form_hash = 0;
    std::uint32_t form_size = 0;
    std::uint32_t form_version = 0;
    bool operator==(const Key&) const = default;
};
static_assert(sizeof(Key) == 24);
constexpr bool IsMap(std::uint32_t map) { return (map >> 24) == 29; }
constexpr bool IsLootGroup(std::uint32_t key) {
    return key / 10000 == 5 && (key % 10000) / 100 == 29;
}
constexpr bool Valid(const Key& key) {
    return key.channel != 0 && key.channel < (std::uint64_t{1} << 63) &&
           key.form_hash != 0 && key.form_size >= 16 && key.form_size <= 1024 &&
           key.form_version == 0;
}
inline std::uint64_t HashForm(std::span<const std::uint8_t> bytes) {
    std::uint64_t hash = 14695981039346656037ULL;
    for (auto byte : bytes) { hash ^= byte; hash *= 1099511628211ULL; }
    return hash;
}
// Expired, unscoped and another dungeon's state must never unblock a dungeon load.
constexpr bool CanUse(const Key& local, const Key& host, std::int64_t age_ms) {
    return Valid(local) && Valid(host) && local == host && age_ms >= 0 && age_ms < 6000;
}
} // namespace Core::Bloodborne::Chalice
