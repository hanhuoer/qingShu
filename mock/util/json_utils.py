def json_parse_to_equivalent(dict):
    result = ''
    for item in dict:
        result += item + '=' + dict[item] + ';'
    return result
