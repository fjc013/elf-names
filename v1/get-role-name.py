from nova_elf_names import generate_seasonal_names

names = generate_seasonal_names(
    user_input="Jane Doe",
    role_hint="humorous names of Santa's helpers",
    count=10
)
print(names)
