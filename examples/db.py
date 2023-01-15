import sqlite3

import numpy as np

if __name__ == '__main__':
    conn = sqlite3.connect('mts.sqlite')
    c = conn.cursor()

    c.execute("SELECT * FROM programs")
    modules = c.fetchall()

    for module in modules:
        test = module[1] + '(' + module[2][-7:-1] + ')'

    c.execute("SELECT "
              "sa.title, "
              "sap.title, "
              "m.title, "
              "m.id, "
              "m.version, "
              "m.ects, "
              "m.exam_type, "
              "group_concat(DISTINCT mp.type) "
              "FROM programs p "
              "JOIN study_areas sa ON sa.program_id = p.id "
              "JOIN modules_study_areas msa ON msa.study_area_id = sa.id "
              "JOIN modules m ON m.id = msa.module_id AND m.version = msa.module_version "
              "LEFT JOIN module_parts mp ON mp.module_id = m.id AND mp.module_version = m.version "
              "JOIN study_areas sap ON sap.id = sa.parent_id "
              "WHERE p.id = ? "
              "GROUP BY m.id, m.version, sa.id "
              "ORDER BY sa.id", (31,))
    all_rows = np.asarray(c.fetchall())
    area = np.array(all_rows)[:, :2]
    area = ': ' + area[:, 0] + '\n[aus ' + area[:, 1] + ']'
    idx = 0
    last = ''
    for i, ar in enumerate(area):
        if last != ar:
            last = ar
            print(i)
            idx += 1
        area[i] = str(idx) + area[i]
    print(area)

    conn.close()
    
