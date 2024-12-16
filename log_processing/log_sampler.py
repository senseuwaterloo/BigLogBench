#1
import os
import hashlib
import random
from utils import timeit


def string_to_seed(s):
    # Convert string to a consistent integer using a hash function
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


@timeit
def log_sampler(log_path: str, output_log_path: str, seed = 'gundam', num_sample = 20000, encoding = 'ISO-8859-1', overwrite=False):

    if not os.path.isdir(os.path.dirname(output_log_path)):
        os.makedirs(os.path.dirname(output_log_path))

    if (not os.path.isfile(output_log_path)) or (os.path.isfile(output_log_path) and overwrite):
        loglines = open(log_path, encoding=encoding).readlines()
        n_lines = len(loglines)
        random.seed(string_to_seed(seed))
        sample_file_writer = open(output_log_path, 'w')

        sample_lines = []
        if n_lines > num_sample:
            step = int(n_lines / num_sample)
            n = 0
            while n < num_sample:
                loc = random.randint(0, step-1)
                sample_lines.append(loglines[loc + (n * step)])
                n = n + 1
        else:
            sample_lines += loglines

        sample_file_writer.writelines(sample_lines)
        sample_file_writer.close()
    else:
        print(f'Skip generating sample as it already exists: {output_log_path}')


if __name__ == "__main__":
    log_sampler()