import aiofiles
import hashlib

async def calc_hash(file_path: str):
    return {
        "md5"   : await calc_md5(file_path),
        "sha1"  : await calc_sha1(file_path),
        "sha256": await calc_sha256(file_path)
    }

async def calc_sha256(file_path: str):
    sha256_hash = hashlib.sha256()

    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

async def calc_sha1(file_path: str):
    sha1_hash = hashlib.sha1()

    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            sha1_hash.update(chunk)
        
    return sha1_hash.hexdigest()

async def calc_md5(file_path: str):
    md5_hash = hashlib.md5()

    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            md5_hash.update(chunk)
        
    return md5_hash.hexdigest()