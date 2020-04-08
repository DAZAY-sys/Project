import numpy as np
import matplotlib.pyplot as plt

import csv
from ua_parser import user_agent_parser
import IP2Location


def graph(un_device_id, un_log, un_ips, un_ua, mob_dev, anoth_dev):
    s = [len(un_device_id.mn), len(un_log.mn), len(un_ips.mn), len(un_ua.mn)]
    s2 = [un_device_id.count, un_log.count, un_ips.count, un_ua.count]

    x = np.arange(len(s)) - 0.2
    x2 = np.arange(len(s2)) + 0.2

    fig, (ax, ax1) = plt.subplots(nrows=1, ncols=2)

    ax.bar(x, s, width=0.4, align='edge', color='slateblue', label='All devices')
    ax.bar(x2, s2, width=0.4, align='edge', color='lightsteelblue', label='Mobile')
    ax.set_xticks(x)

    ax.set(title='Uniqueness of parameters')
    ax.set_xticklabels(('Uniq_dev', 'Uniq_logs', 'Uniq_ips', 'Uniq_ua', 'Mob_dev', 'Anoth_dev'))
    ax.legend()

    fig.set_figwidth(12)  # ширина Figure
    fig.set_figheight(6)  # высота Figure

    vals = [mob_dev, anoth_dev]
    labels = ["Mob_dev", "Anoth_dev"]
    ax1.set_title('Information about type of the devices')
    expl = (0.06, 0)
    ax1.pie(vals, labels=labels, labeldistance=1.05, startangle=-20, explode=expl, autopct='%1.1f%%',
            colors=['beige', 'darkgrey'])

    plt.show()


class Type:
    def __init__(self):
        self.mn = set()
        self.count = 0

    def change_m(self, line):
        if (line not in self.mn):
            self.mn.add(line)
            return True
        return False

    def change_c(self, mob_or):
        if (mob_or):
            self.count += 1


def csv_make(file_ob):
    i = 0
    mob_dev = 0
    anoth_dev = 0
    un_ips = Type()
    un_log = Type()
    un_ua = Type()
    un_device_id = Type()

    new_str = ''
    os_vers = ''
    reader = csv.reader(file_ob, delimiter=';')
    with open("output.csv", "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ['country; region; city; latitude; longitude; browser; brow_vers; os_family; os_version; device_name'])

        IP2LocObj = IP2Location.IP2Location()
        IP2LocObj.open("IP2LOCATION-LITE-DB5.BIN")

        for line in reader:
            if (i == 0):
                i += 1
                continue

            parsed_string = user_agent_parser.Parse(line[3])
            brow_name = parsed_string['user_agent']['family']
            brow_vers = ''
            if (parsed_string['user_agent']['major'] is not None):
                brow_vers = parsed_string['user_agent']['major']
                if (parsed_string['user_agent']['minor'] is not None):
                    brow_vers += '.' + parsed_string['user_agent']['minor']
                    if (parsed_string['user_agent']['patch'] is not None):
                        brow_vers += '.' + parsed_string['user_agent']['patch']

            os_fam = parsed_string['os']['family']
            if (parsed_string['os']['major'] is not None):
                os_vers = parsed_string['os']['major']

            if parsed_string['device']['brand'] is None:
                device_name = '---'
                mob_or = False
                anoth_dev += 1
            else:
                device_name = parsed_string['device']['family']
                mob_dev += 1
                mob_or = True
                if (parsed_string['device']['brand'] is not None):
                    device_name += " " + parsed_string['device']['brand']

            if (un_ua.change_m(line[3])):
                un_ua.change_c(mob_or)

            if (un_device_id.change_m(line[0])):
                un_device_id.change_c(mob_or)
            if (un_log.change_m(line[1])):
                un_log.change_c(mob_or)

            ip_parts = (line[2])[2:-2].split()
            p = 0
            for l in ip_parts:
                if (un_ips.change_m(l.strip(",'"))):
                    p += 1
                rec = IP2LocObj.get_all(l.strip(",'"))
            for i in range(p):
                un_ips.change_c(mob_or)

            for k in rec.region.split(','): new_str += k + ' '
            writer.writerow([
                rec.country_long + '; ' + new_str + '; ' + rec.city + '; ' + str(rec.latitude) + '; ' + str(
                    rec.longitude) + '; ' + brow_name + '; ' + brow_vers + '; ' + os_fam + '; ' + os_vers + '; ' + device_name])
            i += 1
            new_str = ''

        graph(un_device_id, un_log, un_ips, un_ua, mob_dev, anoth_dev)


if __name__ == '__main__':
    with open('test.csv', 'r') as f_ob:
        csv_make(f_ob)
