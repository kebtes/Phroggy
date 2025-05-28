# from services.check_file import calc_sha256
# from services.check_file import send_file_for_scan, get_scan_report

# import asyncio

# async def main():
#     # id = await calc_sha256("sample.txt")
#     report = await send_file_for_scan("sample.txt")
#     msg = await get_scan_report(report)

#     # print(sha_val)
#     print(msg)

# asyncio.run(main())

from pathlib import Path

p = Path("sample.txt")
print(p)