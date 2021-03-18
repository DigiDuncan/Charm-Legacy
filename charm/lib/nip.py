from pathlib import Path
from typing import Literal, Union
from zipfile import ZipFile, ZIP_DEFLATED

import tqdm


def build_all(dst, *, copy=None, create=None, progress=False, clean=False):
    return n_all(dst, dst_type="dir", copy=copy, create=create, progress=progress, clean=clean)


def zip_all(dst, *, copy=None, create=None, progress=False):
    return n_all(dst, dst_type="zip", copy=copy, create=create, progress=progress)


def n_all(dst: Union[Path, str], *, dst_type: Literal["dir", "zip"], copy=None, create=None, progress=False, clean=False):
    if dst_type not in ("dir", "zip"):
        raise ValueError(f"Invalid dst_type: {dst_type}")
    dst = Path(dst)
    if copy is None:
        copy = {}
    if create is None:
        create = {}

    if clean and dst_type == "dir":
        dst.unlink(missing_ok=True)

    if dst_type == "zip":
        dst.parent.mkdir(parents=True, exist_ok=True)
    elif dst_type == "dir":
        dst.mkdir(parents=True, exist_ok=True)

    copy_pairs = copy.items()
    create_pairs = create.items()
    if progress:
        default_bar_format = "{l_bar}{bar}{r_bar}"
        copy_pairs = tqdm.tqdm(copy_pairs, unit = " files")
        copy_pairs.bar_format = f"Copying {len(copy_pairs)} existing files to {dst_type}...\n" + default_bar_format
        create_pairs = tqdm.tqdm(create_pairs, unit = " files")
        create_pairs.bar_format = f"Adding {len(create_pairs)} new files to {dst_type}...\n" + default_bar_format

    from contextlib import ExitStack

    # This ExitStack thing means that my "with ZipFile() as z" call can be used conditionally
    with ExitStack() as stack:
        if dst_type == "zip":
            z = stack.enter_context(ZipFile(dst, mode="w", compression=ZIP_DEFLATED))
            savefn = zip_save(z)
        elif dst_type == "dir":
            savefn = file_save(dst)

        copy_files(copy_pairs,  savefn)
        create_files(create_pairs,  savefn)


def zip_save(z):
    def save(name, data):
        z.writestr(name, data)
    return save


def file_save(dst):
    def save(name, data):
        filedst = dst / name
        if isinstance(data, bytes):
            filedst.write_bytes(data)
        else:
            filedst.write_text(data)
    return save


def copy_files(copy_pairs, save):
    for newname, srcpath in copy_pairs:
        data = Path(srcpath).read_bytes()
        save(newname, data)


def create_files(create_pairs, save):
    for newname, data in create_pairs:
        save(newname, data)
