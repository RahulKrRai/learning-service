import pandas as pd
import os
from datetime import datetime, timedelta

# Example: You can have multiple pairs of location and timestamp columns
column_map = {"Port of load": "Planned Load Date",
              "Port of discharge": "Planned Arrival Date",
              "Gate-Out Empty location": "Gate-Out Empty ts",
              "Gate-In Full location": "Gate-In Full ts",
              "Vessel Load location": "Vessel Load ts",
              "Vessel Depart location": "Vessel Depart ts",
              "Vessel Arrive location": "Vessel Arrive ts",
              "Vessel Discharge location": "Vessel Discharge ts",
              "Gate-Out Full location": "Gate-Out Full ts",
              "Gate-In Empty location": "Gate-In Empty ts"}
locode_map  = {
  "MYNTL": "+08",
  "SAJBI": "+03",
  "USSEA": "-08",
  "QAUMS": "+03",
  "USMOB": "-06",
  "USMIA": "-05",
  "USPEF": "-06",
  "IEDUB": "+00",
  "ITGOA": "+01",
  "GEPTI": "+04",
  "CNQZJ": "+08",
  "USEWR": "-05",
  "LYMRA": "+02",
  "MRNKC": "+00",
  "PLSZZ": "+01",
  "PRSJU": "-04",
  "REPDG": "+04",
  "JPTAK": "+09",
  "DZGHZ": "+01",
  "USTPA": "-05",
  "NZLYT": "+12",
  "THSGK": "+07",
  "SYLTK": "+02",
  "PFPPT": "-10",
  "VELAG": "-04",
  "DJJIB": "+03",
  "LYBEN": "+02",
  "IQUQR": "+03",
  "IDPWG": "+07",
  "AUFRE": "+10",
  "DKAAR": "+01",
  "LTKLJ": "+02",
  "MYBKI": "+08",
  "YEADE": "+03",
  "ITNAP": "+01",
  "GYGEO": "-04",
  "NGAPP": "+01",
  "US8OT": "-05",
  "FRFOS": "+01",
  "CZXUY": "+01",
  "CASUY": "-03",
  "THLKR": "+07",
  "CNHIN": "+08",
  "AMEVN": "+04",
  "DEGRB": "+01",
  "CLSCL": "-04",
  "DEBER": "+01",
  "CLCAS": "-04",
  "INVPI": "+01",
  "USNBJ": "-05",
  "INSAA": "+05:30",
  "MXMEX": "-06",
  "ESCAR": "+01",
  "QAHMD": "+03",
  "CNQZL": "+08",
  "CZMLK": "+01",
  "IESWO": "+00",
  "USGXX": "-05",
    "FRMRS": "+01",
    "CUMAR": "-05",
    "PAMIT": "-05",
    "USRIC": "-05",
    "CNANJ": "+08",
    "CNNGB": "+08",
    "Ningbo": "+08",
    "NLRTM": "+02",
    "Rotterdam": "+02",
    "CNXIS": "+08",
    "Xiaoshan": "+08",
    "NLBON": "+02",
    "Born": "+02",
    "PKKHI": "+05",
    "Karachi": "+05",
    "PKBQM": "+05",
    "Port": "+05",
    "CNSHA": "+08",
    "Shanghai": "+08",
    "NLMOE": "+02",
    "Moerdijk": "+02",
    "ESBCN": "+02",
    "Barcelona": "+02",
    "CNYTN": "+08",
    "Yantian": "+08",
    "NLOOS": "+02",
    "Oosterhout": "+02",
    "SIKOP": "+02",
    "Koper": "+02",
    "PKLHE": "+05",
    "Lahore": "+05",
    "ATWER": "+02",
    "Werndorf": "+02",
    "NLVEN": "+02",
    "Venlo": "+02",
    "CNZJG": "+08",
    "Zhangjiagang": "+08",
    "ATGRZ": "+02",
    "Graz": "+02",
    "CNMAW": "+08",
    "Mawei": "+08",
    "CNXMN": "+08",
    "Xiamen": "+08",
    "VNVUT": "+07",
    "Vung": "+07",
    "VNSGN": "+07",
    "Ho": "+07",
    "INMUN": "+05",
    "Mundra": "+05",
    "INLUH": "+05",
    "Ludhiana": "+05",
    "THLCH": "+07",
    "Laem": "+07",
    "KHKOS": "+07",
    "Kampong": "+07",
    "KHPNH": "+07",
    "Phnom": "+07",
    "CNTXG": "+08",
    "Tianjin": "+08",
    "INNSA": "+05",
    "Nhava": "+05",
    "INNMB": "+05",
    "Navi": "+05",
    "PKLYP": "+05",
    "Faisalabad": "+05",
    "CNHAZ": "+08",
    "Hangzhou": "+08",
    "CNSZH": "+08",
    "Suzhou": "+08",
    "INTUT": "+05",
    "Tuticorin": "+05",
    "INSON": "+05",
    "Sonipat": "+05",
    "VNHPH": "+07",
    "Haiphong": "+07",
    "VNBDU": "+07",
    "Binh": "+07",
    "IDJKT": "+07",
    "Jakarta": "+07",
    "CNTAO": "+08",
    "Qingdao": "+08",
    "CNNJG": "+08",
    "Nanjing": "+08",
    "CNFZH": "+08",
    "Fuzhou": "+08",
    "CNFOC": "+08",
    "EGDAM": "+03",
    "Dumyat": "+03",
    "EGEDK": "+03",
    "El": "+03",
    "CNZSN": "+08",
    "Zhongshan": "+08",
    "CNHGH": "+08",
    "CNBIJ": "+08",
    "Beijiao": "+08",
    "CNSHK": "+08",
    "Shekou": "+08",
    "CNNSA": "+08",
    "Nansha": "+08",
    "TRALI": "+03",
    "Aliaga": "+03",
    "TRIZM": "+03",
    "Izmir": "+03",
    "BDCGP": "+06",
    "Chattogram": "+06",
    "INDWN": "+05",
    "Samalkha": "+05",
    "LKCMB": "+05",
    "Colombo": "+05",
    "LKBIY": "+05",
    "Biyagama": "+05",
    "CNTAC": "+08",
    "Taicang": "+08",
    "INCOK": "+05",
    "Cochin": "+05",
    "CNZPU": "+08",
    "Zhapu": "+08",
    "CNWZO": "+08",
    "Wenzhou": "+08",
    "USHOU": "-05",
    "Houston": "-05",
    "BEANR": "+02",
    "Antwerpen": "+02",
    "CNWEN": "+08",
    "Wenling": "+08",
    "DESCW": "+02",
    "Schweinfurt": "+02",
    "INPVL": "+05",
    "Panvel": "+05",
    "CNYIU": "+08",
    "Yiwu": "+08",
    "CNJIU": "+08",
    "Jiujiang": "+08",
    "VNBHA": "+07",
    "Bien": "+07",
    "CNDLC": "+08",
    "Dalian": "+08",
    "LKWLL": "+05",
    "Welisara": "+05",
    "CNNTG": "+08",
    "Nantong": "+08",
    "CNJAX": "+08",
    "Jiaxing": "+08",
    "INDRI": "+05",
    "Dadri": "+05",
    "DEWVN": "+02",
    "Wilhelmshaven": "+02",
    "MXZLO": "-06",
    "Manzanillo": "-06",
    "ARDKS": "-06",
    "Dock": "-06",
    "NZPOE": "+12",
    "DERGM": "+02",
    "Nuremberg": "+02",
    "INBOM": "+05",
    "Mumbai": "+05",
    "TRMER": "+03",
    "Mersin": "+03",
    "PKQCT": "+05",
    "DENUE": "+02",
    "Nurnberg": "+02",
    "CNJMN": "+08",
    "Jiangmen": "+08",
    "DEHAM": "+02",
    "Hamburg": "+02",
    "ITCTA": "+02",
    "Catania": "+02",
    "CNDMY": "+08",
    "Damaiyu": "+08",
    "CNHME": "+08",
    "Haimen": "+08",
    "TRGZT": "+03",
    "Gaziantep": "+03",
    "CNHNG": "+08",
    "Henggang": "+08",
    "NOLAR": "+02",
    "Larvik": "+02",
    "PKSKT": "+05",
    "Sialkot": "+05",
    "NLBOT": "+02",
    "Botlek": "+02",
    "MXESE": "-07",
    "Ensenada": "-07",
    "CNHZH": "+08",
    "Huzhou": "+08",
    "BRSSZ": "-03",
    "Santos": "-03",
    "CNDFG": "+08",
    "Dafeng": "+08",
    "INDEL": "+05",
    "Delhi": "+05",
    "NLAPN": "+02",
    "Alphen": "+02",
    "USOJM": "+02",
    "Home": "+02",
    "INICD": "+05",
    "New": "+05",
    "NLGRA": "+02",
    "s-Gravendeel": "+02",
    "VNDNA": "+07",
    "Dong": "+07",
    "UAILK": "+03",
    "Chornomorsk": "+03",
    "AESHJ": "+04",
    "Sharjah": "+04",
    "UAODS": "+03",
    "Odesa": "+03",
    "CNTAZ": "+08",
    "Taizhou": "+08",
    "DEDUI": "+02",
    "Duisburg": "+02",
    "CNYZH": "+08",
    "Yangzhou": "+08",
    "IDBDJ": "+08",
    "Banjarmasin": "+08",
    "INHAL": "+05",
    "Haldia": "+05",
    "DEWRZ": "+02",
    "Waren": "+02",
    "Rajula": "+05",
    "CNZH": "+08",
    "GBLGP": "+00",
    "AUSYD": "+10",
    "INRJU": "+05",
    "AAAAA": "+00",
    "TRGEM": "+03",
    "KRPUS": "+09",
    "CNSWA": "+08",
    "ZZZZZ": "+00",
    "USLAX": "-07",
    "ARBUE": "-03",
    "BRIOA": "-03",
    "ILASH": "+03",
    "DEBRV": "+01",
    "CNCZX": "+08",
    "MYTPP": "+08",
    "OMSLL": "+04",
    "SGSIN": "+08",
    "MATNG": "+01",
    "EGPSE": "+02",
    "ESALG": "+02",
    "MAPTM": "+01",
    "HKHKG": "+08",
    "ESVLC": "+02",
    "COBUN": "-05",
    "EGPSD": "+02",
    "EGALY": "+02",
    "MYPKG": "+08",
    "ITGIT": "+01",
    "PTSIE": "+00",
    "INTRV": "+05",
    "EGAKI": "+02",
    "TRTEK": "+03",
    "MTMLA": "+02",
    "AEJEA": "+04",
    "MTMAR": "+02",
    "TRISK": "+03",
    "MXVER": "+01",
    "INHZR": "+01",
    "EGSOK": "+01",
    "BRPNG": "+01",
    "DZALG": "+01",
    "DZORN": "+01",
    "CAMTR": "+01",
    "USORF": "+01",
    "CLSAI": "+01",
    "TRIZT": "+01",
    "CLVAP": "+01",
    "nan": "+01",
    "INKNU": "+01",
    "DEMUC": "+01",
    "DELUX": "+01",
    "USCRB": "+01",
    "CATOR": "+01",
    "USCHI": "+01",
    "VNCLI": "+07",
    "TWKHH": "+08",
    "CNNKG": "+08",
    "FIHEL": "+03",
    "TRIST": "+03",
    "SAJED": "+03",
    "INENR": "+05:30",
    "ITSPE": "+02",
    "USNYC": "-04",
    "USBAL": "-04",
    "GQBSG": "+01",
    "JPUKB": "+09",
    "TRGEB": "+03",
    "AERKT": "+03",
    "CASJB": "+08",
    "TZDAR": "+03",
    "PECLL": "-05",
    "MXATM": "-05",
    "CAHAL": "-07",
    "PHMNL": "+08",
    "JPYOK": "+09",
    "JPTYO": "+09",
    "ECGYE": "-05",
    "USSAV": "-04",
    "CLARI": "-04",
    "GTIZ4": "-05",
    "MACAS": "-05",
    "KEMBA": "+03",
    "JOAQJ": "+03",
    "SNDKR": "+04",
    "INCCU": "+05:30",
    "ZAPLZ": "+01",
    "PLGDN": "+02",
    "SAKAC": "+03",
    "GHTEM": "+02",
    "INQRP": "+05:30",
    "NLAPH": "+02",
    "CNPNU": "+08",
    "INPNI": "+05:30",
    "CNSRS": "+08",
    "INGNO": "+05:30",
    "CNTZU": "+08",
    "INSWA": "+05:30",
    "FRSXB": "+02",
    "INMAA": "+05:30",
    "USLUI": "-07",
    "OMSOH": "+04",
    "AEAUH": "+04",
    "GBFXT": "+01",
    "CNDCB": "+08",
    "CNHUA": "+08",
    "USLGB": "-07",
    "GBSOU": "+01",
    "CNZNG": "+08",
    "CNZHA": "+08",
    "CAVAN": "-04",
    "CHFKD": "+01",
    "DECGN": "+02",
    "USMSP": "-07",
    "DEBON": "+02",
    "MYBGR": "+08",
    "NLVLA": "+02",
    "BEANB": "+02",
    "HUBUD": "+08",
    "JOAMM": "+03",
    "FRLEH": "+02",
    "PACTB": "-03",
    "MYWSP": "+08",
    "CACAL": "-05",
    "AUMEL": "+10",
    "NOOSL": "+01",
    "DZBJA": "+01",
    "CNSXG": "+08",
    "INBAC": "+05:30",
    "KRUSN": "+09",
    "ITRAN": "+01",
  "BEZEE": "+01",
  "BELGG": "+01",
  "BEMEH": "+01",
  "NLRTM": "+01",
  "NLTLB": "+01",
  "NLMEP": "+01",
  "NLOST": "+01",
  "NLDOR": "+01",
  "DEMHG": "+01",
  "ATENA": "+01",
  "CHBSL": "+01",
  "HRRJK": "+01",
  "GRPIR": "+02",
  "ITSAL": "+01",
  "ITTRS": "+01",
  "QADOH": "+03",
  "SADMM": "+03",
  "LBBEY": "+02",
  "INBLR": "+05:30",
  "INAMD": "+05:30",
  "INPAP": "+05:30",
  "CNHZS": "+08",
  "CNTAG": "+08",
  "VNDAD": "+07",
  "VNUIH": "+07",
  "IDSRG": "+07",
  "BRRIO": "-03",
  "COCTG": "-05",
  "PABLB": "-05",
  "MXLZC": "-06",
  "USDET": "-05",
  "USCHS": "-05",
  "NGTIN": "+01",
  "MUPLU": "+04",
  "JPOSA": "+09",
  "JMKIN": "-05",
  "DOCAU": "-04",
  "DEKEH": "+01",
  "ESHSP": "+01",
    "BHBAH": "+03",
    "FRFEN": "+01",
"NLWAL": "+01",
"USMEM": "-06",
"JPNGO": "+09"
}

