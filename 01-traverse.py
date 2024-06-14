# Load the content of the files
with open('./hanshu.txt', 'r', encoding='utf-8') as file:
    hanshu_content = file.read()

# A short snippet from 'shiji' to compare.
shiji_content = "高祖沛豐邑中陽里人也姓劉氏"

# Implementing a method to find common substrings
def find_common_substrings(s1, s2, min_length=4):
    """
    Find common substrings between s1 and s2 with a minimum length of min_length.
    Returns a list of tuples containing (substring, start_index_s1, end_index_s1, start_index_s2, end_index_s2).
    """
    common_substrings = []
    len_s1 = len(s1)
    
    for i in range(len_s1):
        for j in range(i + min_length, len_s1 + 1):
            substring = s1[i:j]
            if substring in s2:
                start_index_s2 = s2.index(substring)
                common_substrings.append((substring, i, j, start_index_s2, start_index_s2 + (j - i)))
    
    return common_substrings

# Finding common substrings between the provided contents
common_substrings = find_common_substrings(shiji_content, hanshu_content)
common_substrings