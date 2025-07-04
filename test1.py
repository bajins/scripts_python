#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import re

import requests as requests
from bs4 import BeautifulSoup

if __name__ == '__main1__':
    s = ["native-tls",
         "futures-util",
         "mio-named-pipes",
         "json-patch",
         "brotli",
         "kuchiki",
         "walkdir",
         "serde_with",
         "schannel",
         "tokio-macros",
         "futures-macro",
         "num-rational",
         "futures-io",
         "glob",
         "heck",
         "adler",
         "pin-utils",
         "tokio",
         "miniz_oxide",
         "tauri-utils",
         "pin-project-internal",
         "tracing-core",
         "indexmap",
         "raw-window-handle",
         "cc",
         "unicode-segmentation",
         "pin-project",
         "tracing",
         "flate2",
         "crypto-common",
         "block-buffer",
         "webview2-com-macros",
         "futures-channel",
         "futures-sink",
         "hashbrown",
         "httparse",
         "color_quant",
         "bytemuck",
         "image",
         "tokio-util",
         "digest",
         "png",
         "tracing-futures",
         "strum_macros",
         "crossbeam-channel",
         "serde_urlencoded",
         "toml",
         "instant",
         "wry",
         "tauri-runtime",
         "cpufeatures",
         "try-lock",
         "want",
         "sha2",
         "strum",
         "h2",
         "ico",
         "mime_guess",
         "http-body",
         "socket2",
         "quick-xml",
         "bstr",
         "base64",
         "rfd",
         "tauri-runtime-wry",
         "dunce",
         "httpdate",
         "http-range",
         "tower-service",
         "tauri-codegen",
         "globset",
         "filetime",
         "cargo_toml",
         "hyper",
         "winres",
         "tokio-tls",
         "tauri",
         "serialize-to-javascript-impl",
         "dirs-sys-next",
         "thread_local",
         "encode_unicode",
         "fastrand",
         "mime",
         "unicode-width",
         "console",
         "hyper-tls",
         "tempfile",
         "ignore",
         "tauri-winrt-notification",
         "webview2-com",
         "notify-rust",
         "serialize-to-javascript",
         "dirs-next",
         "tauri-macros",
         "tauri-build",
         "attohttpc",
         "tar",
         "os_info",
         "open",
         "os_pipe",
         "serde_repr",
         "shared_child",
         "winreg",
         "number_prefix",
         "state",
         "ipnet",
         "reqwest",
         "indicatif",
         "bincode",
         "download_rs",
         "tauri-plugin-window-state",
         "rustc_version",
         "tracing-attributes",
         "Compiling"]
    for i in s:
        r = requests.get(f"""https://docs.rs/releases/search?query={i}""")
        rs = BeautifulSoup(r.content)
        a = rs.select(".recent-releases-container > ul > li:nth-child(1) > a")
        r = requests.get(f"""https://docs.rs{a[0].attrs["href"]}""")
        # print(r.content)
        rs = BeautifulSoup(r.content, features="html.parser")
        # a = rs.find('a', text=re.compile(".*Repository.*", flags=re.DOTALL))
        a = rs.find(lambda tag: tag.name == "a" and "Repository" in tag.text)
        print(a.attrs["href"])

if __name__ == '__main__':
    s = "https://raw.fastgit.org/lifedever/bookmark/master/bookmark.json"
    r = requests.get(s)
    for i in json.loads(r.content)[0]["children"]:
        if "children" in i:
            for j in i["children"]:
                if "url" not in j and "children" in j:
                    for k in j["children"]:
                        print(k["title"], k["url"])
                else:
                    print(j["title"].encode('utf-8', 'replace').decode('utf-8'), j["url"])
        else:
            print(i["title"].encode('utf-8', 'replace').decode('utf-8'), i["url"])