downloads_path = os.path.expanduser("~/Downloads/ocean-2025-07-14-2026-04-30.csv")
sheet_name = 'sheet1'
# Final result map
keys_map = [("PORT_OF_LOAD", "PLANNED_DEPARTURE_DATE"),
("PORT_OF_DISCHARGE", "PLANNED_ARRIVAL_DATE"),
("GATE_OUT_EMPTY_PLACE", "GATE_OUT_EMPTY_TS"),
("LOAD_GATE_IN_FULL_PLACE", "LOAD_GATE_IN_FULL_TS"),
("VESSEL_LOAD_PLACE", "VESSEL_LOAD_TS"),
("VESSEL_DEPART_PLACE", "VESSEL_DEPART_TS"),
("VESSEL_ARRIVE_PLACE", "VESSEL_ARRIVE_TS"),
("VESSEL_DISCHARGE_PLACE", "VESSEL_DISCHARGE_TS"),
("DISCHARGE_GATE_OUT_FULL_PLACE", "DISCHARGE_GATE_OUT_FULL_TS"),
("GATE_IN_EMPTY_PLACE", "GATE_IN_EMPTY_TS"),
("FIRST_TRANSSHIPMENT_ARRIVE_PLACE", "FIRST_TRANSSHIPMENT_ARRIVE_TS"),
("FIRST_TRANSSHIPMENT_UNLOAD_PLACE", "FIRST_TRANSSHIPMENT_UNLOAD_TS"),
("FIRST_TRANSSHIPMENT_LOAD_PLACE", "FIRST_TRANSSHIPMENT_LOAD_TS"),
("FIRST_TRANSSHIPMENT_DEPART_PLACE", "FIRST_TRANSSHIPMENT_DEPART_TS"),
("LAST_TRANSSHIPMENT_ARRIVE_PLACE", "LAST_TRANSSHIPMENT_ARRIVE_TS"),
("LAST_TRANSSHIPMENT_UNLOAD_PLACE", "LAST_TRANSSHIPMENT_UNLOAD_TS"),
("LAST_TRANSSHIPMENT_LOAD_PLACE", "LAST_TRANSSHIPMENT_LOAD_TS"),
("LAST_TRANSSHIPMENT_DEPART_PLACE", "LAST_TRANSSHIPMENT_DEPART_TS"),
("ORIGIN_GATE_OUT_FULL_PLACE", "ORIGIN_GATE_OUT_FULL_TS"),
("ORIGIN_GATE_IN_FULL_PLACE", "ORIGIN_GATE_IN_FULL_TS"),
("DESTINATION_ARRIVE_PLACE", "DESTINATION_ARRIVE_TS"),
("PORT_OF_DISCHARGE", "LATEST_SHIPPEO_DISCHARGE_ETA"),
("PORT_OF_DISCHARGE", "LATEST_CARRIER_DISCHARGE_ETA"),
("PORT_OF_DISCHARGE", "LATEST_CARRIER_DESTINATION_ETA_TS"),
("ORIGIN_LOAD_PLACE", "ORIGIN_LOAD_TS"),
("ORIGIN_DEPART_PLACE", "ORIGIN_DEPART_TS"),
("PORT_OF_LOAD", "LATEST_CARRIER_LOADING_ETD"),
("PORT_OF_LOAD", "LATEST_SHIPPEO_LOADING_ETD"),
]
location_timezone_map = {}
# df = pd.read_excel(downloads_path,skiprows=0)
# xls = pd.ExcelFile(downloads_path)
df = pd.read_csv(downloads_path, low_memory=False)
df["ORDER_CREATION_DATE"] = pd.to_datetime(
    df["ORDER_CREATION_DATE"],
    errors="coerce"
)
# df = (
#     df
#     .sort_values("ORDER_CREATION_DATE", ascending=False)
#     .drop_duplicates(subset=["CONTAINER_REFERENCE"], keep="first")
#     .reset_index(drop=True)
# )

