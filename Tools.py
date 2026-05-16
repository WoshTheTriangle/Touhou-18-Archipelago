def getPointerAddress(pm, base, offsets) -> int:
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset

    return pm.read_uint(address) + offsets[-1]
