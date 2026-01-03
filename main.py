import os
import sys

src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)
os.chdir(src_dir)

from bot import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
