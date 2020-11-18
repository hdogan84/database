def santize_altitude(value: str):
    result = value.strip()
    if result.startswith("<"):
        result = result.split("<")[1]
    tmp = result.split("-")
    if len(tmp) > 1:
        result = int(tmp[0])
    if result == "?" or result == "NULL":
        return None
    try:
        return int(result)
    except:
        return None


# print(santize_altitude("< 1"))


# print(santize_altitude("2 - 300"))

# print(santize_altitude("3"))

# print(santize_altitude("ass a 4"))


def sanitize_name(value: str, max_length: int):
    if len(value) <= max_length:
        return value
    else:
        return value[:max_length]
    return len(value)


# print(sanitize_name("aaaa", 5))

# print(sanitize_name("aaaaabbb", 5))


def get_group_id(id: str) -> int:
    if id.startswith("g"):
        try:
            return int(id[1:])
        except:
            return None
    return None


print(get_group_id("g3a2"))
print(get_group_id("a12"))