# df = df[~df["PORT_OF_LOAD"].isin(["ESBCN", "MAPTM", "NLRTM", "NLMOE", "SIKOP", "BEANR", "DEBRV", "DEHAM", "DEWHV", "DEWVN", "AESHJ"])]
df = df[~df["CURRENT_STATUS"].isin(["CANCELLED", "NOT_TRACKABLE_SCAC_NOT_SUPPORTED", "NOT_TRACKABLE_CONTAINER_NOT_SUPPORTED_BY_OCEAN_CARRIER", "ORDER_NOT_TRACKABLE"])]
# container_ids = ["TAWU4006127"]
# df = df[df["CONTAINER_REFERENCE"].isin(container_ids)]

df1 = df[df["CURRENT_STATUS"] == "COMPLETED"].copy()
df2 = df[df["CURRENT_STATUS"] != "COMPLETED"].copy()
# print(xls.sheet_names)
missed_locode = {}


def split_with_padding(value):
    # Replace 'null' with empty
    value = str(value).replace("null", "").strip()
    value = str(value).replace("nan", "").strip()

    # Split by comma
    parts = [p.strip() for p in value.split(",")]

    # Pad or trim to exactly 3 elements
    while len(parts) < 3:
        parts.append("")
    return parts[:3]
# Process rows
# Update the timestamp column based on location match
def apply_offset(row, locode_column, timestamp_column):
    locode = str(row[locode_column]).strip().split(" ")[0]
    offset_str = locode_map.get(locode)

    if pd.isna(row[timestamp_column]):
        original_time = pd.to_datetime(row[timestamp_column])
        return original_time.tz_localize(None)
    else:
        if offset_str is None:
            # print(offset_str)
            missed_locode[locode] = 2
    try:
        # Parse the timestamp
        original_time = pd.to_datetime(row[timestamp_column])

        # Parse offset, assuming format "+HH+MM"
        if offset_str is not None and (offset_str.startswith("+") or offset_str.startswith("-")):
            parts = []
            if offset_str.startswith("+"):
                parts = offset_str[1:].split(":")
            else:
                parts = offset_str[1:].split(":")
            offset_hours = 0
            offset_minutes = 0
            if len(parts) != 2:
                offset_hours = int(parts[0])
            else:
                offset_minutes = int(parts[1])
        else:
            print(offset_str)
            missed_locode[locode] = 1
            original_time = pd.to_datetime(row[timestamp_column])
            return original_time.tz_localize(None)

        # Add offset
        updated_time = original_time + timedelta(hours=offset_hours, minutes=offset_minutes)

        # Return formatted string (same format as original)
        return updated_time.tz_localize(None) #.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        print(f"Error processing row: {e} {row[timestamp_column]}")
        missed_locode[locode] = 1
        return row[timestamp_column].tz_localize(None)
