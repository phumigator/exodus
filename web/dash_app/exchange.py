"""
Модуль для взаимодействия с MOEX, получения данных об облигациях и расчёта кривой ZCYC.
"""
import requests
import pandas as pd
import numpy as np
import warnings
from datetime import date
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings('ignore')


# ------------------ Вспомогательные функции для MOEX ------------------
def fetch_all_pages(url, params=None, block_name='securities'):
    """
    Загружает все страницы данных с MOEX (пагинация по start).
    """
    if params is None:
        params = {}
    all_data = []
    start = 0
    while True:
        params['start'] = start
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        block = data.get(block_name, {})
        columns = block.get('columns', [])
        rows = block.get('data', [])

        if not rows:
            break

        df_page = pd.DataFrame(rows, columns=columns)
        all_data.append(df_page)

        if len(rows) < 100:
            break
        start += 100

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def find_issuer_by_inn(inn):
    """Поиск идентификатора эмитента по ИНН."""
    url = "https://iss.moex.com/iss/issuers.json"
    params = {'q': inn}
    df = fetch_all_pages(url, params, block_name='issuers')
    if df.empty:
        return None
    return df.iloc[0]['id']


def get_bonds_by_issuer_id(issuer_id):
    """Получение списка облигаций эмитента по его ID."""
    url = f"https://iss.moex.com/iss/issuers/{issuer_id}/securities.json"
    params = {
        'securities.columns': 'secid,isin,regnumber,name,emitent_title,type,is_traded'
    }
    df = fetch_all_pages(url, params, block_name='securities')
    if df.empty:
        return pd.DataFrame()
    df.columns = [col.lower() for col in df.columns]
    mask = df['type'].str.contains('bond', case=False, na=False) & (df['is_traded'] == 1)
    bonds_df = df[mask].copy()
    keep_cols = ['secid', 'isin', 'regnumber', 'name', 'emitent_title', 'type']
    available_cols = [col for col in keep_cols if col in bonds_df.columns]
    bonds_df = bonds_df[available_cols]
    return bonds_df


def search_bonds_by_inn_direct(inn):
    """Прямой поиск облигаций по ИНН (если не удалось найти эмитента)."""
    url = "https://iss.moex.com/iss/securities.json"
    params = {
        'q': inn,
        'securities.columns': 'secid,isin,regnumber,name,emitent_title,type,is_traded'
    }
    df = fetch_all_pages(url, params, block_name='securities')
    if df.empty:
        return pd.DataFrame()
    df.columns = [col.lower() for col in df.columns]
    mask = df['type'].str.contains('bond', case=False, na=False) & (df['is_traded'] == 1)
    bonds_df = df[mask].copy()
    keep_cols = ['secid', 'isin', 'regnumber', 'name', 'emitent_title', 'type']
    available_cols = [col for col in keep_cols if col in bonds_df.columns]
    bonds_df = bonds_df[available_cols]
    return bonds_df


def get_bonds_by_inn(inn):
    """
    Основная функция: ищет облигации по ИНН (сначала через эмитента, затем прямым поиском).
    """
    try:
        issuer_id = find_issuer_by_inn(inn)
        if issuer_id:
            bonds_df = get_bonds_by_issuer_id(issuer_id)
            if not bonds_df.empty:
                return bonds_df
    except Exception as e:
        print(f"Issuer lookup failed: {e}")
    return search_bonds_by_inn_direct(inn)


