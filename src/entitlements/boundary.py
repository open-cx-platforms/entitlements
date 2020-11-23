import math
import re

BOUNDARY_START = r"(^|\r?\n)-*BEGIN .+? LICENSE-*\r?\n"
BOUNDARY_END = r"\r?\n-*END .+? LICENSE-*(\r?\n|$)"


def add_boundary(data, product_name):
    def complement(text, width):
        total_padding = max(width - len(text), 0)
        padding = total_padding / 2.0

        return "".join((
            "-" * math.ceil(padding),
            text,
            "-" * math.floor(padding),
        ))

    return "\n".join((
        complement("BEGIN {} LICENSE".format(product_name), 60),
        remove_boundary(data).strip(),
        complement("END {} LICENSE".format(product_name), 60),
    ))


def remove_boundary(data):
    after_boundary = re.split(BOUNDARY_START, data, maxsplit=1)[-1]
    in_boundary = re.split(BOUNDARY_END, after_boundary, maxsplit=1)[0]
    return in_boundary
