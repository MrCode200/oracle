def isfloat(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

print("0.8".isdecimal())