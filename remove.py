def remove_verfied(with_verfied):
    temp_list = []
    for i in with_verfied:
        if i == '\n':
            break
        else:
            temp_list.append(i)
    return str("".join(temp_list))
def remove_space(with_follow):
    temp_list = []
    for i in with_follow:
        if i == ' ':
            break
        else:
            temp_list.append(i)
    return int("".join(temp_list))

if __name__ == "__main__":
    st = remove_space("prajwal verified")
    print(st)