def update_row_in_logward_format(new_row):
    row = new_row.copy()  # Create a copy of the row to avoid modifying the original DataFrame
    row["Carrier Updated Location POL Name"] = row["PORT_OF_LOAD"].split('(')[1].replace(')', '').replace('(',
                                                                                                     '') if pd.notnull(
        row["PORT_OF_LOAD"]) else ""
    row["Carrier Updated Location POD Name"] = row["PORT_OF_DISCHARGE"].split('(')[1].replace(')', '').replace('(',
                                                                                                          '') if pd.notnull(
        row["PORT_OF_DISCHARGE"]) else ""
    row["Depot Pre Location"] = row["GATE_OUT_EMPTY_PLACE"].split('(')[1].replace(')', '').replace('(',
                                                                                                   '') if pd.notnull(
        row["GATE_OUT_EMPTY_PLACE"]) else ""
    row["Depot Pre Country"] = row["GATE_OUT_EMPTY_PLACE"].split('(')[0][:2] if pd.notnull(
        row["GATE_OUT_EMPTY_PLACE"]) and len(row["GATE_OUT_EMPTY_PLACE"].split('(')) > 0 else ""
    row["Depot On Location"] = row["GATE_IN_EMPTY_PLACE"].split('(')[1].replace(')', '').replace('(', '') if pd.notnull(
        row["GATE_IN_EMPTY_PLACE"]) else ""
    row["Depot On Country"] = row["GATE_IN_EMPTY_PLACE"].split('(')[0][:2] if pd.notnull(
        row["GATE_IN_EMPTY_PLACE"]) and len(row["GATE_IN_EMPTY_PLACE"].split('(')) > 0 else ""
    row["TS Port 1 Name"] = row["FIRST_TRANSSHIPMENT_ARRIVE_PLACE"].split('(')[1].replace(')', '').replace('(', '') if pd.notnull(
        row["FIRST_TRANSSHIPMENT_ARRIVE_PLACE"]) else ""
    row["FIRST_TRANSSHIPMENT_LOAD_PLACE_Name"] = row["FIRST_TRANSSHIPMENT_LOAD_PLACE"]
    row["FIRST_TRANSSHIPMENT_DEPART_PLACE_Name"] = row["FIRST_TRANSSHIPMENT_DEPART_PLACE"]
    row['TS Port 2 Name'] = row["LAST_TRANSSHIPMENT_ARRIVE_PLACE"].split('(')[1].replace(')', '').replace('(', '') if pd.notnull(
        row["LAST_TRANSSHIPMENT_ARRIVE_PLACE"]) else ""
    row["LAST_TRANSSHIPMENT_UNLOAD_PLACE_Name"] = row["LAST_TRANSSHIPMENT_UNLOAD_PLACE"]
    row["LAST_TRANSSHIPMENT_LOAD_PLACE_Name"] = row["LAST_TRANSSHIPMENT_LOAD_PLACE"]
    row["LAST_TRANSSHIPMENT_DEPART_PLACE_Name"] = row["LAST_TRANSSHIPMENT_DEPART_PLACE"]
    # row["Destination On Location"] = row["DESTINATION_ARRIVE_PLACE"].split(' ')[1].replace(')', '').replace('(', '')
    # row["Destination On Country"] = row["DESTINATION_ARRIVE_PLACE"].split(' ')[0][:2]
    row["Destination On Location"] = str(row["DESTINATION_ARRIVE_PLACE"]).split('(')[1].replace(')', '').replace(
        '(', '') if pd.notna(row["DESTINATION_ARRIVE_PLACE"]) else ""
    row["Destination On Country"] = str(row["DESTINATION_ARRIVE_PLACE"]).split('(')[0][:2] if pd.notna(
        row["DESTINATION_ARRIVE_PLACE"]) and len(str(row["DESTINATION_ARRIVE_PLACE"]).split('(')) > 1 else ""

    POL_vessel_names = split_with_padding(row["VESSEL_NAME_LIST"])
    row["Vessel 1"] = POL_vessel_names[0] or ""
    row["Vessel 2"] = POL_vessel_names[1] or ""
    row["Vessel 3"] = POL_vessel_names[2] or ""
    # print(row["VESSEL_IMO_LIST"])
    VESSEL_imo_list = split_with_padding(row["VESSEL_IMO_LIST"])
    # Use "" for empty IMO so Excel has empty cells; "" would be parsed as NaN in Node (e.g. parseInt(""))
    row["POL Vessel IMO"] = VESSEL_imo_list[0] or ""
    row["Leg 2 Vessel IMO"] = VESSEL_imo_list[1] or ""
    row["Leg 5 Vessel IMO"] = VESSEL_imo_list[2] or ""
    # row["Pick Up Origin Location"] = row["INLAND_ORIGIN_PLACE"].split(' ')[1].replace(')', '').replace('(', '')
    # row["Pick Up Origin Country"] = row["INLAND_ORIGIN_PLACE"].split(' ')[0][:2]
    inland_origin_place = str(row["INLAND_ORIGIN_PLACE"]) if pd.notna(row["INLAND_ORIGIN_PLACE"]) else ""
    origin_place_parts = inland_origin_place.split('(')

    row["Pick Up Origin Location"] = origin_place_parts[1].replace(')', '').replace('(', '') if len(
        origin_place_parts) > 1 else ""
    row["Pick Up Origin Country"] = origin_place_parts[0][:2] if len(origin_place_parts) > 0 else ""
    # row["Concat (Container +MBL)"] = str(row["CONTAINER_REFERENCE"]) + str(row["BILL_OF_LADING_LIST"])
    row["Concat (Container +MBL)"] = (
            ("" if pd.isna(row["CONTAINER_REFERENCE"]) else str(row["CONTAINER_REFERENCE"])) +
            ("" if pd.isna(row["BILL_OF_LADING_LIST"]) else str(row["BILL_OF_LADING_LIST"]))
    )
    return row


