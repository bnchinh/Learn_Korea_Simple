import pandas as pd
import random

# Mapping for Hán Hàn digits and units
digits = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
units = ['', '십', '백', '천']
big_units = ['', '만', '억', '조']

def korean_sino_number(n):
    if n == 0:
        return '영'
    result = ''
    str_n = str(n)
    length = len(str_n)
    group_count = (length + 3) // 4  # Group by 4 digits
    str_n = str_n.zfill(group_count * 4)
    for group_idx in range(group_count):
        group = str_n[group_idx*4:(group_idx+1)*4]
        group_read = ''
        for idx, digit_char in enumerate(group):
            digit = int(digit_char)
            if digit != 0:
                if digit == 1 and idx != 3:
                    group_read += units[3 - idx]
                else:
                    group_read += digits[digit] + units[3 - idx]
        if group_read:
            result += group_read + big_units[group_count - group_idx - 1]
    return result

def generate_sino_samples(n_sample, max_value=1000000):
    # Randomly choose unique numbers; avoid zero
    selected = random.sample(range(1, max_value + 1), n_sample)
    return pd.DataFrame(
        [{'Vietnamese': f"Số hán {n}", 'Korean': korean_sino_number(n)} for n in selected]
    )

def pick_random_words(vocab_path, numbers_path, n_vocab, n_numbers):
    vocab_df = pd.read_excel(vocab_path)
    numbers_df = pd.read_excel(numbers_path)
    half_n = n_numbers // 2

    # Sample vocab
    vocab_sample = vocab_df.sample(n=n_vocab, random_state=None)
    number_sample = numbers_df.sample(n=half_n, random_state=None)
    # Generate random sino numbers in memory
    sino_sample = generate_sino_samples(n_numbers - half_n)

    combined_df = pd.concat([vocab_sample, number_sample, sino_sample], ignore_index=True)
    return combined_df

# Example usage:
# combined_df = pick_random_words("vocab_modified.xlsx", "numbers.xlsx", 40, 10)
# print(combined_df)
