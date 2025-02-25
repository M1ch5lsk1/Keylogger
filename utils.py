def get_config_data(path_config: str) -> dict:
    with open(path_config, "r") as file:
        properties = {}
        file_data = file.readlines()
        for line in file_data:
            # deletes comments from lines if they exist
            if "#" in line:
                line = line[: line.index("#")]

            # extracts key and value from line
            key, value = line.strip().split("=")

            # removes whitespaces and quotes from values
            key, value = key.strip(), value.strip()
            value = value.replace('"', "")
            if not value:
                raise ValueError(f"Value for key '{key}' is empty")

            # checks if value could be converted to int
            if value.isdigit():
                value = int(value)

            properties[key.lower()] = value

        return properties