def expand_rows_for_bol(df: pd.DataFrame) -> pd.DataFrame:
    """
    If BILL_OF_LADING_LIST is comma-separated, create one row per B/L value.
    """
    if "BILL_OF_LADING_LIST" not in df.columns:
        return df

    tmp_col = "__bol_list"

    def _to_list(val):
        s = "" if pd.isna(val) else str(val)
        parts = [p.strip() for p in s.split(",")] if "," in s else [s.strip()]
        return [p for p in parts if p] or [""]

    df = df.copy()
    df[tmp_col] = df["BILL_OF_LADING_LIST"].apply(_to_list)
    df = df.explode(tmp_col).reset_index(drop=True)
    df["BILL_OF_LADING_LIST"] = df[tmp_col]
    df.drop(columns=[tmp_col], inplace=True)

    # Rebuild concatenated field now that B/L is per-row
    if "CONTAINER_REFERENCE" in df.columns:
        df["Concat (Container +MBL)"] = (
                ("" if df["CONTAINER_REFERENCE"].isna().all() else df["CONTAINER_REFERENCE"].astype(str).fillna("")) +
                df["BILL_OF_LADING_LIST"].astype(str).fillna("")
        )

    return df

for loc_col, ts_col in keys_map:
    # df[ts_col] = df.apply(lambda row: apply_offset(row, loc_col, ts_col), axis=1)
    df1[ts_col] = df1.apply(lambda row: apply_offset(row, loc_col, ts_col), axis=1)
    df2[ts_col] = df2.apply(lambda row: apply_offset(row, loc_col, ts_col), axis=1)

    print(loc_col, ts_col)
