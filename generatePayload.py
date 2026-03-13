import math

def generate_lorem_bits_txt(filename, target_bits):
    lorem = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
        "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in "
        "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
        "deserunt mollit anim id est laborum.\n"
    )

    target_bytes = math.ceil(target_bits / 8)
    content = ""

    while len(content.encode("utf-8")) < target_bytes:
        content += lorem

    content_bytes = content.encode("utf-8")[:target_bytes]

    with open(filename, "wb") as f:
        f.write(content_bytes)

    actual_bits = len(content_bytes) * 8

    print(f"File '{filename}' generated")
    print(f"Target bits : {target_bits}")
    print(f"Actual bits : {actual_bits}")

if __name__ == "__main__":
    for i in range (1, 100):
        generate_lorem_bits_txt(f"payload/{1000 * i}bits.txt", i * 1000)
    # generate_lorem_bits_txt(f"payload/1bits.txt", 1)
