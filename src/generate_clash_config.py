#!/usr/bin/env python3
# coding: utf-8
import yaml
from yaml import CSafeLoader as Loader, CSafeDumper as Dumper
from pathlib import Path
from shutil import copyfile
import typer
import io


def create_proxy_providers(custom_data, black_list):
    obj = {}
    for i, v in custom_data.items():
        if i in black_list:
            obj[i] = {}
        else:
            obj[i] = v
    return obj


def replace_url(url, convert=""):
    """
    convert: http://127.0.0.1:25500/sub?target=clash&url=
    """
    return convert + url


def create_provider(name, obj, interval1=3600, interval2=300, convert=""):
    return {
        "type": "http",
        "path": f"./profiles/proxies/{name}.yaml",
        "url": replace_url(obj["url"], convert=convert),
        "filter": obj["filter"] if "filter" in obj else "",
        "interval": interval1,
        "health-check": {
            "enable": True,
            "url": "http://www.gstatic.com/generate_204",
            "interval": interval2,
        },
    }


def add_group_proxies(custom_data, enable_match=True):
    # enable_match开启匹配前缀功能
    # 匹配前缀,DOG-gatern项,匹配D-default,O-other,G-Game三个组,最好用大写,包含匹配(in)
    # 匹配子前缀,R-uk-region,匹配RG-uk-gatern_s,RG-uk-mojie_s,匹配的是[1:-1]中间的uk,相等匹配(==)
    res = []
    for group in custom_data["proxy-groups"]:
        res.append(group)
        group["proxies"] = []
        for i, v in custom_data["proxy-providers"].items():
            if not enable_match:
                group["proxies"].append(f"{i}_s")
                continue
            if group["name"].split("-")[0] in i.split("-")[0]:
                if len(group["name"].split("-")) <= 2:
                    group["proxies"].append(f"{i}_s")
                elif "-".join(group["name"].split("-")[1:-1]) == "-".join(
                    i.split("-")[1:-1]
                ):
                    group["proxies"].append(f"{i}_s")
        group["proxies"] = [*group["proxies"], "DIRECT", "REJECT"]
    return res


def create_proxy_groups(name, interval=300):
    return [
        {
            "name": f"{name}_s",
            "type": "select",
            "interval": interval,
            "url": "http://www.gstatic.com/generate_204",
            "proxies": [f"{name}_a"],
            "use": [name],
        },
        {
            "name": f"{name}_a",
            "type": "url-test",
            "interval": interval,
            "url": "http://www.gstatic.com/generate_204",
            "use": [name],
        },
    ]


def build_config(custom_data, convert=""):
    new_obj = create_proxy_providers(custom_data, ["proxy-providers", "proxy-groups"])

    for i, v in custom_data["proxy-providers"].items():
        new_provider = create_provider(i, v, convert=convert)
        new_obj["proxy-providers"][i] = new_provider

    new_obj["proxy-groups"] = add_group_proxies(custom_data)

    for i, v in custom_data["proxy-providers"].items():
        new_group = create_proxy_groups(i)
        new_obj["proxy-groups"] = [*new_obj["proxy-groups"], *new_group]
    return new_obj


def load_yaml_str(text):
    return yaml.safe_load(text)


def dump_yaml_str(data):
    yaml_s = io.StringIO()
    yaml.safe_dump(
        data, yaml_s, allow_unicode=True, default_flow_style=False, sort_keys=False
    )
    return yaml_s.getvalue()


def load_yaml(path):
    with open(path, "r", encoding="utf8") as f:
        custom_data = yaml.load(f, Loader=Loader)
        return custom_data


def dump_yaml(new_obj, outPath):
    with open(outPath, "w", encoding="utf8") as f:
        yaml.dump(new_obj, f, allow_unicode=True, Dumper=Dumper)
    return outPath


def build_config_local(path="src/template.yaml", outPath="src/config.yaml", convert=""):
    custom_data = load_yaml(path)

    new_obj = build_config(custom_data, convert=convert)

    dump_yaml(new_obj, outPath)
    print("generate config success", outPath)
    return new_obj


if __name__ == "__main__":
    app = typer.Typer(pretty_exceptions_show_locals=False)
    app.command(help="also bcl")(build_config_local)
    app.command("bcl", hidden=True)(build_config_local)
    app()
