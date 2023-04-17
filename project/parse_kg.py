import json

def process_entity_attribute_list(multiline_attributes_list: list):
    ent_id = None
    for attribute_list in multiline_attributes_list:
        for attribute in attribute_list:
            print(attribute)



def main():
    fname = "input/kg.jsonl"
    g = []
    with open(fname, 'rt') as f:
        current_ent = []
        for line in f:
            line = line.rstrip()
            line = json.loads(line)
            current_ent.append(line["data"])
            if line["next"] is not None:
                continue
            else:
                process_entity_attribute_list(current_ent)
                print()
                current_ent = []

if __name__ == "__main__":
    main()