def fetch_bond_details(secid, isin):
    """
    Загружает детальную информацию по конкретной облигации.
    """
    result = {'secid': secid, 'isin': isin}
    board_id = None

    # 1. Получаем BOARDID
    try:
        url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{isin}.json"
        params = {
            'iss.meta': 'off',
            'iss.only': 'marketdata',
            'marketdata.columns': 'BOARDID'
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            marketdata = data.get('marketdata', {})
            rows = marketdata.get('data', [])
            if rows and len(rows) > 0:
                board_id = rows[0][0]
    except Exception as e:
        print(f"Error fetching BOARDID for {secid}: {e}")

    if not board_id:
        return result

    # 2. Получаем все данные через BOARDID
    try:
        url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/{board_id}/securities/{isin}.json"
        params = {
            'iss.meta': 'off',
            'iss.only': 'securities,marketdata,orderbook,marketdata_yields',
            'securities.columns': 'SHORTNAME,COUPONPERCENT,COUPONVALUE,ACCRUEDINT,FACEVALUE,FACEUNIT,MATDATE,OFFERDATE,NEXTCOUPON,COUPONPERIOD,ISSUESIZE',
            'marketdata.columns': 'LAST,YIELDTOOFFER',
            'orderbook.columns': 'YIELD',
            'marketdata_yields.columns': 'EFFECTIVEYIELD,GSPREADBP,DURATION'
        }
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            securities = data.get('securities', {})
            sec_cols = securities.get('columns', [])
            sec_rows = securities.get('data', [])
            if sec_rows:
                sec_data = dict(zip(sec_cols, sec_rows[0]))
                for key, value in sec_data.items():
                    result[key.lower()] = value

            marketdata = data.get('marketdata', {})
            mkt_cols = marketdata.get('columns', [])
            mkt_rows = marketdata.get('data', [])
            if mkt_rows:
                mkt_data = dict(zip(mkt_cols, mkt_rows[0]))
                for key, value in mkt_data.items():
                    result[key.lower()] = value

            orderbook = data.get('orderbook', {})
            ob_cols = orderbook.get('columns', [])
            ob_rows = orderbook.get('data', [])
            if ob_rows:
                ob_data = dict(zip(ob_cols, ob_rows[0]))
                for key, value in ob_data.items():
                    result[key.lower()] = value

            mkt_yields = data.get('marketdata_yields', {})
            my_cols = mkt_yields.get('columns', [])
            my_rows = mkt_yields.get('data', [])
            if my_rows:
                my_data = dict(zip(my_cols, my_rows[0]))
                for key, value in my_data.items():
                    result[key.lower()] = value
    except Exception as e:
        print(f"Error in comprehensive fetch for {secid}: {e}")

    # Дополнительные вычисляемые поля
    if 'facevalue' in result and 'last' in result:
        try:
            face = float(result['facevalue'])
            last = float(result['last'])
            result['price_rub'] = face * last / 100
        except:
            pass

    if 'matdate' in result:
        try:
            mat_date = pd.to_datetime(result['matdate'])
            today = pd.Timestamp.now().normalize()
            days_to_mat = (mat_date - today).days
            if days_to_mat >= 0:
                result['days_to_maturity'] = days_to_mat
        except:
            pass

    if 'couponperiod' in result:
        try:
            period = float(result['couponperiod'])
            if period > 0:
                freq = 365 / period
                result['coupon_frequency'] = round(freq, 2)
        except:
            pass

    if 'facevalue' in result and 'issuesize' in result:
        try:
            face = float(result['facevalue'])
            size = float(result['issuesize'])
            result['issue_volume'] = face * size
        except:
            pass

    return result


# ------------------ Курсы валют ЦБ РФ ------------------
def get_cbr_rates(date_obj=None):
    """
    Получает курсы валют с сайта ЦБ РФ на указанную дату (по умолчанию сегодня).
    Возвращает словарь {код_валюты: курс_к_рублю}.
    """
    if date_obj is None:
        date_obj = date.today()
    date_str = date_obj.strftime("%d/%m/%Y")
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = 'windows-1251'
        root = ET.fromstring(resp.text)
        rates = {'RUB': 1.0}
        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text
            value = float(valute.find('Value').text.replace(',', '.'))
            nominal = int(valute.find('Nominal').text)
            rates[char_code] = value / nominal
        rates['SUR'] = 1.0
        return rates
    except Exception as e:
        print(f"Ошибка получения курсов ЦБ: {e}")
        # заглушка
        return {'RUB': 1.0, 'SUR': 1.0, 'USD': 90.0, 'EUR': 99.0, 'CNY': 12.5}


def enrich_bonds(bonds_df, rates=None):
    """
    Обогащает DataFrame облигаций всеми доступными полями и добавляет issue_volume_rub.
    """
    if bonds_df.empty:
        return bonds_df

    bond_pairs = list(zip(bonds_df['secid'], bonds_df['isin']))
    enriched_rows = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_secid = {executor.submit(fetch_bond_details, secid, isin): secid for secid, isin in bond_pairs}
        for future in as_completed(future_to_secid):
            secid = future_to_secid[future]
            try:
                details = future.result()
                enriched_rows.append(details)
            except Exception as e:
                print(f"Error processing {secid}: {e}")
                enriched_rows.append({'secid': secid})

    details_df = pd.DataFrame(enriched_rows)
    merged_df = bonds_df.merge(details_df, on='secid', how='left', suffixes=('', '_y'))

    for col in merged_df.columns:
        if col.endswith('_y'):
            merged_df = merged_df.drop(columns=[col])

    desired_cols = [
        'shortname', 'couponpercent', 'couponvalue', 'accruedint', 'facevalue', 'faceunit',
        'matdate', 'offerdate', 'nextcoupon', 'couponperiod', 'last',
        'yieldtoofter', 'yield', 'effectiveyield', 'gspreadbp', 'duration',
        'price_rub', 'days_to_maturity', 'coupon_frequency', 'issue_volume'
    ]
    for col in desired_cols:
        if col not in merged_df.columns:
            merged_df[col] = None

    if rates is None:
        rates = get_cbr_rates()

    def rub_volume(row):
        vol = row.get('issue_volume')
        curr = row.get('faceunit', 'RUB')
        if pd.isna(vol) or vol is None:
            return None
        rate = rates.get(curr, 1.0)
        try:
            return float(vol) * rate
        except:
            return None

    merged_df['issue_volume_rub'] = merged_df.apply(rub_volume, axis=1)

    columns_map = {
        'secid': 'Trade Code',
        'isin': 'ISIN',
        'regnumber': 'Reg Number',
        'name': 'Name',
        'emitent_title': 'Issuer',
        'type': 'Type',
        'shortname': 'Short Name',
        'couponpercent': 'Coupon %',
        'couponvalue': 'Coupon RUB',
        'accruedint': 'Accrued Int',
        'facevalue': 'Face Value',
        'faceunit': 'Currency',
        'matdate': 'Maturity Date',
        'offerdate': 'Offer Date',
        'nextcoupon': 'Next Coupon',
        'couponperiod': 'Coupon Period (days)',
        'last': 'Price %',
        'yieldtoofter': 'Yield to Offer',
        'yield': 'YTM',
        'effectiveyield': 'Effective Yield',
        'gspreadbp': 'G-spread (bp)',
        'duration': 'Duration (years)',
        'price_rub': 'Price RUB',
        'days_to_maturity': 'Days to Maturity',
        'coupon_frequency': 'Coupon Frequency (per year)',
        'issue_volume': 'Issue Volume',
        'issue_volume_rub': 'Issue Volume (RUB)'
    }
    available_cols = [col for col in columns_map if col in merged_df.columns]
    final_df = merged_df[available_cols].rename(columns=columns_map)

    date_cols = ['Maturity Date', 'Offer Date', 'Next Coupon']
    for col in date_cols:
        if col in final_df.columns:
            final_df[col] = pd.to_datetime(final_df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    final_df = final_df.fillna('')
    return final_df


# ------------------ Загрузка данных ZCYC ------------------
def fetch_zcyc_data():
    """Загрузка данных кривой бескупонной доходности с MOEX."""
    try:
        url = "https://iss.moex.com/iss/engines/stock/zcyc/securities.json"
        response = requests.get(url, timeout=10)
        data = response.json()

        columns = data['params']['columns']
        values = data['params']['data']

        if not values:
            return None, "Нет доступных данных"

        df = pd.DataFrame(values, columns=columns)

        required_cols = ['tradedate', 'tradetime', 'B1', 'B2', 'B3', 'T1',
                         'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9']

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f"Отсутствуют столбцы: {missing_cols}"

        df_selected = df[required_cols].copy()

        numeric_cols = ['B1', 'B2', 'B3', 'T1'] + [f'G{i}' for i in range(1, 10)]

        for col in numeric_cols:
            try:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
            except:
                df_selected[col] = 0.0

        df_selected[numeric_cols] = df_selected[numeric_cols].fillna(0)

        return df_selected, None

    except Exception as e:
        return None, str(e)


def calculate_zcyc_curve(params, t_min=0.01, t_max=30, points=1500):
    """
    Расчёт кривой ZCYC по параметрам модели.
    params – словарь с ключами B1, B2, B3, T1, G1..G9.
    """
    try:
        beta0 = float(params.get('B1', 0.0))
        beta1 = float(params.get('B2', 0.0))
        beta2 = float(params.get('B3', 0.0))
        tau = float(params.get('T1', 1.0))

        g_values = []
        for i in range(1, 10):
            g_key = f'G{i}'
            g_val = params.get(g_key, 0.0)
            g_values.append(float(g_val))

        if tau <= 0:
            tau = 1.0

        def GT(t, beta0, beta1, beta2, tau, g_values):
            t_safe = np.maximum(t, 1e-10)
            term1 = beta0 + beta1 * tau * (1 - np.exp(-t_safe / tau)) / t_safe
            term2 = beta2 * ((1 - np.exp(-t_safe / tau)) * tau / t_safe - np.exp(-t_safe / tau))

            # Коэффициенты для Гауссовых членов (фиксированные)
            a_values = np.zeros(9)
            b_values = np.zeros(9)
            a_values[0] = 0
            a_values[1] = 0.6
            b_values[0] = a_values[1]
            k = 1.6
            for i in range(2, 9):
                a_values[i] = a_values[i - 1] + k ** (i - 1)
                b_values[i - 1] = b_values[i - 2] * k

            term3 = 0
            for i in range(9):
                if b_values[i] != 0:
                    term3 += g_values[i] * np.exp(-((t_safe - a_values[i]) ** 2) / (b_values[i] ** 2))

            GT = term1 + term2 + term3
            return GT / 10000

        def KBD(t):
            YT = 100 * (np.exp(GT(t, beta0, beta1, beta2, tau, g_values)) - 1)
            return YT

        t_vals = np.linspace(t_min, t_max, points)
        kbd_vals = KBD(t_vals)

        results_df = pd.DataFrame({
            'Срок (лет)': t_vals,
            'Доходность (%)': kbd_vals,
            'Накопленная доходность': np.cumsum(kbd_vals) / np.arange(1, len(kbd_vals) + 1)
        })

        return results_df, None

    except Exception as e:
        print(f"Ошибка в calculate_zcyc_curve: {e}")
        import traceback
        traceback.print_exc()
        return None, str(e)


# ------------------ Начальные данные ZCYC (на случай ошибки) ------------------
_default_df, _ = fetch_zcyc_data()
if _default_df is None:
    print("Использую тестовые данные для ZCYC")
    _default_df = pd.DataFrame({
        'tradedate': ['2024-01-01'],
        'tradetime': ['10:00:00'],
        'B1': [0.05], 'B2': [-0.02], 'B3': [0.03], 'T1': [1.5],
        'G1': [0.001], 'G2': [-0.002], 'G3': [0.0015],
        'G4': [-0.001], 'G5': [0.0005], 'G6': [-0.0003],
        'G7': [0.0002], 'G8': [-0.0001], 'G9': [0.00005]
    })

default_zcyc_data = _default_df  # для использования в layout и callbacks