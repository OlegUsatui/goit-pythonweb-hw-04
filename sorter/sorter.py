import asyncio
import shutil
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def copy_file(file_path: Path, output_folder: Path):
    extension = file_path.suffix.lstrip('.') or "no_extension"
    destination_folder = output_folder / extension
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination_path = destination_folder / file_path.name

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, shutil.copy2, file_path, destination_path)
    logging.info(f"Copied: {file_path} -> {destination_path}")

async def read_folder(source_folder: Path, output_folder: Path):
    tasks = []
    async for file_path in _iter_files(source_folder):
        tasks.append(copy_file(file_path, output_folder))
    await asyncio.gather(*tasks)

async def _iter_files(folder: Path):
    for item in folder.iterdir():
        if item.is_dir():
            async for sub_item in _iter_files(item):
                yield sub_item
        else:
            yield item

def main():
    parser = argparse.ArgumentParser(description="Sort files by extension into subfolders.")
    parser.add_argument("source", type=str, help="Path to the source folder.")
    parser.add_argument("output", type=str, help="Path to the output folder.")
    args = parser.parse_args()

    source_folder = Path(args.source).resolve()
    output_folder = Path(args.output).resolve()
    print(source_folder, output_folder)
    if not source_folder.is_dir():
        logging.error(f"Source folder does not exist: {source_folder}")
        exit(1)

    output_folder.mkdir(parents=True, exist_ok=True)

    logging.info("Starting file sorting...")
    asyncio.run(read_folder(source_folder, output_folder))
    logging.info("File sorting completed.")