current_time = datetime.now()
print(missed_locode)

# df = df.apply(update_row_in_logward_format, axis=1, result_type='expand')
df1 = df1.apply(update_row_in_logward_format, axis=1, result_type='expand')
df2 = df2.apply(update_row_in_logward_format, axis=1, result_type='expand')

# Duplicate rows for comma-separated BILL_OF_LADING_LIST
df1 = expand_rows_for_bol(df1)
df2 = expand_rows_for_bol(df2)

current_time2 = datetime.now()
print(f"Logward format + B/L expansion done at {(current_time2 - current_time).total_seconds()}s")

# Replace NaN with empty string
df1 = df1.fillna("")
df2 = df2.fillna("")
# write to excel in reverse order
df1 = df1.iloc[::-1].reset_index(drop=True)
df2 = df2.iloc[::-1].reset_index(drop=True)
current_time3 = datetime.now()
print(f"Reset index Done at {(current_time3 - current_time).total_seconds()}s")

# Save back to Excel in chunks of 2000 rows each
CHUNK_SIZE = 2000

def save_df_chunked(df, base_path):
    base_path = base_path.rsplit(".", 1)[0]  # remove .xlsx
    for start in range(0, len(df), CHUNK_SIZE):
        chunk = df.iloc[start : start + CHUNK_SIZE]
        part_num = start // CHUNK_SIZE + 1
        path = f"{base_path}_part{part_num}.xlsx"
        chunk.to_excel(path, index=False)
        print(f"Saved {path} ({len(chunk)} rows)")

save_df_chunked(df1, "~/Downloads/container_completed_ocean-2025-07-14-2026-04-30.xlsx")
save_df_chunked(df2, "~/Downloads/container_not_completed_ocean-2025-07-14-2026-04-30.xlsx")
print(f"Done at {(datetime.now() - current_time).total_seconds()}s")

