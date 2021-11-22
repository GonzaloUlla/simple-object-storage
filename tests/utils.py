from uuid import UUID


def get_uuid(bucket: str, _id: int) -> UUID:
    return UUID(f"00000000-0000-0000-0000-0000000000{bucket[-1]}{_id}")
