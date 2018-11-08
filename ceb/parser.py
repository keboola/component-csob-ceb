'''
Created on 6. 11. 2018

@author: esner
'''
import os
import csv
import hashlib

KEY_HEADER_ROW = 'HLAVA'
KEY_DATA_ROW = 'UC_POLOZKA'

KEY_VYPIS = 'VYPIS'

SEPA_STATS_PK = ['STATS_PK']
SEPA_DATA_PK = ['STATS_ID', 'DATUM_START', 'DATUM_END', 'TYP_TRANSAKCE', 'TRACE_ID']

SEPA_STATS_HEADER = ['CISLO_UCTU',
                     'MENA',
                     'NAZEV_UCTU',
                     'CISLO_VYPISU',
                     'ROK_VYPISU',
                     'DATUM_START',
                     'ZUSTATEK_START',
                     'DATUM_END',
                     'ZUSTATEK_END',
                     'OBRAT_DR',
                     'OBRAT_CR',
                     'UROK_SAZBA_START',
                     'UROK_SAZBA_END',
                     'FREKVENCE',
                     'PK']

SEPA_DATA_ADD_COLS = ['STATS_PK', 'DATUM_START', 'DATUM_END']

SEPA_DATA_HEADER = [
    'TYP_TRANSAKCE',
    'TRACE_ID',
    'REF_KLIENT',
    'REF_BANKA',
    'DATUM_ODUCT',
    'CASTKA_PLATBY',
    'MENA_PLATBY',
    'KURZ',
    'ZUSTATEK',
    'POPIS_POLOZKY',
    'POZNAMKA',
    'POR_CISLO',
    'OPER_KOD',
    'DATUM_SPLAT',
    'DATUM_ZAUCT',
    'ZNAMENKO',
    'CASTKA',
    'MENA',
    'CISLO_SEKU',
    'DOM_ZAHR',
    'KOD_BANKY',
    'SS',
    'VS',
    'KS',
    'CISLO_PROTIUCTU',
    'NAZEV_PROTIUCTU',
    'SS_PLATCE',
    'VS_PLATCE',
    'ZPRAVA_PRIJEMCI1',
    'ZPRAVA_PRIJEMCI2',
    'ZPRAVA_PRIJEMCI3',
    'ZPRAVA_PRIJEMCI4',
    'ADRESA1',
    'ADRESA2',
    'ADRESA3',
    'ADRESA4',
    'ZPRAVA_PLATCI1',
    'ZPRAVA_PLATCI2',
    'ZPRAVA_PLATCI3',
    'ZPRAVA_PLATCI4',
    'KANAL']


class CEB_txt_parser:

    @staticmethod
    def parse(file_path, output_path, type):
        """

        Returns list {'file_path': data_output_file.name,
                         'id': SEPA_DATA_PK,
                         'type': 'data'}
        """
        if type == KEY_VYPIS:
            return CEB_txt_parser.parse_sepa(file_path, output_path)
        else:
            raise ValueError('Unsupported filetype {}'.format(type))

    @staticmethod
    def parse_sepa(file_path, output_path):
        """

        Returns list {'file_path': data_output_file.name,
                         'id': SEPA_DATA_PK,
                         'type': 'data'}
        """

        file_name = os.path.basename(file_path)

        stats_output_path = os.path.join(
            output_path, KEY_VYPIS.lower() + '-stats', file_name + '-stats.csv')
        if not os.path.exists(os.path.dirname(stats_output_path)):
            os.makedirs(os.path.dirname(stats_output_path))

        data_output_path = os.path.join(
            output_path, KEY_VYPIS.lower() + '-data', file_name + '-data.csv')
        if not os.path.exists(os.path.dirname(data_output_path)):
            os.makedirs(os.path.dirname(data_output_path))

        # write stats
        with open(file_path, encoding='windows-1250') as input_file:
            with open(stats_output_path, 'w+', newline='', encoding='utf-8') as stats_out:
                writer = csv.writer(stats_out)
                row = input_file.readline()
                line = row.split('|')
                if (line[0] != KEY_HEADER_ROW):
                    raise ValueError(
                        "First line of file [{}] does not contain header".format(file_name))
                # clean line (remove first(type) and last(extra sep) col
                del line[-1]
                del line[0]
                # write header
                writer.writerow(SEPA_STATS_HEADER)

                # set stat variables
                c_ucet = line[0]
                mena = line[1]
                nr_vypis = line[3]
                date_start = line[5]
                date_end = line[7]
                stats_pk = hashlib.md5('|'.join(
                    [c_ucet, mena, nr_vypis, date_start, date_end]).encode(encoding='utf_8')).hexdigest()
                line += [stats_pk]
                # write data
                writer.writerow(line)

            # write data
            with open(data_output_path, 'w+', newline='', encoding='utf-8') as data_output_file:
                writer = csv.writer(data_output_file)
                line = []
                # write header
                writer.writerow(SEPA_DATA_HEADER + SEPA_DATA_ADD_COLS)

                for row in input_file:
                    values = row.split('|')
                    if(values[0] == KEY_HEADER_ROW):
                        # skip
                        continue
                    if(values[0] == KEY_DATA_ROW):
                        # clean line (remove first(type) and last(extra sep)
                        # col
                        del values[-1]
                        del values[0]

                        # add additional values
                        values = values + [stats_pk, date_start, date_end]
                        writer.writerow(values)
                    else:
                        raise ValueError(
                            'Unsupported type: {}'.format(values[0]))

            stats_res = {'file_path': stats_out.name,
                         'id': SEPA_STATS_PK,
                         'type': KEY_VYPIS.lower() + '-stats'}
            data_res = {'file_path': data_output_file.name,
                        'id': SEPA_DATA_PK,
                        'type': KEY_VYPIS.lower() + '-data'}

            return [stats_res, data_res]
