import requests
from requests.exceptions import RequestException
from collections import defaultdict

def get_location_info(api_key, ip_address, api_url):
    url = f'{api_url}?apiKey={api_key}&ip={ip_address}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        return {'error': {'info': str(e)}}

def process_ip_list(api_keys, api_urls, input_file, output_file, error_log, info_log):
    try:
        with open(input_file, 'r') as file, open(output_file, 'w', encoding='utf-8') as out_file, open(error_log, 'w') as err_log, open(info_log, 'w') as inf_log:
            out_file.write("IP\tCountry\tRegion\tCity\tZip\tLat\tLon\tAccept\n")

            for line in file:
                ip_data = line.strip().split(' ')
                ip_address = ip_data[0]

                locations = defaultdict(list)

                for i, (api_key, api_url) in enumerate(zip(api_keys, api_urls), start=1):
                    location_info = get_location_info(api_key, ip_address, api_url)
                    if isinstance(location_info, dict):
                        lat, lon = location_info.get('latitude', ''), location_info.get('longitude', '')
                        accept_data = f"{i}/3" if 'error' not in location_info else f"0/3"

                        locations[ip_address].append({
                            'country': location_info.get('country', ''),
                            'region': location_info.get('region', ''),
                            'city': location_info.get('city', ''),
                            'zip': location_info.get('zip', ''),
                            'lat': lat,
                            'lon': lon,
                            'accept_data': accept_data
                        })

                        if 'error' in location_info:
                            err_log.write(f"Error for IP {ip_address} (Source {i}): {location_info['error']['info']}\n")

                        inf_log.write(f'По адресу {ip_address} запрос к Source {i} выполнен\n')

                        # Отладочный вывод для второго источника данных
                        if i == 2:
                            print(f"Source {i} response for IP {ip_address}: {location_info}")
                        if i == 1:
                            print(f"Source {i} response for IP {ip_address}: {location_info}")
                        if i == 3:
                            print(f"Source {i} response for IP {ip_address}: {location_info}")

                if locations[ip_address]:
                    # Проверяем совпадения в городах
                    cities = [loc['city'] for loc in locations[ip_address] if loc['city']]
                    num_sources = len(api_urls)
                    num_successful_sources = len(locations[ip_address])

                    if len(set(cities)) == 1:  # Все города совпадают
                        accept_data = f"1/{num_sources}"
                    elif len(set(cities)) == 2:  # Есть два одинаковых города
                        accept_data = f"2/{num_sources}"
                    elif len(set(cities)) == num_sources:  # Все города разные
                        accept_data = f"{num_successful_sources}/{num_sources}"
                    else:  # Некоторые города совпадают
                        accept_data = f"{num_successful_sources - 1}/{num_sources}"

                    # Вывести уникальные ответы и их средние значения
                    for loc in locations[ip_address]:
                        out_file.write(f"{ip_address}\t{loc['country']}\t{loc['region']}\t{loc['city']}\t{loc['zip']}\t{loc['lat']}\t{loc['lon']}\t{accept_data}\n")

    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    api_keys = ["e853e91a2d6a4117b3daff2388504625", "2234FC23420CC70C23DC8D3966E1F9B8", 'https://ipwhois.io/ru/']
    api_urls = ["https://api.ipgeolocation.io/ipgeo", "https://api.ip2location.io/?", 'http://ipwho.is/8.8.4.4']
    input_file = r"C:\Users\rolan\Desktop\ip\ip_w.txt"
    output_file = "output_results.txt"
    error_log = "error.log"
    info_log = "info.log"

    process_ip_list(api_keys, api_urls, input_file, output_file, error_log, info_log)
