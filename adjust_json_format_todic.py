import json

path = "/media/bassel/Career/toronto_broadcasting/toronto_2/0/saved_state_test/state_0.65_360_150_250_10_1_nede_0_discont_prob_.json";

for i in range(1, 3001):
    p = path.replace("_.json", "_"+str(i)+".json")

    with open(p) as f:
        data = json.load(f)

    avs_dict = {}

    for av in data["avs"]:
        avs_dict[av["vehicle_id"]] = av

    data["avs"] = avs_dict

    navs_dict = {}

    for nav in data["navs"]:
        navs_dict[nav["vehicle_id"]] = nav

    data["navs"] = navs_dict

    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
