#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author : bajins https://www.bajins.com
# @File : content_type.py
# @Version: 1.0.0
# @Time : 2019/8/22 9:24
# @Project: windows-wallpaper-python
# @Package: 
# @Software: PyCharm

import mimetypes
import os


def get_content_type(ext):
    """
    根据文件后缀设置 content type
    :param ext: 后缀
    :return:
    """
    # 转换为小写
    ext = ext.lower

    if ext == ".aeliff":
        return "audio/aeliff"
    elif ext == ".anv":
        return "application/x-anv"
    elif ext == ".asa":
        return "text/asa"
    elif ext == ".asf":
        return "video/x-ms-asf"
    elif ext == ".asp":
        return "text/asp"
    elif ext == ".asx":
        return "video/x-ms-asf"
    elif ext == ".au":
        return "audio/basic"
    elif ext == ".avi":
        return "video/avi"
    elif ext == ".awf":
        return "application/vnd.adobe.workflow"
    elif ext == ".biz":
        return "text/xml"
    elif ext == ".bmp":
        return "application/x-bmp"
    elif ext == ".bot":
        return "application/x-bot"
    elif ext == ".c4t":
        return "application/x-c4t"
    elif ext == ".c90":
        return "application/x-c90"
    elif ext == ".cal":
        return "application/x-cals"
    elif ext == ".cat":
        return "application/vnd.ms-pki.seccat"
    elif ext == ".cdf":
        return "application/x-netcdf"
    elif ext == ".cdr":
        return "application/x-cdr"
    elif ext == ".cel":
        return "application/x-cel"
    elif ext == ".cer":
        return "application/x-x509-ca-cert"
    elif ext == ".cg4":
        return "application/x-g4"
    elif ext == ".cgm":
        return "application/x-cgm"
    elif ext == ".cit":
        return "application/x-cit"
    elif ext == ".class":
        return "java/*"
    elif ext == ".cml":
        return "text/xml"
    elif ext == ".cmp":
        return "application/x-cmp"
    elif ext == ".cmx":
        return "application/x-cmx"
    elif ext == ".cot":
        return "application/x-cot"
    elif ext == ".crl":
        return "application/pkix-crl"
    elif ext == ".crt":
        return "application/x-x509-ca-cert"
    elif ext == ".csi":
        return "application/x-csi"
    elif ext == ".css":
        return "text/css"
    elif ext == ".cut":
        return "application/x-cut"
    elif ext == ".dbf":
        return "application/x-dbf"
    elif ext == ".dbm":
        return "application/x-dbm"
    elif ext == ".dbx":
        return "application/x-dbx"
    elif ext == ".dcd":
        return "text/xml"
    elif ext == ".dcx":
        return "application/x-dcx"
    elif ext == ".der":
        return "application/x-x509-ca-cert"
    elif ext == ".dgn":
        return "application/x-dgn"
    elif ext == ".dib":
        return "application/x-dib"
    elif ext == ".dll":
        return "application/x-msdownload"
    elif ext == ".doc":
        return "application/msword"
    elif ext == ".dot":
        return "application/msword"
    elif ext == ".drw":
        return "application/x-drw"
    elif ext == ".dtd":
        return "text/xml"
    elif ext == ".dwf":
        return "application/x-dwf"
    elif ext == ".dwg":
        return "application/x-dwg"
    elif ext == ".dxb":
        return "application/x-dxb"
    elif ext == ".dxf":
        return "application/x-dxf"
    elif ext == ".edn":
        return "application/vnd.adobe.edn"
    elif ext == ".emf":
        return "application/x-emf"
    elif ext == ".eml":
        return "message/rfc822"
    elif ext == ".ent":
        return "text/xml"
    elif ext == ".epi":
        return "application/x-epi"
    elif ext == ".eps":
        return "application/postscript"
    elif ext == ".etd":
        return "application/x-ebx"
    elif ext == ".exe":
        return "application/x-msdownload"
    elif ext == ".fax":
        return "image/fax"
    elif ext == ".fdf":
        return "application/vnd.fdf"
    elif ext == ".felif":
        return "application/fractals"
    elif ext == ".fo":
        return "text/xml"
    elif ext == ".frm":
        return "application/x-frm"
    elif ext == ".g4":
        return "application/x-g4"
    elif ext == ".gbr":
        return "application/x-gbr"
    elif ext == ".gcd":
        return "application/x-gcd"
    elif ext == ".gelif":
        return "image/gelif"
    elif ext == ".gl2":
        return "application/x-gl2"
    elif ext == ".gp4":
        return "application/x-gp4"
    elif ext == ".hgl":
        return "application/x-hgl"
    elif ext == ".hmr":
        return "application/x-hmr"
    elif ext == ".hpg":
        return "application/x-hpgl"
    elif ext == ".hpl":
        return "application/x-hpl"
    elif ext == ".hqx":
        return "application/mac-binhex40"
    elif ext == ".hrf":
        return "application/x-hrf"
    elif ext == ".hta":
        return "application/hta"
    elif ext == ".htc":
        return "text/x-component"
    elif ext == ".htm":
        return "text/html"
    elif ext == ".html":
        return "text/html"
    elif ext == ".htt":
        return "text/webviewhtml"
    elif ext == ".htx":
        return "text/html"
    elif ext == ".icb":
        return "application/x-icb"
    elif ext == ".ico":
        return "image/x-icon"
    elif ext == ".eliff":
        return "application/x-eliff"
    elif ext == ".ig4":
        return "application/x-g4"
    elif ext == ".igs":
        return "application/x-igs"
    elif ext == ".iii":
        return "application/x-iphone"
    elif ext == ".img":
        return "application/x-img"
    elif ext == ".ins":
        return "application/x-internet-signup"
    elif ext == ".isp":
        return "application/x-internet-signup"
    elif ext == ".IVF":
        return "video/x-ivf"
    elif ext == ".java":
        return "java/*"
    elif ext == ".jfelif":
        return "image/jpeg"
    elif ext == ".jpe":
        return "image/jpeg"
    elif ext == ".jpeg":
        return "image/jpeg"
    elif ext == ".jpg":
        return "image/jpeg"
    elif ext == ".js":
        return "application/x-javascript"
    elif ext == ".jsp":
        return "text/html"
    elif ext == ".la1":
        return "audio/x-liquid-file"
    elif ext == ".lar":
        return "application/x-laplayer-reg"
    elif ext == ".latex":
        return "application/x-latex"
    elif ext == ".lavs":
        return "audio/x-liquid-secure"
    elif ext == ".lbm":
        return "application/x-lbm"
    elif ext == ".lmsff":
        return "audio/x-la-lms"
    elif ext == ".ls":
        return "application/x-javascript"
    elif ext == ".ltr":
        return "application/x-ltr"
    elif ext == ".m1v":
        return "video/x-mpeg"
    elif ext == ".m2v":
        return "video/x-mpeg"
    elif ext == ".m3u":
        return "audio/mpegurl"
    elif ext == ".m4e":
        return "video/mpeg4"
    elif ext == ".mac":
        return "application/x-mac"
    elif ext == ".man":
        return "application/x-troff-man"
    elif ext == ".math":
        return "text/xml"
    elif ext == ".mdb":
        return "application/x-mdb"
    elif ext == ".mfp":
        return "application/x-shockwave-flash"
    elif ext == ".mht":
        return "message/rfc822"
    elif ext == ".mhtml":
        return "message/rfc822"
    elif ext == ".mi":
        return "application/x-mi"
    elif ext == ".mid":
        return "audio/mid"
    elif ext == ".midi":
        return "audio/mid"
    elif ext == ".mil":
        return "application/x-mil"
    elif ext == ".mml":
        return "text/xml"
    elif ext == ".mnd":
        return "audio/x-musicnet-download"
    elif ext == ".mns":
        return "audio/x-musicnet-stream"
    elif ext == ".mocha":
        return "application/x-javascript"
    elif ext == ".movie":
        return "video/x-sgi-movie"
    elif ext == ".mp1":
        return "audio/mp1"
    elif ext == ".mp2":
        return "audio/mp2"
    elif ext == ".mp2v":
        return "video/mpeg"
    elif ext == ".mp3":
        return "audio/mp3"
    elif ext == ".mp4":
        return "video/mpeg4"
    elif ext == ".mpa":
        return "video/x-mpg"
    elif ext == ".mpd":
        return "application/vnd.ms-project"
    elif ext == ".mpe":
        return "video/x-mpeg"
    elif ext == ".mpeg":
        return "video/mpg"
    elif ext == ".mpg":
        return "video/mpg"
    elif ext == ".mpga":
        return "audio/rn-mpeg"
    elif ext == ".mpp":
        return "application/vnd.ms-project"
    elif ext == ".mps":
        return "video/x-mpeg"
    elif ext == ".mpt":
        return "application/vnd.ms-project"
    elif ext == ".mpv":
        return "video/mpg"
    elif ext == ".mpv2":
        return "video/mpeg"
    elif ext == ".mpw":
        return "application/vnd.ms-project"
    elif ext == ".mpx":
        return "application/vnd.ms-project"
    elif ext == ".mtx":
        return "text/xml"
    elif ext == ".mxp":
        return "application/x-mmxp"
    elif ext == ".net":
        return "image/pnetvue"
    elif ext == ".nrf":
        return "application/x-nrf"
    elif ext == ".nws":
        return "message/rfc822"
    elif ext == ".odc":
        return "text/x-ms-odc"
    elif ext == ".out":
        return "application/x-out"
    elif ext == ".p10":
        return "application/pkcs10"
    elif ext == ".p12":
        return "application/x-pkcs12"
    elif ext == ".p7b":
        return "application/x-pkcs7-certelificates"
    elif ext == ".p7c":
        return "application/pkcs7-mime"
    elif ext == ".p7m":
        return "application/pkcs7-mime"
    elif ext == ".p7r":
        return "application/x-pkcs7-certreqresp"
    elif ext == ".p7s":
        return "application/pkcs7-signature"
    elif ext == ".pc5":
        return "application/x-pc5"
    elif ext == ".pci":
        return "application/x-pci"
    elif ext == ".pcl":
        return "application/x-pcl"
    elif ext == ".pcx":
        return "application/x-pcx"
    elif ext == ".pdf":
        return "application/pdf"
    elif ext == ".pdx":
        return "application/vnd.adobe.pdx"
    elif ext == ".pfx":
        return "application/x-pkcs12"
    elif ext == ".pgl":
        return "application/x-pgl"
    elif ext == ".pic":
        return "application/x-pic"
    elif ext == ".pko":
        return "application/vnd.ms-pki.pko"
    elif ext == ".pl":
        return "application/x-perl"
    elif ext == ".plg":
        return "text/html"
    elif ext == ".pls":
        return "audio/scpls"
    elif ext == ".plt":
        return "application/x-plt"
    elif ext == ".png":
        return "image/png"
    elif ext == ".pot":
        return "application/vnd.ms-powerpoint"
    elif ext == ".ppa":
        return "application/vnd.ms-powerpoint"
    elif ext == ".ppm":
        return "application/x-ppm"
    elif ext == ".pps":
        return "application/vnd.ms-powerpoint"
    elif ext == ".ppt":
        return "application/x-ppt"
    elif ext == ".pr":
        return "application/x-pr"
    elif ext == ".prf":
        return "application/pics-rules"
    elif ext == ".prn":
        return "application/x-prn"
    elif ext == ".prt":
        return "application/x-prt"
    elif ext == ".ps":
        return "application/x-ps"
    elif ext == ".ptn":
        return "application/x-ptn"
    elif ext == ".pwz":
        return "application/vnd.ms-powerpoint"
    elif ext == ".r3t":
        return "text/vnd.rn-realtext3d"
    elif ext == ".ra":
        return "audio/vnd.rn-realaudio"
    elif ext == ".ram":
        return "audio/x-pn-realaudio"
    elif ext == ".ras":
        return "application/x-ras"
    elif ext == ".rat":
        return "application/rat-file"
    elif ext == ".rdf":
        return "text/xml"
    elif ext == ".rec":
        return "application/vnd.rn-recording"
    elif ext == ".red":
        return "application/x-red"
    elif ext == ".rgb":
        return "application/x-rgb"
    elif ext == ".rjs":
        return "application/vnd.rn-realsystem-rjs"
    elif ext == ".rjt":
        return "application/vnd.rn-realsystem-rjt"
    elif ext == ".rlc":
        return "application/x-rlc"
    elif ext == ".rle":
        return "application/x-rle"
    elif ext == ".rm":
        return "application/vnd.rn-realmedia"
    elif ext == ".rmf":
        return "application/vnd.adobe.rmf"
    elif ext == ".rmi":
        return "audio/mid"
    elif ext == ".rmj":
        return "application/vnd.rn-realsystem-rmj"
    elif ext == ".rmm":
        return "audio/x-pn-realaudio"
    elif ext == ".rmp":
        return "application/vnd.rn-rn_music_package"
    elif ext == ".rms":
        return "application/vnd.rn-realmedia-secure"
    elif ext == ".rmvb":
        return "application/vnd.rn-realmedia-vbr"
    elif ext == ".rmx":
        return "application/vnd.rn-realsystem-rmx"
    elif ext == ".rnx":
        return "application/vnd.rn-realplayer"
    elif ext == ".rp":
        return "image/vnd.rn-realpix"
    elif ext == ".rpm":
        return "audio/x-pn-realaudio-plugin"
    elif ext == ".rsml":
        return "application/vnd.rn-rsml"
    elif ext == ".rt":
        return "text/vnd.rn-realtext"
    elif ext == ".rtf":
        return "application/x-rtf"
    elif ext == ".rv":
        return "video/vnd.rn-realvideo"
    elif ext == ".sam":
        return "application/x-sam"
    elif ext == ".sat":
        return "application/x-sat"
    elif ext == ".sdp":
        return "application/sdp"
    elif ext == ".sdw":
        return "application/x-sdw"
    elif ext == ".sit":
        return "application/x-stuffit"
    elif ext == ".slb":
        return "application/x-slb"
    elif ext == ".sld":
        return "application/x-sld"
    elif ext == ".slk":
        return "drawing/x-slk"
    elif ext == ".smi":
        return "application/smil"
    elif ext == ".smil":
        return "application/smil"
    elif ext == ".smk":
        return "application/x-smk"
    elif ext == ".snd":
        return "audio/basic"
    elif ext == ".sol":
        return "text/plain"
    elif ext == ".sor":
        return "text/plain"
    elif ext == ".spc":
        return "application/x-pkcs7-certelificates"
    elif ext == ".spl":
        return "application/futuresplash"
    elif ext == ".spp":
        return "text/xml"
    elif ext == ".ssm":
        return "application/streamingmedia"
    elif ext == ".sst":
        return "application/vnd.ms-pki.certstore"
    elif ext == ".stl":
        return "application/vnd.ms-pki.stl"
    elif ext == ".stm":
        return "text/html"
    elif ext == ".sty":
        return "application/x-sty"
    elif ext == ".svg":
        return "text/xml"
    elif ext == ".swf":
        return "application/x-shockwave-flash"
    elif ext == ".tdf":
        return "application/x-tdf"
    elif ext == ".tg4":
        return "application/x-tg4"
    elif ext == ".tga":
        return "application/x-tga"
    elif ext == ".telif":
        return "image/teliff"
    elif ext == ".teliff":
        return "image/teliff"
    elif ext == ".tld":
        return "text/xml"
    elif ext == ".top":
        return "drawing/x-top"
    elif ext == ".torrent":
        return "application/x-bittorrent"
    elif ext == ".tsd":
        return "text/xml"
    elif ext == ".txt":
        return "text/plain"
    elif ext == ".uin":
        return "application/x-icq"
    elif ext == ".uls":
        return "text/iuls"
    elif ext == ".vcf":
        return "text/x-vcard"
    elif ext == ".vda":
        return "application/x-vda"
    elif ext == ".vdx":
        return "application/vnd.visio"
    elif ext == ".vml":
        return "text/xml"
    elif ext == ".vpg":
        return "application/x-vpeg005"
    elif ext == ".vsd":
        return "application/x-vsd"
    elif ext == ".vss":
        return "application/vnd.visio"
    elif ext == ".vst":
        return "application/x-vst"
    elif ext == ".vsw":
        return "application/vnd.visio"
    elif ext == ".vsx":
        return "application/vnd.visio"
    elif ext == ".vtx":
        return "application/vnd.visio"
    elif ext == ".vxml":
        return "text/xml"
    elif ext == ".wav":
        return "audio/wav"
    elif ext == ".wax":
        return "audio/x-ms-wax"
    elif ext == ".wb1":
        return "application/x-wb1"
    elif ext == ".wb2":
        return "application/x-wb2"
    elif ext == ".wb3":
        return "application/x-wb3"
    elif ext == ".wbmp":
        return "image/vnd.wap.wbmp"
    elif ext == ".wiz":
        return "application/msword"
    elif ext == ".wk3":
        return "application/x-wk3"
    elif ext == ".wk4":
        return "application/x-wk4"
    elif ext == ".wkq":
        return "application/x-wkq"
    elif ext == ".wks":
        return "application/x-wks"
    elif ext == ".wm":
        return "video/x-ms-wm"
    elif ext == ".wma":
        return "audio/x-ms-wma"
    elif ext == ".wmd":
        return "application/x-ms-wmd"
    elif ext == ".wmf":
        return "application/x-wmf"
    elif ext == ".wml":
        return "text/vnd.wap.wml"
    elif ext == ".wmv":
        return "video/x-ms-wmv"
    elif ext == ".wmx":
        return "video/x-ms-wmx"
    elif ext == ".wmz":
        return "application/x-ms-wmz"
    elif ext == ".wp6":
        return "application/x-wp6"
    elif ext == ".wpd":
        return "application/x-wpd"
    elif ext == ".wpg":
        return "application/x-wpg"
    elif ext == ".wpl":
        return "application/vnd.ms-wpl"
    elif ext == ".wq1":
        return "application/x-wq1"
    elif ext == ".wr1":
        return "application/x-wr1"
    elif ext == ".wri":
        return "application/x-wri"
    elif ext == ".wrk":
        return "application/x-wrk"
    elif ext == ".ws":
        return "application/x-ws"
    elif ext == ".ws2":
        return "application/x-ws"
    elif ext == ".wsc":
        return "text/scriptlet"
    elif ext == ".wsdl":
        return "text/xml"
    elif ext == ".wvx":
        return "video/x-ms-wvx"
    elif ext == ".xdp":
        return "application/vnd.adobe.xdp"
    elif ext == ".xdr":
        return "text/xml"
    elif ext == ".xfd":
        return "application/vnd.adobe.xfd"
    elif ext == ".xfdf":
        return "application/vnd.adobe.xfdf"
    elif ext == ".xhtml":
        return "text/html"
    elif ext == ".xls":
        return "application/x-xls"
    elif ext == ".xlw":
        return "application/x-xlw"
    elif ext == ".xml":
        return "text/xml"
    elif ext == ".xpl":
        return "audio/scpls"
    elif ext == ".xq":
        return "text/xml"
    elif ext == ".xql":
        return "text/xml"
    elif ext == ".xquery":
        return "text/xml"
    elif ext == ".xsd":
        return "text/xml"
    elif ext == ".xsl":
        return "text/xml"
    elif ext == ".xslt":
        return "text/xml"
    elif ext == ".xwd":
        return "application/x-xwd"
    elif ext == ".x_b":
        return "application/x-x_b"
    elif ext == ".x_t":
        return "application/x-x_t"
    else:
        return "application/octet-stream"


def judge_type(file):
    """
    判断类型
    :param file: 文件
    :return:
    """
    suffix = os.path.splitext(file)[-1]
    return get_content_type(suffix)


def get_mime_type(file_path):
    """
    根据系统API获取Content-Type，没有查询到会返回None
    :param file_path:文件地址
    :return:
    """
    return mimetypes.guess_type(file_path)[0]
