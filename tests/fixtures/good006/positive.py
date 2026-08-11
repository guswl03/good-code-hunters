from yaml import safe_load as load_yaml

document = "safe: true"
data = load_yaml(document)
