from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import tqdm


def zip_all(dst, *, copy=None, create=None, progress=False):
    if copy is None:
        copy = {}
    if create is None:
        create = {}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dst, mode="w", compression=ZIP_DEFLATED) as z:
        if progress:
            copy_pairs = tqdm.tqdm(copy.items(), unit = " files")
            create_pairs = tqdm.tqdm(create.items(), unit = " files")
        else:
            copy_pairs = copy.items()
            create_pairs = create.items()

        if progress:
            print("Copying files to zip...")
        for newname, srcpath in copy_pairs:
            data = Path(srcpath).read_bytes()
            z.writestr(newname, data)

        if progress:
            print("Writing logs to zip...")
        for newname, data in create_pairs:
            z.writestr(newname, data)
