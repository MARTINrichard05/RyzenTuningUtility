import json

params = {"tempEdit": False, "temp": 75,
                          "avgPEdit": False, "avgpower": 10,
                          "pkPEdit": False, "pkpower": 13,
          }

presetlist = {
    "default": {
        "mode" : "manual",
        "max_temp" : 75,
        "temp_enabled" : False,
        "max_avg_power" : 10,
        "avg_power_enabled" : False,
        "max_peak_power" : 13,
        "peak_power_enabled" : False,

    }
}
with open('../gui/presets.json', 'w') as fp:
    json.dump(presetlist, fp)